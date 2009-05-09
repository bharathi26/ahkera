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
from django.http import HttpResponse

from restms.handlers.base import BaseHandler
from restms.handlers.header import base_header

class join_header(base_header):
    """Header used in JOINs"""
    class Meta: 
        app_label = 'restms'
    join = models.ForeignKey('join')

class join(BaseHandler):
    """ A RestMS join. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # table ----------
    address = models.CharField(max_length=100)
    type    = models.CharField(max_length=100, editable=False, blank=True )
    feed    = models.ForeignKey('feed')
    pipe    = models.ForeignKey('pipe')
    # table ----------

    resource_type = "join"

    # Methods:
    #
    # GET - retrieves the join representation.
    # DELETE - deletes the join.

    def __unicode__(self):
        return "#%s: feed [%s] ==> pipe [%s]" % (self.hash, self.feed, self.pipe)

    DELETE = lambda self, request: self.default_DELETE(request)

    def GET(self, request):
        """ JOIN getter """
        t = loader.get_template("join/get.xml")
        c = Context({'join'     : self,
                     'feed'     : self.feed,
                     'headers'  : self.join_header_set.all(),
                     'base_url' : request.build_absolute_uri('/')})
        return HttpResponse(t.render(c))

