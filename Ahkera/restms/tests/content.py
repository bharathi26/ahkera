
import tools
from django.test import TestCase

class contentTestCase(TestCase):
    """Test cases for the content handlers"""
    fixtures = ['simple_test.json']

    def testGET(self):
        """Simple content GET test retrieving non-embedded content"""
        expected = """The wise programmer is told about Tao
And follows it.
The average programmer is told about Tao
And searches for it.
The foolish programmer is told about Tao
And laughs at it.

If it were not for laughter, there would be no Tao.
"""
        r = self.client.get('/restms/resource/content_2')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(tools.linediff(r.content, expected))

    def testGETFail(self):
        """Simple content GET fail on nonexisting and on embedded content"""
        r = self.client.get('/restms/resource/content_99')
        self.assertEqual(r.status_code, 404)
        r = self.client.get('/restms/resource/content_1')
        self.assertEqual(r.status_code, 400)

    def testDELETE(self):
        """Complex content DELETE test (checks whether the content is really gone)"""
        client = tools.RESTclient()
        r = client.delete('/restms/resource/content_2')
        self.assertEqual(r.status_code, 200)
        r = client.get('/restms/resource/content_2')
        self.assertEqual(r.status_code, 404)

    def testDELETEFail(self):
        """Simple content DELETE fail test on embedded content"""
        client = tools.RESTclient()
        r = client.delete('/restms/resource/content_1')
        self.assertEqual(r.status_code, 400)

    def testPUTFail(self):
        """Simple content PUT fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.put('/restms/resource/content_3',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                            <restms xmlns="http://www.restms.org/schema/restms">
                                <content type="text/plain" encoding="ascii" >Just testing.</content>
                            </restms>
                       """)
        self.assertEqual(r.status_code, 405)

    def testPOSTFail(self):
        """Simple content POST fail test (not allowed)"""
        client = tools.RESTclient()
        r = client.post('/restms/resource/message_1',
                content_type="restms+xml",
                data = """<?xml version="1.0"?>
                           <restms xmlns="http://www.restms.org/schema/restms">
                                <content type="text/plain" encoding="ascii" >Just testing.</content>
                           </restms>
                       """)
        self.assertEqual(r.status_code, 405)

