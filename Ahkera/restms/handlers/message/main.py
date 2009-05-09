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
from django.core.exceptions import ObjectDoesNotExist

from restms.handlers.base import BaseHandler
from restms.handlers.header import base_header

import content

class message_data(BaseHandler):
    """ Message data. This table is for rapid prototyping ONLY.
        Messages / Content will go into a faster store (like CouchDB) soon. """

    address     = models.CharField( max_length = 100, blank = True )
    message_id  = models.CharField( max_length = 100, blank = True )
    reply_to    = models.CharField( max_length = 100, blank = True )

    class Meta: 
        app_label = 'restms'

    def __unicode__(self):
        return """#%s (#%s) - %s => %s""" % (
                self.hash, self.message_id, self.reply_to, self.address)

    def delete_if_not_referenced(self):
        # FIXME: This might be racy.
        try:
            self.message_set.all()
        except ObjectDoesNotExist:
            self.message_header_set.delete()
            super(message_data, self).delete()


class message_header(base_header):
    """Header for messages"""
    class Meta: 
        app_label = 'restms'
    message = models.ForeignKey('message_data')


class message(models.Model):
    """A RestMS message. Can be in multiple pipes, so this is 
       just a reference to the message data itself."""
    hash    = models.AutoField( primary_key = True )
    pipe    = models.ForeignKey('pipe')
    data    = models.ForeignKey('message_data')

    @models.permalink
    def get_absolute_url(self):
        """Return absolute resource URI (without protocol / domain)"""
        return ("restms.views.resource", ['message', str(self.hash)])

    class Meta: 
        app_label = 'restms'

    def __unicode__(self):
        return """#%s (#%s) - %s => %s""" % (
                self.hash, self.data.message_id, self.data.reply_to, self.data.address)

    # Methods:
    # GET - retrieve the message.
    # DELETE - delete the message.

    def GET(self, request):
        """ GET the message, its headers and contents.
            (We currently only support staged content, no
             embedded content)"""
        t = loader.get_template("message/get.xml")
        c = Context({ 'message'     : self.data,
                      'headers'     : self.data.message_header_set.all(),
                      'content_emb' : self.content_set.filter(data__embedded = True),
                      'content_ext' : self.content_set.filter(data__embedded = False),
                      'base_url'    : request.build_absolute_uri('/')})
        return HttpResponse(t.render(c))

    def DELETE(self, request):
        self.delete()
        return HttpResponse()

    def delete(self):
        data = self.data
        super(message, self).delete()
        data.delete_if_not_referenced()

