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
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseServerError

from restms.handlers.base import BaseHandler

class content(BaseHandler):
    """ A RestMS staged content."""
    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    message         = models.ForeignKey('message', blank=True)
    feed            = models.ForeignKey('feed')
    content_type    = models.CharField ( max_length=100 )

    # This is the closest thing django has to a blob field.
    #  We should use a document DB like CouchDB for 
    #  staged content eventually.
    payload         = models.TextField() 
    #uri            = models.URLField(verify_exists=False)  # Document DB URI

    resource_type   = "content"

    def _not_allowed(self, request):
        """Return HTTP not allowed w/ list of allowed methods"""
        return HttpResponseNotAllowed(['GET', 'DELETE'])

    PUT = _not_allowed
    POST = _not_allowed

    def GET(self, request):
        return HttpResponse( content_type=self.content_type, content=self.payload  )

