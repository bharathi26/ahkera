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

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest
from restms.handlers import BaseHandler

class content_data(BaseHandler):
    """RestMS message content data. This table is for 
        rapid prototyping ONLY.
        Content will go into a faster store (like CouchDB) soon. """

    type        = models.CharField( max_length = 100, blank = True )
    encoding    = models.CharField( max_length = 100, blank = True )
    embedded    = models.BooleanField()
    value       = models.TextField()

    class Meta: 
        app_label = 'restms'

    def __unicode__(self):
        return """#%s: %s,%s (embd: %s, len %s)""" % (
                self.hash, self.type, self.encoding, str(self.embedded), len(self.value))

    def delete_if_not_referenced(self):
        # FIXME: This might be racy.
        try:
            self.content_set.all()
        except ObjectDoesNotExist:
            super(content_data, self).delete()


class content(models.Model):
    """A RestMS message content. As messages, contents can be in multiple
       pipes, but always belong to the same message in these pipes."""
    hash        = models.AutoField( primary_key = True )
    message     = models.ForeignKey('message')
    data        = models.ForeignKey('content_data')

    resource_type = "content"

    @models.permalink
    def get_absolute_url(self):
        """Return absolute resource URI (without protocol / domain)"""
        return ("restms.views.resource", ['content', str(self.hash)])

    class Meta: 
        app_label = 'restms'

    def __unicode__(self):
        return """#%s: %s,%s (embd: %s, len %s)""" % (
                self.hash, self.data.type, self.data.encoding, 
                str(self.data.embedded), len(self.data.value))

    # Methods:
    # GET - retrieve the content.
    # DELETE - delete the content.

    def GET(self, request):
        if self.data.embedded:
            return HttpResponseBadRequest()
        return HttpResponse( self.data.value, 
                             content_type = self.data.type)

    def DELETE(self, request):
        if self.data.embedded:
            return HttpResponseBadRequest()
        self.delete()
        return HttpResponse()

    def delete(self):
        data = self.data
        super(content, self).delete()
        data.delete_if_not_referenced()

