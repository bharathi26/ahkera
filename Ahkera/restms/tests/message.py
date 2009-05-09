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

class messageTestCase(TestCase):
    """Test cases for the message handlers"""
    fixtures = ['simple_test.json']

    def testGET(self):
        """Simple message GET test retrieving some messages"""
        expected = [ """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <message
        address="*.*"
        reply_to="me">
        <header name="my_header" value="heyho" />
        <content href="http://testserver/restms/resource/content_2" />
        <content type="text/funny" encoding="ascii" >Das Reh springt hoch, das Reh springt weit, warum auch nicht, es hat ja Zeit.</content>
    </message>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <message
        address="next"
        reply_to="nobody">
        <header name="funny header" value="123" />
        <content type="text/cmd" encoding="ascii" >Do something! NOW!</content>
    </message>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <message
        address="next"
        reply_to="nobody">
        <header name="funny header" value="123" />
        <content type="text/cmd" encoding="ascii" >Do something! NOW!</content>
    </message>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <message
        address="next"
        reply_to="nobody">
        <header name="funny header" value="123" />
        <content type="text/cmd" encoding="ascii" >Do something! NOW!</content>
    </message>
</restms>
""", """<?xml version="1.0"?>
<restms xmlns="http://www.restms.org/schema/restms">
    <message
        address="trallalla"
        reply_to="the pope">
        <header name="one more" value="header value" />
        <content href="http://testserver/restms/resource/content_3" />
    </message>
</restms>
"""]

        for i in range(1,len(expected) + 1):
            r = self.client.get('/restms/resource/message_%s' % (i))
            self.assertEqual(r.status_code, 200)
            self.assertTrue(tools.linediff(r.content, expected[i-1], message="msg #%s" % i))

    def testGETFail(self):
        """Simple message GET fail on nonexisting message"""
        r = self.client.get('/restms/resource/message_99')
        self.assertEqual(r.status_code, 404)

    def testDELETE(self):
        """Complex message DELETE test (checks whether the message is really gone)"""
        client = tools.RESTclient()
        for i in range(2,6):
            r = client.delete('/restms/resource/message_%s' % i)
            self.assertEqual(r.status_code, 200)
            r = client.get('/restms/resource/message_%s' % i)
            self.assertEqual(r.status_code, 404)

    def testPUTFail(self):
        """Simple message PUT fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.put('/restms/resource/message_1',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                            <restms xmlns="http://www.restms.org/schema/restms">
                                <message>
                                    <header name="funny header" value="123" />
                                    <content type="text/cmd" encoding="ascii" >Do something! NOW!</content>
                                </message>
                            </restms>
                       """)
        self.assertEqual(r.status_code, 405)

    def testPOSTFail(self):
        """Simple message POST fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.post('/restms/resource/message_1',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                                <content type="text/plain" encoding="ascii" >Just testing.</content>
                           </restms>
                       """)
        self.assertEqual(r.status_code, 405)

