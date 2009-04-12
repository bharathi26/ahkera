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
from django.http import HttpResponse, HttpResponseNotFound
import restms.models as handlers

def resource(request, type, hash):
    # find the corresponding resource object
    handler = getattr(handlers, type)
    try: res = handler.objects.get(hash=hash)
    except: return HttpResponseNotFound()
    return getattr(res, request.method)(request)

def feeder(request, name=None):
    try: res = handlers.feed.objects.get(name=name)
    except: return HttpResponseNotFound()
    return getattr(res, request.method)(request)

def domain(request, name = None):
    return HttpResponse("Domain handler for hash %s" % (hash,) )
