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

from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseServerError
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

    def _read_some(self, chunk=1024):
        # FIXME !!! HACK ALERT !!!: find a better way to access raw 
        #  HTTP input streams. This os only tested on the django development
        #  web server.
        # FIXME If a payload is appended after a RestMS XML envelope we will
        #  lose paload data when reading too much here. Maybe implementing
        #  an Expat text_data callback which puts this trailing data into a
        #  temporary Buffer would help.
        """Read some bytes of input."""
        try: return self._in_stream.read(chunk)
        except AttributeError:
            if self._req.environ['wsgi.input']: 
                self._in_stream = self._req.environ['wsgi.input']
            elif self._req._req: self._in_stream = self._req._req
            else: _exc(HttpResponseServerError, "No input stream\n")
        return self._in_stream.read(chunk)

    class xml_mapper():
        def __init__(self, res):
            """XML to restms object mapper"""
            self.done = False; self._tag_done = False; self._rest_xml = False
            self._res = res
            self._xp = xml.parsers.expat.ParserCreate()
            self._xp.StartElementHandler = self._start_elem
            self._xp.EndElementHandler = self._end_elem

        def _start_elem(self, name, attrs):
            """Start element XML parser callback (e.g. <elem>) """
            if name == "restms": self._rest_xml = True; return
            if not self._rest_xml or (name != self._res.resource_type): return
            for key in attrs: 
                old_val = getattr(self._res, key)
                if (attrs[key] != old_val) and not self._res.writeable(key):
                    _exc(HttpResponseBadRequest, "".join(
                      ["Trying to change read-only attribute \"", key, "\"\n"]))
                setattr(self._res, key, attrs[key])

        def _end_elem(self, name):
            """End element XML parser callback (e.g. </elem>)"""
            if name == self._res.resource_type: self._tag_done = True
            if name == "restms": 
                if self._tag_done: self.done = True
                self._rest_xml = False; 

        def parse_chunk(self, chunk): self._xp.Parse(chunk)

    def parse(self, request, restms_resource):
        """Main parser worker function. The request contents are parsed 
           and restms_resource properties are updated accordingly.
           @throws RestMSProcessorException
           """
        try: 
           len = int(request.META['CONTENT_LENGTH'])
           if len < 1: raise Exception()
        except: _exc( HttpResponseBadRequest,
                "Content Length header field invalid\n")
        self._req = request;
        xp = RestMSProcessor.xml_mapper(restms_resource)
        while (not xp.done) and (len > 0): 
            chunksize = min(1024, len)
            xp.parse_chunk(self._read_some(chunksize))
            len -= chunksize
        if not xp.done: _exc( HttpResponseBadRequest,
                            "Invalid XML description\n")

