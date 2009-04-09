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

class feed(models.Model):
    """ A RestMS feed. 
   The XML specification provided by the client when creating a new feed has this format:

    <?xml version="1.0"?>
    <restms xmlns="http://www.imatix.com/schema/restms">
        <feed
         [ type="{feed type}" ]                  default is "topic"
         [ title="{short title}" ]               optional title
         [ license="{license name}" ]            optional license name
         />
    </restms>

    """

    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # helpers
    type_choices = ( ( "fanout",     "fanout"   ),
                     ( "direct",     "direct"   ),
                     ( "topic",      "topic"    ),
                     ( "headers",    "headers"  ),
                     ( "system",     "system"   ),
                     ( "rotary",     "rotary"   ),
                     ( "service",    "service"  ) )
    # table ----------
    hash    = models.AutoField( primary_key = True )
    name    = models.CharField( max_length = 100 )
    type    = models.CharField( max_length = 1, choices = type_choices)
    title   = models.CharField( max_length = 100 )
    license = models.CharField( max_length = 100 )
    created = models.DateTimeField( auto_now_add = True )
    modified= models.DateTimeField( auto_now = True )
    # table ----------

    def __unicode__(self):
        return """#%s: "%s" (%s)""" % (self.hash, self.name, self.type)

    def GET(self):
        """ Retrieves the feed. This method conforms to the generic model and we do not explain it further. """
        t = loader.get_template("feed/get.tmpl")
        c = Context({'feed' : self})
        return HttpResponse(t.render(c))

    def PUT(self):
        """ Updates the feed. This method conforms to the generic model. The feed name and type cannot be modified. """
        return "PUT" + self.__unicode__()

    def DELETE(self):
        """ Deletes the feed. This method conforms to the generic model and we do not explain it further."""
        return "POST " + self.__unicode__()

    def POST(self):
        """ Sends a message to the feed or stage a content on the feed. We explain these in the description of messages """
        return "DELETE " + self.__unicode__()

