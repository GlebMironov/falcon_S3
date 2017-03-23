import hashlib

import falcon

def max_body(limit):
    """Decorator to limit the size of the uploaded file
    
        Note:
            Awaits parameter 'limit' in MB.
    
    """

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the file is too large. The file must not '
                   'exceed ' + str(limit) + ' bytes in length.')
            raise falcon.HTTPRequestEntityTooLarge(
                'File size is too large', msg)
    return hook

def read_chunks(f, chunk_size=8192):
    """Read file
    
        Note: 
            Reads potentially big file by chunks
    
    """

    while True:
        data = f.read(chunk_size)
        if not data:
            break
        yield data

def md5(f):
    """Obtain the md5 digest
    
        Note: 
            Obtains md5 hash function of file-like object
    
    """

    h = hashlib.md5()
    for chunk in read_chunks(f):
        h.update(chunk)
    return h.hexdigest()
