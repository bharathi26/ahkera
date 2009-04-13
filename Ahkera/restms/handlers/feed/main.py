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
from django.shortcuts import render_to_response, get_object_or_404

from restms.handlers.base import BaseHandler
import restms.handlers.join as join 

class feed(BaseHandler):
    """ A RestMS feed. 
    """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # helpers
    type_choices = ( ( "fanout",     "fanout"   ),
                     ( "direct",     "direct"   ),
                     ( "topic",      "topic"    ),
                     ( "headers",    "headers"  ),
                     ( "system",     "system"   ),
                     ( "rotary",     "rotary"   ),
                     ( "service",    "service"  ) )
    # table ----------
    name    = models.CharField( max_length = 100, editable=False )
    type    = models.CharField( max_length = 1, choices = type_choices, editable=False, blank=True )
    title   = models.CharField( max_length = 100, blank = True )
    license = models.CharField( max_length = 100, blank = True )

    # table ----------
    resource_type = "feed"

    def __unicode__(self):
        return """#%s: "%s" (%s)""" % (self.hash, self.name, self.type)

    @models.permalink
    def get_absolute_url(self):
        return ("restms.views.feeder", str(self.hash))

    # Methods:
    #
    # GET - retrieves the feed. (BaseHandler)
    # PUT - updates the feed.  The feed name and type cannot be modified. (BaseHandler) 
    # DELETE - deletes the feed. (and all associated JOINs)
    # POST - sends a message to the feed or stage a content on the feed.

    def POST(self, request):
        """ Sends a message to the feed or stage a content on the feed."""
        # TODO: spread / post message aaccording to feed type
        # route the message to subscribed joins according to the subscription address (pattern)
        #  We might want a separate routing class for this.
        return HttpResponse("POST" + self.__unicode__() + " [" + self.xml + "]")

    def DELETE(self,request):
        """ DELETE a feed and all associated JOINs"""
        try: 
            join.main.join.objects.filter(feed = self.hash).delete()
            self.delete()
        except Exception, e: print e; return HttpResponseServerError()
        return HttpResponse()
