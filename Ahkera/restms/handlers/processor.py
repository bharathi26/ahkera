#   Copyright 2009 Thilo Fromm
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
import xml.parsers.expat
import sys

from .. import handlers


# TODO: JSON implementation

#   The RestMS processors (for both XML and JSON data) 
#     parse incoming data and update or create RestMS resources.
#   Both processors implement the create() and update() functions described 
#   below.
#   A processor for a given request can conveniently be instanciated
#     by the factory method create_processor().
#

class RestMSProcessorException(Exception):
    """ This exception is thrown when the parser encounters an irregularity
        in the input or fails internally. Exception payload is a corresponding
        HttpResponse (BadRequest, NotAllowed). Example handler:
        ----
        try: do_smth()
        except RestMSProcessorException, e: return e.message
        ------
        e.message will hold a descriptive HttpResponse object, so
        the caller might return this to django right away.
        """

def _exc(type, msg):
    raise RestMSProcessorException(
            type(msg, mimetype="text/plain"))


class RestMSXMLProcessor:
    """ Simple RestMS XML parser.
        The parser uses the expat non-validating XML parser to manipulate 
        RestMS resource properties (db fields) while respecting the 
        "editable" flag."""

    def _parser_init(self): 
        """Initialisation called before each processor pass"""
        self.done = False
        self._rest_xml = False
        self._xp = xml.parsers.expat.ParserCreate()
        self._xp.EndElementHandler = self._end_elem

    #
    #  ---  Parser helper functions ---
    #

    def _in_restms_xml(self, key):
        """Check whether we are within a <restms> tag"""
        if key == "restms": 
            if len(self._res_stack) > 0: 
                _exc(HttpResponseBadRequest, 
                        "ERROR: <restms> tag within <restms> tag")
            self._res_stack.append(name)
            return False
        return (len(self._res_stack) > 0)

    def _check_attr(self, res, attr, val, write_check=True):
        try: old_val = getattr(res, attr)
        except: _exc(HttpResponseBadRequest, "".join(
                ["\"", attr,"\" is not a valid property / child resource",
                    " for resource type \"",
                    res.resource_type, "\" \n"]))
        if  (write_check 
             and (val != old_val) 
             and not res.writeable(attr)):
            _exc(HttpResponseForbidden, "".join(
              ["Trying to change read-only attribute \"", key, "\"\n"]))

    #
    #  ---  ExPat callback functions ---
    #

    # start element callback when updating an existing resource

    def _start_elem_update(self, name, attrs):
        """Start element XML parser callback for updating an object.
           The object's properties will be updated according to
           the XML conill be updated according to
           the XML contents. """
        if not self._in_restms_xml(name): return

        # sanity: check incoming resource type
        if name != self._restms_objects[0].resource_type:
            _exc(HttpResponseBadRequest, "".join(
                ["\"",name,"\" resource type encountered while expecting \"",
                    self._restms_objects[0].resource_type, "\" \n"]))

        # update the resource, check attributes
        for key in attrs: 
            self._check_attr(self._restms_objects[0], key, attrs[key])
            setattr(self._restms_objects[0], key, attrs[key])


    # start element callback when creating new resources

    def _start_elem_create(self, name, attrs):
        """Start element XML parser callback for creating an object.
           This method creates a restms resource object from the 
           incoming xml element. The object then is added to the list
           of root resources or, if present, to a parent resource.
           """
        if not self._in_restms_xml(name): return

        # sanity: incoming resource type allowed?
        if not (name in self._allowed_resources):
            _exc(HttpResponseForbidden, "".join(
              ["Creation of resource type \"", name, "\" not allowed here\n"]) )

        # create object, check + set attributes
        res = getattr(handlers, name)()
        for key in attrs: 
            self._check_attr(res, key, attrs[key], write_check=False)
            setattr(self._res, key, attrs[key])

        # add to resources list; attach to parent if present
        if len(self._res_stack) > 1: 
            parent_set = "".join([res.resource_type, "_set"])
            parent_res = self._res_stack[len(self._res_stack)]
            self._check_attr(parent_res, parent_set, write_check=False)
            parent_relation = getattr(parent_res, parent_set)
            parent_relation.add(res)
            self._res_stack.append(res)
        self._restms_objects.append(res)


    def _end_elem(self, name):
        """End element XML parser callback """
        # check whether tag was closed accordingly
        start_tag = self._restms_objects[ len(self._restms_objects) ].resource_type 
        if (name != start_tag): _exc(HttpResponseBadRequest, 
                    "Invalid XML: <", start_tag, "> closed with </", name, ">\n")

        if (name == "restms"):
            self._done = True
        if self._res_stack: self._res_stack.pop()

    #
    #  ---  public access functions  ---
    #

    def create_resource(self, request, allowed_resources):
        """Create RestMS resources from request contents.
            The processor will create an object hierarchy from e.g.
            this XML:
            <message address="abc">
                <header ...>
                <content ...>
            </message>
            "message" is a root resource; "header" and "content"
            are child resources.
            The processor supports creating multiple root resources
            from one chunk of data as well as multi-level child depth.

            @param request the incoming request.

            @return An array of all objects created.

            @throws RestMSProcessorException The exception "text"
                will contain either 
                HttpResponseBadRequest (if invalid XML is detected)
                    or
                HttpResponseForbidden (upon invalid RestMS resource definitions)
        """
        # TODO: limit child resources depth (INI file)
        # TODO: limit number of root resources (INI file)
        self._parser_init()
        self._res_stack = []
        self._resources = []
        self._allowed_resources = allowed_resources
        self._xp.StartElementHandler = self._start_elem_create
        self._xp.Parse(request.raw_post_data)
        if not self._done: _exc( HttpResponseBadRequest,
                            "Invalid XML\n")
        if not self._resources:_exc( HttpResponseBadRequest,
                            "Empty request\n")
        return self._resources


    def update_resource(self, request, resource):
        """Update RestMS resources from request contents.
               Parse incoming request, update the RestMS resource.
                The request contents are parsed and restms_resource properties
                are updated accordingly.

            @param request incoming HTTP request to be parsed
            @param restms_resource RestMS resource object to be updated

            @throws RestMSProcessorException The exception "text"
                will contain either 
                HttpResponseForbidden (if the request tries to update an 
                    invalid or readonly property of the resource)
                or
                HttpResponseBadRequest (if invalix XML was encountered)
        CAVEAT: update_resource does not kwon how to handle child resources.
        """
        self._parser_init()
        self._res_stack = none
        self._resources = [resource, ]
        self._xp.StartElementHandler = self._start_elem_update
        self._xp.Parse(request.raw_post_data)
        if not self._done: _exc( HttpResponseBadRequest,
                            "Invalid XML\n")

def create_processor(request):
    """Simple Factory to return a RestMS processor instance suitable for 
       processing the request.
       """
    # TODO: implementation
    
       





