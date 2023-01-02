from unittest.mock import Mock
import pytest
import json
import os
from datetime import datetime
from service.utils import download_invoice
from freezegun import freeze_time
from mock import patch, mock_open, call
from botocore.exceptions import EndpointConnectionError
from service import ROOT_PATH

NORDPOOL_INVOICE_MONTHLY_URL = "/test/invoices"
NORDPOOL_INVOICE_YEARLY_URL = "/test/auto"

@pytest.mark.parametrize("month", [
    pytest.param("", id="empty_month"),
    pytest.param("invalid-month", id="invalid_month_value")
])
def test_invoice_download_invalid_month(client, month):
    response = client.get(
        f"{NORDPOOL_INVOICE_MONTHLY_URL}",
        query_string={"month": month},
    )
    assert response.status_code == 400

@freeze_time("2022-12-30")
@pytest.mark.usefixtures("mock_set_client")
@pytest.mark.parametrize("month", [
    pytest.param("2022-10", id="month_starting_with_0"),
    pytest.param("2022-12", id="month_starting_without_0")
])
def test_invoice_monthly_download_success(client, month):
    with patch('os.remove'):
        file_data = mock_open(read_data = b"Test Mock")
        with patch("builtins.open", file_data):
            response = client.get(
                f"{NORDPOOL_INVOICE_MONTHLY_URL}",
                query_string={"month": month},
            )
            assert response.status_code == 200

@freeze_time("2022-09-30")
@pytest.mark.usefixtures("mock_set_client")
def test_invoice_yearly_download_success(client):
    with patch('os.remove'):
        file_data = mock_open(read_data = b"Test Mock")
        with patch("builtins.open", file_data):
            response = client.get(
                f"{NORDPOOL_INVOICE_YEARLY_URL}"
            )
            assert response.status_code == 200

@freeze_time("2022-10-30")
def test_invoice_download_s3_exception(client):
    with patch('botocore.client.BaseClient._make_api_call', side_effect= EndpointConnectionError(endpoint_url="test_url")) as mock_s3_exception:
        response = client.get(
            f"{NORDPOOL_INVOICE_MONTHLY_URL}",
            query_string={"month": "2022-10"},
        )
        assert response.json == {"error": "Failed to download the invoice from s3"}
        assert response.status_code == 500

@freeze_time("2022-10-30")
def test_invoice_auto_download_s3_exception(client, monkeypatch):
    from service.utils.s3handler import s3_handler
    class S3_Object():
        def __init__(self, *args, **kwargs):
            pass
    
        def Bucket(self, bucket):
            self.objects = self
            return self
    
        def download_file(self, bucket, key, local_path):
            raise EndpointConnectionError(endpoint_url="test_url")
    
        def list_objects(self, Bucket):
            return {"Contents": [{"Key": "invoice_Aug22_gesamt.xlsx"}]}
    def set_client(self):
        self.client = S3_Object()
    monkeypatch.setattr(s3_handler, "set_s3_client", set_client)
    
    response = client.get(
            f"{NORDPOOL_INVOICE_YEARLY_URL}"
        )
    assert response.json == {"error": "Failed to download the invoice from s3"}
    assert response.status_code == 500

@freeze_time("2020-10-30")
def test_invoice_auto_year_mismatch(client, monkeypatch):
    # invoice year and year of the files in s3 bucket mismatch
    from service.utils.s3handler import s3_handler
    class S3_Object():
        def __init__(self, *args, **kwargs):
            pass
    
        def Bucket(self, bucket):
            self.objects = self
            return self
    
        def download_file(self, bucket, key, local_path):
            raise EndpointConnectionError(endpoint_url="test_url")
    
        def list_objects(self, Bucket):
            return {"Contents": [{"Key": "invoice_Aug22_gesamt.xlsx"}]}
    def set_client(self):
        self.client = S3_Object()
    monkeypatch.setattr(s3_handler, "set_s3_client", set_client)
    with patch("service.utils.s3handler.s3_handler.download_file_from_s3") as mock_download:
        response = client.get(
                f"{NORDPOOL_INVOICE_YEARLY_URL}"
            )
        assert response.status_code == 500
        mock_download.assert_not_called()

