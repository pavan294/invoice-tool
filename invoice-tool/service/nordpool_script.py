import os
import logging
from base.config import Config
from datetime import datetime, timedelta
from service.utils.nordpool_client import NordPoolApiClient, get_monthly_invoice_file_name
from service import get_local_file_path
from service.utils.s3handler import s3_handler
# get config
CONFIG = Config().get_config()

logging.basicConfig(level = logging.DEBUG)

def execute_nordpool_script(nordpool_client, invoice_file_name:str, from_delivery_date:datetime, to_delivery_date:datetime):
    """ 
       cron-job executes the nordpool script and initaites file uploading process
    Params
    -------
        invoice_file_name : str
            name of the monthly invoice excel which should be uploaded to s3
        from_delivery_date : datetime
            start date to fecth data from external nordpool clearing api
        to_delivery_date : datetime
            end date to fecth data from external nordpool clearing api
    """
    nordpool_client.excel_generation(invoice_file_name, from_delivery_date, to_delivery_date)
    invoice_file_path = get_local_file_path(invoice_file_name)
    s3_handler().upload_file_to_s3(invoice_file_path, f"invoices/{invoice_file_name}")
    os.remove(invoice_file_path)

def start_monthly_nordpool_script(to_delivery_date:datetime, nordpool_client):
    """ 
      cron-job initiates nordpool script
    Params
    -------
        to_delivery_date : datetime
          end date to fecth data from external nordpool clearing api
    """
    from_delivery_date = to_delivery_date.replace(day=1)
    invoice_file_name = get_monthly_invoice_file_name(to_delivery_date)
    execute_nordpool_script(nordpool_client, invoice_file_name, from_delivery_date, to_delivery_date)

def main():
    logging.info("Started nordpool script.")
    to_delivery_date = datetime.now() - timedelta(days=1)
    NordPoolClient = NordPoolApiClient()
    start_monthly_nordpool_script(to_delivery_date, NordPoolClient)
    logging.info("Ended nordpool script.")

if __name__ == '__main__':
    main()
