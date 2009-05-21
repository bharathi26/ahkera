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
import tools
from django.test import TestCase

class feedTestCase(TestCase):
    """Test cases for the feed handlers"""
    fixtures = ['simple_test.json']

    def testGET(self):
        """Simple feed GET test retrieving some feeds"""
        expected = {
            'Announcements' : """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <feed
        name="Announcements"
        type=""
        title="Announcement channel."
        license="None"
    />
</restms>
""",
            'commands'      : """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <feed
        name="commands"
        type="fifo"
        title="Command processing queue"
        license="GPL"
    />
</restms>
""",
            'direct'        : """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <feed
        name="direct"
        type="direct"
        title="Direct feed"
        license="proprietary"
    />
</restms>
"""}
        for feed in expected:
            r = self.client.get('/restms/feed/%s' % feed)
            self.assertEqual(r.status_code, 200)
            self.assertTrue(tools.linediff(r.content, expected[feed]))

    def testGETFail(self):
        """Simple feed GET fail test retrieving a nonexisting feed"""
        r = self.client.get('/restms/feed/fail')
        self.assertEqual(r.status_code, 404)

    def testPUT(self):
        """Complex feed PUT test (modifies, then retrieves and checks a feed)"""
        client = tools.RESTclient()

        r = client.put('/restms/feed/Announcements', content_type="restms+xml",
                data = """<?xml version="1.0"?>
                 <restms xmlns="http://www.restms.org/schema/restms">
                        <feed
                            name="Announcements"
                            type=""
                            title="Announcement channel - test modification."
                            license="BSD"
                        />
                 </restms>
                     """)
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/restms/feed/Announcements')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(tools.linediff(r.content, """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <feed
        name="Announcements"
        type=""
        title="Announcement channel - test modification."
        license="BSD"
    />
</restms>
"""))

    def testPOST(self):
        """Simple feed POST test (does not check for message arrival)"""
        # TODO: content staging

        r = self.client.post('/restms/feed/Announcements', content_type="restms+xml",
        data = """<?xml version="1.0"?>
             <restms xmlns="http://www.restms.org/schema/restms">
                    <message
                        address="alt.rec.misc"
                        message_id="0815-4711-12345"
                        reply_to="/dev/null" >
                        <header name="some test header" value="qwertz">
                        <header name="more test header" value="brfff">
                        <content type="text/beverage" encoding="ascii">
                            Free beer!
                        </content>
                    </ message>
             </restms>
             """)
        self.assertEqual(r.status_code, 200)

    def testDELETE(self):
        """Complex feed DELETE test (checks whether the feed is really gone)"""
        client = tools.RESTclient()
        r = client.delete('/restms/feed/commands')
        self.assertEqual(r.status_code, 200)
        r = client.get('/restms/feed/commands')
        self.assertEqual(r.status_code, 404)

