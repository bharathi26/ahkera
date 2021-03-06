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

class pipeTestCase(TestCase):
    """Test cases for the feed handlers"""
    fixtures = ['simple_test.json']

    def testGET(self):
        """Simple pipe GET test retrieving some pipes"""
        expected = ["""<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <pipe
        type=""
        title="server #1 inbox" >
        <join href="http://testserver/restms/resource/join_1"
            type=""
            address="*"
            feed="http://testserver/restms/feed/commands" />
        <join href="http://testserver/restms/resource/join_2"
            type=""
            address="server.warn.*"
            feed="http://testserver/restms/feed/Announcements" />
        <message href="http://testserver/restms/resource/message_1"
            address="*.*"
            message_id="0815" />
        <message href="http://testserver/restms/resource/message_2"
            address="next"
            message_id="4711" />
    </pipe>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <pipe
        type=""
        title="server #2 inbox" >
        <join href="http://testserver/restms/resource/join_3"
            type=""
            address="*"
            feed="http://testserver/restms/feed/commands" />
        <message href="http://testserver/restms/resource/message_3"
            address="next"
            message_id="4711" />
    </pipe>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <pipe
        type="direct"
        title="My Mailbox" >
        <join href="http://testserver/restms/resource/join_4"
            type=""
            address="events.*"
            feed="http://testserver/restms/feed/Announcements" />
        <join href="http://testserver/restms/resource/join_5"
            type=""
            address="*"
            feed="http://testserver/restms/feed/direct" />
        <message href="http://testserver/restms/resource/message_4"
            address="next"
            message_id="4711" />
        <message href="http://testserver/restms/resource/message_5"
            address="trallalla"
            message_id="12345" />
    </pipe>
</restms>
"""]
        for i in range(1, len(expected) + 1):
            r = self.client.get('/restms/resource/pipe_%s' % i)
            self.assertEqual(r.status_code, 200)
            self.assertTrue(tools.linediff(r.content, expected[i-1]))


    def testGETFail(self):
        """Simple pipe GET fail test retrieving a nonexisting pipe"""
        r = self.client.get('/restms/resource/pipe_99')
        self.assertEqual(r.status_code, 404)


    def testPUTFail(self):
        """Simple pipe PUT fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.put('/restms/resource/pipe_1', content_type="restms+xml",
                            data = """ <?xml version="1.0"?>
                                       <restms xmlns="http://www.restms.org/schema/restms">
                                            <pipe type="" title="fail test" />
                                        </restms>
                                    """)
        self.assertEqual(r.status_code, 405)


    def testDELETE(self):
        """Complex pipe DELETE test (checks whether the pipe is really gone)"""
        client = tools.RESTclient()
        r = client.delete('/restms/resource/pipe_1')
        self.assertEqual(r.status_code, 200)
        r = client.get('/restms/resource/pipe_1')
        self.assertEqual(r.status_code, 404)

    def testPOST(self):
        """Complex pipe POST test"""
        data = """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <join
        address="alt.rec.misc"
        feed="http://testserver/restms/feed/Announcements">
        <header name="some test header" value="qwertz" />
        <header name="more test header" value="brfff" />
    </join>
</restms>
"""
        r = self.client.post('/restms/resource/pipe_1', content_type="restms+xml",
            data = data)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(tools.linediff(r.content, data))

        join_loc = r["Location"].split("/")[-1]
        r = self.client.get('/restms/resource/%s' % join_loc)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(tools.linediff(r.content, data))

