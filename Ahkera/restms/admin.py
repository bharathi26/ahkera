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

from django.contrib import admin
from restms.models import feed, pipe, join, message, domain
from handlers.message import message_header, message_data
from handlers.message.content import content, content_data
from handlers.join import join_header
from handlers.domain.profile import profile

class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'title', 'hash')

class FeedForJoinInline(admin.TabularInline):
    model = feed
    extra = 1

class JoinInline(admin.TabularInline):
    inlines = [ FeedForJoinInline ]
    model = join
    extra = 1

class JoinHeaderInline(admin.TabularInline):
    model = join_header
    extra = 1

class JoinAdmin(admin.ModelAdmin):
    inlines = [ JoinHeaderInline ]

class MessageHeaderInline(admin.TabularInline):
    model = message_header
    extra = 1

class MessageInline(admin.TabularInline):
    model = message
    extra = 1

class ContentInline(admin.TabularInline):
    model = content
    extra = 5

class ContentDataInline(admin.TabularInline):
    model = content_data
    extra = 1

class PipeAdmin(admin.ModelAdmin):
    inlines = [ JoinInline ]

admin.site.register(feed, FeedAdmin)
admin.site.register(pipe, PipeAdmin)
admin.site.register(join, JoinAdmin)
admin.site.register(join_header)
admin.site.register(message, inlines=[ContentInline])
admin.site.register(message_data, inlines=[MessageHeaderInline, MessageInline])
admin.site.register(message_header)
admin.site.register(content)
admin.site.register(content_data, inlines=[ContentInline])
admin.site.register(domain)
admin.site.register(profile)

