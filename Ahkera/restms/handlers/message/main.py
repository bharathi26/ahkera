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

class message(models.Model):
    """ A RestMS Message. This table is for rapid prototyping ONLY.
        Messages will go into a faster store (like CouchDB) soon. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    hash            = models.AutoField( primary_key = True, editable = False )
    address         = models.CharField( max_length = 100 )
    delivery_mode   = models.CharField( max_length = 100 )
    priority        = models.SmallIntegerField() # 0-9
    correlation_id  = models.CharField( max_length = 100 )
    reply_to        = models.CharField( max_length = 100 )
    expiration      = models.DateTimeField()
    message_id      = models.CharField( max_length = 100 )
    timestamp       = models.DateTimeField()
    type            = models.CharField( max_length = 100 )
    user_id         = models.CharField( max_length = 100 )
    app_id          = models.CharField( max_length = 100 )
    sender_id       = models.CharField( max_length = 100 )
    header_name     = models.TextField()
    header_value    = models.TextField()

    created         = models.DateTimeField( auto_now_add = True, editable = False )
    modified        = models.DateTimeField( auto_now = True, editable = False )

