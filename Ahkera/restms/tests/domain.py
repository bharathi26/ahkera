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

from django.test import TestCase
import tools

class domainTestCase(TestCase):
    """Test cases for the feed handlers"""
    fixtures = ['simple_test.json']

    def testGET(self):
        """Simple domain GET test retrieving a domain"""
        expected = """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <domain title="The Serenity domain">
        <profile
            name="defaults"
            title="The defaults profile"
            href="http://www.restms.org/3:Defaults" />
        <feed
            name="Announcements"
            title="Announcement channel."
            type=""
            license="None"
            href="http://testserver/restms/feed/Announcements" />
        <feed
            name="commands"
            title="Command processing queue"
            type="fifo"
            license="GPL"
            href="http://testserver/restms/feed/commands" />
        <feed
            name="direct"
            title="Direct feed"
            type="direct"
            license="proprietary"
            href="http://testserver/restms/feed/direct" />
    </domain>
</restms>
"""
        r = self.client.get('/restms/domain/Serenity')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(tools.linediff(r.content, expected))

    def testGETFail(self):
        """Simple domain GET fail test retrieving a nonexisting domain"""
        r = self.client.get('/restms/domain/fail')
        self.assertEqual(r.status_code, 404)

    def testDELETEFail(self):
        """Simple domain DELETE fail test (not allowed for domains)"""
        client = tools.RESTclient()
        r = client.delete('/restms/domain/Serenity')
        self.assertEqual(r.status_code, 405)

    def testPUTFail(self):
        """Simple domain PUT fail test (not allowed for domains)"""
        client = tools.RESTclient()
        r = client.put('/restms/domain/Serenity',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                              <domain title="DOMAIN PUT FAIL TEST">
                              </domain>
                           </restms>
                       """)
        self.assertEqual(r.status_code, 405)

    def testPOSTFeed(self):
        """Simple domain POST test creating a test runner feed (without check)"""
        r = self.client.post('/restms/domain/Serenity',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                              <feed name="Test Runner Feed"
                                title="The Test Runner Feed"
                                license="BSD" />
                           </restms>
                        """ )
        self.assertEqual(r.status_code, 201)

    def testPOSTPipe(self):
        """Simple domain POST test creating a test runner pipe"""
        r = self.client.post('/restms/domain/Serenity',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                              <pipe title="The Test Runner Pipe" />
                           </restms>
                        """ )
        self.assertEqual(r.status_code, 201)