@freeze_time("2022-10-30")
@pytest.mark.usefixtures("mock_set_client")
def test_invoice_download_open_failure(client):
    with patch('os.remove'):
        with patch("builtins.open", new_callable=mock_open) as mock_file_open:
            mock_file = mock_file_open.return_value
            mock_file.read.side_effect = OSError
            response = client.get(
                f"{NORDPOOL_INVOICE_MONTHLY_URL}",
                query_string={"month": "2022-10"},
            )
            assert json.loads(response.data.decode("utf-8")) == {"error": "Error occured while serving the invoice after downloading from s3."}
            assert response.status_code == 500


@freeze_time("2022-10-30")
@pytest.mark.usefixtures("mock_set_client")
@pytest.mark.parametrize("month", [
    pytest.param(True),
    pytest.param(False)
])
def test_invoice_download_remove_failure(client, month):
    download_invoice.logging = Mock()
    with patch('shutil.rmtree') as mock_remove_file:
        mock_remove_file.side_effect = OSError
        with patch("builtins.open", new_callable=mock_open) as mock_file_open:
            mock_file = mock_file_open.return_value
            mock_file.read.return_value= b"Test Mock"
            if month:
                response = client.get(
                    f"{NORDPOOL_INVOICE_MONTHLY_URL}",
                    query_string={"month": "2022-10"},
                )
            else:
                response = client.get(
                        f"{NORDPOOL_INVOICE_YEARLY_URL}"
                    )
            download_invoice.logging.exception.assert_has_calls([
                call('Error occured while closing and removing the invoice after downloading from s3.'),
                ])
            # retuns 200 because file is served but error is logged because it does not remove file from local and this will be catched by the kibana monitor
            assert response.status_code == 200


@freeze_time("2022-06-30")
def test_invoice_download_future_data_request(client):
    month = "2022-09"
    response = client.get(
        f"{NORDPOOL_INVOICE_MONTHLY_URL}",
        query_string={"month": f"{month}"},
    )
    assert response.json == {"error": f"No data available as user requested data for future days {month}"}
    assert response.status_code == 400

@freeze_time("2022-06-30")
def test_invoice_download_past_data_request(client):
    month = "2021-11"
    live_date = datetime.strptime("2022-10", "%Y-%m").date()
    response = client.get(
        f"{NORDPOOL_INVOICE_MONTHLY_URL}",
        query_string={"month": f"{month}"},
    )
    assert response.json == {"error": f"The requested data for time period {month} is not available. Data is only available from {live_date} onwards."}
    assert response.status_code == 400


@freeze_time("2023-01-30")
def test_invoice_yearly_download_overlap_failure(client):
    with patch('botocore.client.BaseClient._make_api_call', side_effect= EndpointConnectionError(endpoint_url="test_url")) as mock_s3_exception:
            response = client.get(
                f"{NORDPOOL_INVOICE_YEARLY_URL}"
            )
    assert response.status_code == 500
    assert response.json == {"error": "Failed to download the invoice file for Jan month from s3"}

@pytest.mark.usefixtures("mock_set_client")
@freeze_time("2023-01-30")
def test_invoice_yearly_download_overlap_success1(client):
    # year is greater than go-live-year
    os.chdir(f"{ROOT_PATH}/tests/unit")
    with patch("shutil.rmtree"):
        file_data = mock_open(read_data = b"Test Mock")
        with patch("builtins.open", file_data):
            response = client.get(
                f"{NORDPOOL_INVOICE_YEARLY_URL}"
            )
            assert response.status_code == 200
    os.chdir(ROOT_PATH)

@pytest.mark.usefixtures("mock_set_client")
@freeze_time("2022-01-30")
def test_invoice_yearly_download_overlap_success2(client):
    # year is not greater than go-live-year
    download_invoice.logging = Mock()
    os.chdir(f"{ROOT_PATH}/tests/unit")
    with patch("shutil.rmtree"):
        file_data = mock_open(read_data = b"Test Mock")
        with patch("builtins.open", file_data):
            response = client.get(
                f"{NORDPOOL_INVOICE_YEARLY_URL}"
            )
            assert response.status_code == 200
    file_name = "Invoice_2021.xlsx"
    download_invoice.logging.info.assert_called_once_with(
        f"Invoice file {file_name} served successfully")
    os.chdir(ROOT_PATH)