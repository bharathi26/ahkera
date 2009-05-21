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

from django.core.exceptions import ObjectDoesNotExist

from restms import processor
from restms.handlers import BaseHandler
from restms.handlers.join import join 
from restms.handlers.feed import feed 

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

    def _add_header(self, element, parent):
        if parent != "join":
            print parent
            raise RestMSProcessorException("<header> outside of <join>.")
        try:
            self._curr_header.save()
        except AttributeError:
            pass
        self._curr.pipe = self
        self._curr.save() # create join ID
        self._curr_header = self._curr.join_header_set.create()

    def _set_feed(self, attribute, value):
        a = value.split("/")
        try:
            try:
                feed_ident = a.pop()
                uri_type = a.pop()
            except IndexError:
                feed_ident = value
                uri_type   = "feed"
            if uri_type == "feed":
                # named feed
                f = feed.objects.get(name = feed_ident)
            elif uri_type == "resource":
                # anonymous feed
                feed_ident = feed_ident[ len("feed_") : ]
                f = feed.objects.get(hash = int(feed_ident))
            else:
                raise proessor.RestMSProcessorException("Illegal feed URI %s." % value)
        except ObjectDoesNotExist:
            raise proessor.RestMSProcessorException("Feed %s does not exist." % value)
        self._curr.feed = f

    def POST(self, request): 
        """ Create a new JOIN. """
        p = processor.RestMSXMLProcessor()
        p.init({ 
            "join"  :   { processor.ELEMENT_START : self.creat_single,
                "type"    : lambda attr, val: setattr(self._curr, attr, val),
                "address" : lambda attr, val: setattr(self._curr, attr, val),
                "feed"    : self._set_feed },
            "header":   { processor.ELEMENT_START : self._add_header,
                "name"  : lambda attr, val: setattr(self._curr_header, attr, val),
                "value" : lambda attr, val: setattr(self._curr_header, attr, val),
                }})
        try:
            p.process(request.raw_post_data, True)
        except processor.RestMSProcessorException, msg:
            return HttpResponseBadRequest(str(msg))
        try:
            try:
                self._curr_header.save()
            except AttributeError:
                pass
            self._curr.pipe = self
            self._curr.save()
        except Exception, e:
            return HttpResponseBadRequest("Incomplete XML description: %s" % e)

        r = HttpResponse(self._curr.render(request), status = 201)
        r['Location'] = request.build_absolute_uri(self._curr.get_absolute_url())
        return r

    def DELETE(self,request):
        """ DELETE a pipe and all associated JOINs"""
        try: self.join_set.delete()
        except: pass
        self.delete()
        return HttpResponse()
