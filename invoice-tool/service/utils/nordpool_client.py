from datetime import datetime
import requests
import logging
from circuitbreaker import circuit
from base.config import Config
from service.utils.excel_operations import invoice_excel_generation

logging.basicConfig(level = logging.DEBUG)

# get config
CONFIG = Config().get_config()
NORD_POOL_INVOICE_DOWNLOAD_ENDPOINT = CONFIG["NORDPOOL"]["INVOICE_DOWNLOAD_ENDPOINT"]
NORD_POOL_AUTH_URL = CONFIG["NORDPOOL"]["AUTH_URL"]
NORD_POOL_TOKEN_URL = CONFIG["NORDPOOL"]["TOKEN_URL"]
NORD_POOL_CLIENT_ID = CONFIG["NORDPOOL"]["CLIENT_ID"]
NORD_POOL_CLIENT_SECRET = CONFIG["NORDPOOL"]["CLIENT_SECRET"]
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60

# Exceptions
class NordPoolException(Exception):
    """
        Exception class to handle NordPool-API Exceptions
    """
    pass

def get_monthly_invoice_file_name(date: datetime)->str:
    """
        generates monthly invoice file name

        Params
        -------
            date : str

        Returns
        -------
            str: invoice file name
    """
    return f'Invoice_{date.strftime("%b%y")}_gesamt.xlsx'

def get_yearly_invoice_file_name(date: datetime)->str:
    """
        generates yearly invoice file name

        Params
        -------
            date : str

        Returns
        -------
            str: invoice file name
    """
    return f'Invoice_{date.strftime("%Y")}.xlsx'

def circuit_fallback(*args, **kwargs):
    """Raises the exception in case the circuit is open
    Raises
    ------
    NoConnexResponseException
        If the failed request to connex server is exceeds the failure_threshold
    """
    logging.exception(f"Nordpool-invoice-downloader request failed")
    raise NordPoolException

class NordPoolApiClient():
    def __init__(self):
        self.user = CONFIG["NORDPOOL"]["USER"]
        self.password = CONFIG["NORDPOOL"]["PASSWORD"]
        self.token = None
    
    def check_nordpool_request_status(self, response, request_url:str, request_description:str):
        """
        checks nordpool requests status is success
        
        Params
        -------
            response : 
            response of the nordpool request
            request_url : str
            nordpool request url name
            request_description: str
            nordpool request description
        Raises
        -------
            NordPoolException: In case of request failure
        """

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            text = f"{request_description} request gives HTTP error response. Request: {request_url}. " \
                   f"Status_code: {response.status_code}. " \
                   f"Content: {response.content}."
            logging.exception(text)
            raise NordPoolException(text)
    
    def load_json(self, file):
        import os
        import json
        filepath = os.path.abspath(
            os.path.join(__file__ ,"../../..")
        )
        relative_path = file.replace("/","\\")
        final_file_path = filepath+"\\"+ relative_path
        with open(final_file_path, "r") as f:
            data = json.load(f)
        return data
    @circuit(failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD, expected_exception=NordPoolException, recovery_timeout=CIRCUIT_BREAKER_RECOVERY_TIMEOUT, fallback_function=circuit_fallback)
    def get_invoice(self, from_delivery_date:str, to_delivery_date:str)->list:
        """
        Endpoint to get the invoice records with in the given date range
        from external nordpool-clearing-api

        Params
        -------
            from_delivery_date : str
            to_delivery_date : str

        Raises
        -------
            NordPoolException: In case of connection failure
        Returns
        -------
            dict: List of invoice records
        int
            HTML statuscode
            200 - Success response i.e, invoice records fetched
            500 - Failed to fetch the invoice records from nordpool-clearing-api
        """
        return self.load_json("tests/unit/assets/nordpool_invoice.json")
        
    
    def excel_generation(self, invoice_file_name:str, from_delivery_date:datetime, to_delivery_date: datetime):
        """
        creates invoice excel file based on generated invoice data
        
        Params
        -------
            invoice_file_name : str
            from_delivery_date : datetime
            to_delivery_date : datetime
        
        Raises
         -------
            ExcelException: In case of excel file creation failure
        """
        invoice_data = self.get_invoice(from_delivery_date.strftime("%Y-%m-%d"), to_delivery_date.strftime("%Y-%m-%d"))
        sorted_invoice_data = sorted(invoice_data, key=lambda item: datetime.strptime(item["FromDeliveryDate"],"%Y-%m-%dT%H:%M:%SZ"))
        invoice_excel_generation(sorted_invoice_data, invoice_file_name)