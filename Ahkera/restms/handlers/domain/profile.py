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

class profile(models.Model):
    """ A RestMS domain profile """
    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # table ----------
    name    = models.CharField( max_length = 100 )
    title   = models.CharField( max_length = 100, blank = True )
    href    = models.URLField( verify_exists = False )
    domain  = models.ForeignKey('domain')
    # table ----------
    
    resource_type = "profile"

    def __unicode__(self):
        return """%s: %s""" % (self.name, self.title)

