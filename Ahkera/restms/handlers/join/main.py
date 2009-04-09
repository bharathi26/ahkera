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
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404

class join(models.Model):
    """ A RestMS join. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # table ----------
    hash    = models.AutoField( primary_key = True, editable = False )
    address = models.CharField(max_length=100)
    feed    = models.ForeignKey('feed')
    pipe    = models.ForeignKey('pipe')
    created = models.DateTimeField( auto_now_add = True, editable = False )
    modified= models.DateTimeField( auto_now = True, editable = False )
    # table ----------
    def __unicode__(self):
        return "#%s: feed [%s] ==> pipe [%s]" % (self.hash, self.feed, self.pipe)

    def GET(self):
        """ Retrieves the join representation. This method conforms to the generic model and we do not explain it further. """
        t = loader.get_template("join/get.tmpl")
        c = Context({'join' : self})
        return HttpResponse(t.render(c))

    def DELETE(self):
        """ Deletes the feed. This method conforms to the generic model and we do not explain it further."""
        return "POST " + self.__unicode__()

    def _not_allowed(self):
        """ Not allowed on Join """
        return HttpResponseNotAllowed(['GET', 'DELETE'])

    PUT = _not_allowed
    POST = _not_allowed

