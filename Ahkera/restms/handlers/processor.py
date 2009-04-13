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


# ============== Refactoring notes ====================
# TODO: RestMSProcessor should be an abstract base class 
#  to be implemented by RestMSProcessorXML and RestMSProcessorJSON
# A Factory could provide a suitable processor depending on a request's
#  Content-Type.

from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
import xml.parsers.expat
import sys

class RestMSProcessorException(Exception):
    """ This exception is thrown when the parser encounters an irregularity
        in the input or fails internally. Exception payload is a corresponding
        HttpResponse (BadRequest, NotAllowed, ServerError). Example handler:
        try: do_smth()
        except RestMSProcessorException, e: return e.message
        e.message will hold a descriptive HttpResponse object.
        """

def _exc(type, msg):
    raise RestMSProcessorException(
            type(msg, mimetype="text/plain"))

class RestMSProcessor:
    """ Simple RestMS XML parser.
        The parser uses the expat non-validating XML parser to manipulate 
        RestMS resource properties (db fields) while respecting the 
        "editable" flag."""

    class xml_mapper():
        """XML to restms object mapper"""
        def __init__(self, res, check_rdonly):
            self.done = False; self._tag_done = False; self._rest_xml = False
            self._res = res; self._check_rdonly = check_rdonly
            self._xp = xml.parsers.expat.ParserCreate()
            self._xp.StartElementHandler = self._start_elem
            self._xp.EndElementHandler = self._end_elem

        def _check_field_access(self, key, val):
            try: old_val = getattr(self._res, key)
            except: _exc(HttpResponseBadRequest, "".join(
                    ["\"",key,"\" is not a valid property for resource type ",
                        self._res.resource_type, " \n"]))
            if (self._check_rdonly):
                if (val != old_val) and not self._res.writeable(key):
                    _exc(HttpResponseForbidden, "".join(
                      ["Trying to change read-only attribute \"", key, "\"\n"]))

        def _start_elem(self, name, attrs):
            """Start element XML parser callback (e.g. <elem>) """
            if name == "restms": self._rest_xml = True; return
            if not self._rest_xml or (name != self._res.resource_type): return
            for key in attrs: 
                self._check_field_access(key, attrs[key])
                setattr(self._res, key, attrs[key])

        def _end_elem(self, name):
            """End element XML parser callback (e.g. </elem>)"""
            if name == self._res.resource_type: self._tag_done = True
            if name == "restms": 
                if self._tag_done: self.done = True
                self._rest_xml = False; 

        def parse_chunk(self, chunk): self._xp.Parse(chunk)

# FIXME: this should be "process()"
    def parse(self, request, restms_resource, check_readonly=True):
        """Main parser worker function. The request contents are parsed 
           and restms_resource properties are updated accordingly.
           @throws RestMSProcessorException
           @param request incoming HTTP request to be parsed
           @param restms_resource RestMS resource object to be updated
           @param check_readonly=True Check for 'editable' property before
                    updating fields (creating vs. updating objects).
                    Write attempts to readonly fields will trigger
                    a FORBIDDEN exception.
           """
        try: 
           len = int(request.META['CONTENT_LENGTH'])
           if len < 1: raise Exception()
        except: _exc( HttpResponseBadRequest,
                "Content Length header field invalid\n")
        xp = RestMSProcessor.xml_mapper(restms_resource, check_readonly)
        xp.parse_chunk(request.raw_post_data)
        if not xp.done: _exc( HttpResponseBadRequest,
                            "Invalid XML description\n")

