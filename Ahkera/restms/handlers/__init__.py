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
from django.shortcuts import render_to_response, get_object_or_404

from restms.processor import RestMSProcessorException

import restms.handlers

class BaseHandler(models.Model):
    """Abstract base class for RestMS resources"""

    hash    = models.AutoField( primary_key = True )
    created = models.DateTimeField( auto_now_add = True, editable = False)
    modified= models.DateTimeField( auto_now = True, editable = False)

    # resource_type attribute is to be set by implementing classes
    #  to the RestMS resource typetype
    def _type_get(self):
        raise AttributeError("Abstract")
    resource_type    = property(_type_get)

    class Meta: 
        app_label = 'restms'
        abstract = True

    # helper methods which ease the life of ann implementing class

    @classmethod
    def writeable(cls, attr):
        """Check wheter the field specified by attr is writeable
            Django currently does not expose this but uses an internal "meta"."""
        return cls._meta.get_field(attr).editable

    @models.permalink
    def get_absolute_url(self):
        """Return absolute resource URI (without protocol / domain)"""
        return ("restms.views.resource", [self.resource_type, str(self.hash)])

    def render(self, request):
        """Render response from resource type"""
        t = loader.get_template("".join([self.resource_type, "/get.xml"]))
        c = Context({ self.resource_type : self,
                      'base_url'         : request.build_absolute_uri("") })
        return t.render(c)

    def creat_single(self, element, parent):
        """Create a single resource instance at self._curr.
           Throw an exception if self._curr already eists.
            This method is meant to be used with 
                RestMSProcessor's ELEMENT_START."""
        if parent: 
            raise RestMSProcessorException(
                    "Unsupported child element %s in parent %s " %
                        element, parent)
        try:
            if self._curr:
                raise RestMSProcessorException(
                        "POST of multiple elements not supported")
        except AttributeError:
            pass
        mod = getattr(restms.handlers, element)
        self._curr =  getattr(mod, element)()

    def readonly_attr(self, attr, val):
        """Throw a RestMSProcessorException if the contents of "attr" are
            to be changed. This method is meant to be used for handling
            readonly attributes in RestMSProcessor's element handler."""
        if val != getattr(self, attr):
            raise RestMSProcessorException(
                "\"%s\" attribute cannot be changed." % attr) 

    # default handlers

    def default_DELETE(self,request):
        """ Generic DELETE removing the resource"""
        self.delete()
        return HttpResponse()

