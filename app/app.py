import falcon
from falcon_multipart.middleware import MultipartMiddleware

from handlers import storage


file_storage = storage.Storage()

app = falcon.API(middleware=[
    MultipartMiddleware(),
])


app.add_route('/storage', file_storage)
