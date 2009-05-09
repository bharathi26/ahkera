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

from restms.handlers.base import BaseHandler
import restms.handlers.feed as feed
import restms.handlers.pipe as pipe
from profile import profile

class domain(BaseHandler):
    """ A RestMS domain. 
    """
    # clutch to make django object-relational magic work
    class Meta: app_label = 'restms'

    # table ----------
    name    = models.CharField( max_length = 100, unique=True )
    title   = models.CharField( max_length = 100, blank = True )
    # table ----------

    resource_type = "domain"

    def __unicode__(self):
        return """#%s - %s: %s""" % (self.hash, self.name, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ("restms.views.domain", str(self.name))

    # Methods:
    #
    # GET - retrieves Domain represenation (domain, profiles, feeds)
    # POST - create new feed or pipe

    def GET(self, request):
        """GET a domain, its associated public (i.e. named) FEEDs and profiles 
        """
        t = loader.get_template("domain/get.xml")
        c = Context({ 'domain'    : self,
                      'feeds'     : self.feed_set.all(),
                      'profiles'  : self.profile_set.all(),
                      'base_url'  : request.build_absolute_uri('/')})
        return HttpResponse(t.render(c))

    def POST(self, request):
        """Create new feed or pipe. Needs processor.py refactored and extended.
        """
        raise AttributeError("NOT IMPLEMENTED")

