import urllib
from django.test import client

class RESTclient(client.Client):
    def put(self, path, data={}, content_type=client.MULTIPART_CONTENT, **extra):
        """
        Requests a response from the server using PUT.
        """
        if content_type is client.MULTIPART_CONTENT:
            put_data = client.encode_multipart(BOUNDARY, data)
        else:
            put_data = data

        r = {
            'CONTENT_LENGTH': len(put_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      urllib.unquote(path),
            'REQUEST_METHOD': 'PUT',
            'wsgi.input':     client.FakePayload(put_data),
        }
        r.update(extra)

        return self.request(**r)

    def delete(self, path, **extra):
        """
        Requests a response from the server using DELETE.
        """
        r = {
            'PATH_INFO':      urllib.unquote(path),
            'REQUEST_METHOD': 'DELETE',
        }
        r.update(extra)

        return self.request(**r)

def extract_header(response):
    buf = "".join([ str(response.status_code),
                    reduce(lambda coll, item: 
                                "".join([coll, str(item)]), 
                           response) ])
    return buf

def linediff(s1, s2, message=""):
    if s1 == s2: return True
    a = s1.split("\n")
    b = s2.split("\n")
    if len(a) > len(b):
        b.extend([ "" for i in range( len(a) - len(b)) ])
    elif  len(a) < len(b):
        a.extend([ "" for i in range( len(b) - len(a)) ])
    for i in range(len(a)):
        if a[i] != b[i]: 
            print "Line #%d %s:\nis : [%s]\nexp: [%s]" % (i, message, a[i], b[i])
    return False 

