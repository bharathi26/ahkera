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

from restms.handlers.processor import RestMSProcessor, RestMSProcessorException

import restms.handlers.join as join 

class pipe(BaseHandler):
    """ A RestMS pipe. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    type_choices = ( ( "fifo",     "fifo"     ),
                     ( "stream",   "stream"   ),
                     ( "ondemand", "ondemand" ),
                     ( "push",     "push"     ) )
    # table ----------
    type    = models.CharField( max_length=1, choices=type_choices, blank=True )
    messages= models.ManyToManyField('message', blank=True)
    title   = models.CharField( blank=True, max_length="100" )
    # table ----------
    resource_type="pipe"

    # Methods:
    #
    # GET - retrieves the pipe representation.
    # DELETE - deletes the pipe.
    # POST - creates a new join for the pipe.

    def __unicode__(self):
        return """#%s: %s""" % (self.hash, self.type)

    def GET(self, request):
        """GET a pipe, its associated JOINs and all its messages """
        try:
            t = loader.get_template("pipe/get.xml")
            c = Context({ 'pipe'    : self,
                          'joins'   : join.main.join.objects.filter(pipe = self.hash),
                          'messages': self.messages.all(),
                          'base_url': request.build_absolute_uri('/')})
        except Exception, e: return HttpResponseServerError()
        return HttpResponse(t.render(c))

    def POST(self, request): 
        """ Create a new JOIN. """
        j = join.main.join(pipe = self.hash)
        RestMSProcessor().parse(request, j, check_readonly = False)
        j.save()
        return j.GET()

    def DELETE(self,request):
        """ DELETE a pipe and all associated JOINs"""
        try: 
            join.main.join.objects.filter(pipe= self.hash).delete()
            self.delete()
        except Exception, e: print e; return HttpResponseServerError()
        return HttpResponse()

    def PUT (self, request):
        """PUT not allowed on pipes."""
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE'])
