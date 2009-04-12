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

class pipe(models.Model):
    """ A RestMS pipe. """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    pipe_choices = ( ( "fifo",     "fifo"     ),
                     ( "stream",   "stream"   ),
                     ( "ondemand", "ondemand" ),
                     ( "push",     "push"     ) )
    # table ----------
    hash    = models.AutoField( primary_key = True, editable = False )
    type    = models.CharField( max_length = 1, choices = pipe_choices )
    created = models.DateTimeField( auto_now_add = True, editable = False )
    modified= models.DateTimeField( auto_now = True, editable = False )
    # table ----------
    resource_type="pipe"

    def __unicode__(self):
        return """#%s: %s""" % (self.hash, self.type)
