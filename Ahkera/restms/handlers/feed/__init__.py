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

from restms.processor import RestMSXMLProcessor, RestMSProcessorException, ELEMENT_START
from restms.handlers import BaseHandler
from restms.handlers.message import message  

class feed(BaseHandler):
    """ A RestMS feed. 
    """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # table ----------
    name    = models.CharField( max_length = 100, editable=False, unique = True )
    type    = models.CharField( max_length = 100, blank = True )
    title   = models.CharField( max_length = 100, blank = True )
    license = models.CharField( max_length = 100, blank = True )
    domain  = models.ForeignKey('domain')
    # table ----------

    resource_type = "feed"

    def __unicode__(self):
        return """#%s: "%s" (%s)""" % (self.hash, self.name, self.type)

    @models.permalink
    def get_absolute_url(self):
        if self.name:
            return ("restms.views.feeder", [str(self.name)])
        else:
            return ("restms.views.resource", [str(self.hash)])

    # Methods:
    #
    # GET - retrieves the feed. (BaseHandler)
    # PUT - updates the feed.  The feed name and type cannot be modified. (BaseHandler) 
    # DELETE - deletes the feed. (and all associated JOINs)
    # POST - sends a message to the feed or stage a content on the feed.

    GET = lambda self, req: HttpResponse(self.render(req))

    def PUT(self, request):
        p = RestMSXMLProcessor()
        self = self
        p.init({ 
            "feed"  :  { ELEMENT_START : lambda attr, val: None,
                "name"   : self.readonly_attr,
                "type"   : self.readonly_attr,
                "title"  : lambda attr, val: setattr(self, attr, val),
                "license": lambda attr, val: setattr(self, attr, val)}})
        p.process(request.raw_post_data, True)
        self.save(force_update = True)
        return HttpResponse(self.render(request))

    def POST(self, request):
        """ Sends a message to the feed or stage a content on the feed."""
        # TODO: spread / post message according to feed type
        # route the message to subscribed joins according to the subscription address (pattern)
        #  We might want a separate routing class for this.
        raise AttributeError("NOT IMPLEMENTED")

    def DELETE(self,request):
        """ DELETE a feed and all associated JOINs"""
        try: 
            self.join_set.delete()
        except: pass
        self.delete()
        return HttpResponse()

