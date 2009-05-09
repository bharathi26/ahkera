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
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from restms.handlers.base import BaseHandler

from ..processor import RestMSXMLProcessor, RestMSProcessorException

import restms.handlers.join as join 

class pipe(BaseHandler):
    """ A RestMS pipe. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # table ----------
    type    = models.CharField( max_length=100, blank =True )
    title   = models.CharField( blank=True, max_length=100 )
    # table ----------

    resource_type = "pipe"
    # Methods:
    #
    # GET - retrieves the pipe representation.
    # DELETE - deletes the pipe.
    # POST - creates a new join for the pipe.

    def __unicode__(self):
        return """#%s: %s (%s)""" % (self.hash, self.title, self.type)

    def GET(self, request):
        """GET a pipe, its associated JOINs and all its messages """
        t = loader.get_template("pipe/get.xml")
        c = Context({ 'pipe'    : self,
                      'joins'   : self.join_set.all(),
                      'messages': self.message_set.all(),
                      'base_url': request.build_absolute_uri('/')})
        return HttpResponse(t.render(c))

    def POST(self, request): 
        """ Create a new JOIN. """
        raise AttributeError("NOT IMPLEMENTED")
        j = self.join_set.create()
        RestMSProcessor().create_resource(request, j, "join")
        return j.GET()

    def DELETE(self,request):
        """ DELETE a pipe and all associated JOINs"""
        try: self.join_set.delete()
        except: pass
        self.delete()
        return HttpResponse()
