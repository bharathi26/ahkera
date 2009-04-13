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
from django.db import models
from django.template import Context, loader
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseServerError

from restms.handlers.base import BaseHandler

import content, header

class message(BaseHandler):
    """ A RestMS Message. This table is for rapid prototyping ONLY.
        Messages will go into a faster store (like CouchDB) soon. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    address = models.CharField( max_length = 100, blank = True )
    id      = models.CharField( max_length = 100, blank = True )
    reply_to= models.CharField( max_length = 100, blank = True )

    resource_type = "message"

    # Methods:
    #
    # GET - retrieve the message.
    # DELETE - delete the message.

    def _not_allowed(self, request):
        """Return HTTP not allowed w/ list of allowed methods"""
        return HttpResponseNotAllowed(['GET', 'DELETE'])

    def GET(self, request):
        """ GET the message, its headers and contents.
            (We currently only support staged content, no
             embedded content)"""
        try:
            t = loader.get_template("message/get.xml")
            c = Context({ 'message' : self,
                          'headers' : msg_header.objects.filter(message=self.hash),
                          'content' : content.objects.filter(message=self.hash),
                          'base_url' : request.build_absolute_uri('/')})
        except Exception, e: return HttpResponseServerError(str(e) + "\n")
        return HttpResponse(t.render(c))

    def DELETE(self,request):
        """ DELETE a message and all associated content and headers"""
        try: 
            c = content.objects.filter(message = self.hash);
            if c: c.delete()
            h = msg_header.objects.filter(message = self.hash);
            if h: h.delete()
            self.delete()
        except Exception, e: print e; return HttpResponseServerError()
        return HttpResponse()

    PUT = _not_allowed
    POST = _not_allowed
