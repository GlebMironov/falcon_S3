import json
import os

from celery.result import AsyncResult
import falcon
from falcon_multipart.middleware import MultipartMiddleware

from tasks import put_data_to_s3, get_data_from_s3
from config import UPLOAD_PATH, DOWNLOAD_PATH, MAX_FILE_SIZE


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


class Storage(object):

    def on_get(self, req, resp):
        """Storage's GET handler
        
            Note:
                Awaits parameter 'file_key' in the request body.
                Runs celery task for getting file_name by file_key,
                downloads file from AWS S3 storage and returns response as
                file-like object.
        
        """

        body = req.stream.read()
        try:
            file_key = json.loads(body.decode('utf-8'))['file_key']
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing File Key',
                'A File Key must be submitted in the request body.')

        task = get_data_from_s3.delay(file_key)
        task_result = AsyncResult(task.id)
        file_name = task_result.get()
        if not file_name:
            raise falcon.HTTPServiceUnavailable(
                'Service error',
                'Service unavailable.')
            
        resp.content_type = 'application/octet-stream'
        resp.content_location = file_name;
        file_path = os.path.join(DOWNLOAD_PATH, file_name)
        resp.stream_len = os.path.getsize(file_path)
        resp.stream = open(file_path, 'rb')

    @falcon.before(max_body(MAX_FILE_SIZE * 1024 * 1024))
    def on_put(self, req, resp):
        """Storage's PUT handler
        
            Note:
                Awaits parameter 'file' as 'multipart/form-data' in the 
                request body.
                Runs celery task for getting file_key from md5 hash of file,
                uploads file to AWS S3 storage and returns in response file_key.
        
        """

        try:
            file = req.get_param('file')
            file_name = file.filename
        except (AttributeError, ValueError, UnicodeDecodeError):
            raise falcon.HTTPBadRequest(
                'Malformed request',
                'Could not parse the request body.')

        raw = file.file.read()
        file_path = os.path.join(UPLOAD_PATH, file_name)
        with open(file_path, 'wb') as f:
            f.write(raw)

        task = put_data_to_s3.delay(file_path)
        task_result = AsyncResult(task.id)
        file_key = task_result.get()
        if not file_key:
            raise falcon.HTTPServiceUnavailable(
                'Service error',
                'Service unavailable.')

        result = {'file_key': file_key}
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(result)


storage = Storage()

app = falcon.API(middleware=[
    MultipartMiddleware(),
])


app.add_route('/storage', storage)
