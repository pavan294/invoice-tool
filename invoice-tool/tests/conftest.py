import pytest
from request_id.middleware.correlation_middleware import CorrelationId

@pytest.fixture
def app():
    from service.main import create_app
    app = create_app()
    app.debug = True
    app.wsgi_app = CorrelationId(app)
    return app


class S3_Object():
    """ This class is used to imitate an S3 object. It is dictionary that applies an arbitrary key-altering
       function before accessing the keys. Instances of this class ARE NOT S3 objects, they only mimic behaviour
       of S3 objects. This class is also used to mimic S3 Object collection behaviour.
       (This class is capable of holding instances of itself)"""

    def __init__(self, *args, **kwargs):
        pass
    
    def put(self, **kwargs):
        pass
    
    def Object(self, bucket, prefix):
        return self
    
    def Bucket(self, bucket):
        self.objects = self
        return self
    
    def download_file(self, bucket, key, local_path):
        pass
    
    def upload_file(self, local_path, bucket, key, **kwargs):
        pass
        
    def filter(self, Prefix):
        return self
    
    def list_objects(self, Bucket):
        return {"Contents": [{"Key": "test.xlsx"}]}
    

@pytest.fixture
def mock_set_client(monkeypatch):
    def set_client(self):
        self.client = S3_Object()
    from service.utils.s3handler import s3_handler
    monkeypatch.setattr(s3_handler, "set_s3_client", set_client)