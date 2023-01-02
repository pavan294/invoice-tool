import pytest
from service.utils.s3handler import s3_handler, S3HandlerException
from unittest.mock import patch
from botocore.exceptions import EndpointConnectionError, ClientError, InvalidRegionError

S3_HANDLER = s3_handler()

def test_set_s3_client_exception():
    with patch('boto3.session.Session.client', side_effect= InvalidRegionError(region_name="test_region")) as mock_s3_exception:
        with pytest.raises(S3HandlerException):
            s3_handler().set_s3_client()


def test_download_client_error():
    with patch('botocore.client.BaseClient._make_api_call', side_effect= ClientError(error_response={"Error": {"Code": 123, "Message": "error while uploading file"}}, operation_name = "download")) as mock_s3_exception:
        with pytest.raises(S3HandlerException) as e:
            S3_HANDLER.download_file_from_s3("bad_file", "test_file")
    
def test_download_endpoint_connection_fail():
    with patch('botocore.client.BaseClient._make_api_call', side_effect= EndpointConnectionError(endpoint_url="test_url")) as mock_s3_exception:
        with pytest.raises(S3HandlerException) as e:
            S3_HANDLER.download_file_from_s3("bad_file", "test_file")


def test_upload_endpoint_connection_fail():
    from service import get_local_file_path
    with patch('botocore.client.BaseClient._make_api_call', side_effect= EndpointConnectionError(endpoint_url="test_url")) as mock_s3_exception:
        with pytest.raises(S3HandlerException):
            S3_HANDLER.upload_file_to_s3(get_local_file_path("invoice/invoice_info.txt"), "test_file")

def test_upload_client_error():
    from service import get_local_file_path
    with patch('botocore.client.BaseClient._make_api_call', side_effect= ClientError(error_response={"Error": {"Code": 123, "Message": "error while uploading file"}}, operation_name = "upload")) as mock_s3_exception:
        with pytest.raises(S3HandlerException):
            S3_HANDLER.upload_file_to_s3(get_local_file_path("invoice/invoice_info.txt"), "test_file")

def test_download_multiple_files_client_error():
    with patch('botocore.client.BaseClient._make_api_call', side_effect= ClientError(error_response={"Error": {"Code": 123, "Message": "error while uploading file"}}, operation_name = "upload")) as mock_s3_exception:
        with pytest.raises(S3HandlerException):
            S3_HANDLER.download_multiple_files_from_s3("test_path", "test_file", 22)


def test_download_multiple_files_index_error(monkeypatch):
    class S3_Object():

        def __init__(self, *args, **kwargs):
            pass
    
        def list_objects(self, Bucket):
            return {"Contents": [{"Key": "testgesamt.xlsx"}]}
   
    def set_client(self):
        self.client = S3_Object()
    
    monkeypatch.setattr(s3_handler, "set_s3_client", set_client)   
    with pytest.raises(IndexError):
            s3_handler().download_multiple_files_from_s3("test_path", "test_file", 22)