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

class joinTestCase(TestCase):
    """Test cases for the feed handlers"""
    fixtures = ['simple_test.json']

    def testGET(self):
        expected = ["""<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <join
        address="*"
        feed="http://testserver/restms/feed/commands">
    </join>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <join
        address="server.warn.*"
        feed="http://testserver/restms/feed/Announcements">
    </join>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <join
        address="*"
        feed="http://testserver/restms/feed/commands">
        <header name="test header" value="for a command join" />
    </join>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <join
        address="events.*"
        feed="http://testserver/restms/feed/Announcements">
    </join>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <join
        address="*"
        feed="http://testserver/restms/feed/direct">
        <header name="my very own header" value="for a join" />
        <header name="plus another header" value="for the same join" />
    </join>
</restms>
""" ]
        for i in range(1,len(expected) + 1):
            r = self.client.get('/restms/resource/join_%s' % i)
            self.assertEqual(r.status_code, 200)
            self.assertTrue(tools.linediff(r.content, expected[i-1]))

    def testGETFail(self):
        """Simple join GET fail test on nonexisting join"""
        r = self.client.get('/restms/resource/join_99')
        self.assertEqual(r.status_code, 404)

    def testDELETE(self):
        """Complex join DELETE test (checks whether the join is really gone)"""
        client = tools.RESTclient()
        r = client.delete('/restms/resource/join_1')
        self.assertEqual(r.status_code, 200)
        r = client.get('/restms/resource/join_1')
        self.assertEqual(r.status_code, 404)

    def testPUTFail(self):
        """Simple join PUT fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.put('/restms/resource/join_2',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                              <join address="server.*"
                                feed="http://testserver/restms/feed/Announcements>"
                              </join>
                           </restms>
                       """)
        self.assertEqual(r.status_code, 405)

    def testPOSTFail(self):
        """Simple join POST fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.post('/restms/resource/join_2',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                            <message
                                address="alt.rec.misc"
                                message_id="0815-4711-12345"
                                reply_to="/dev/null" />
                           </restms>
                       """)
        self.assertEqual(r.status_code, 405)

