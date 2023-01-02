import shutil
import logging
from flask import Response, after_this_request
from service.utils.s3handler import s3_handler, S3HandlerException
from service import INVOICE_YEARLY_ROOT_PATH, INVOICE_MONTHLY_ROOT_PATH, INVOICE_MERGE_ROOT_PATH

logging.basicConfig(level = logging.DEBUG)
def execute_invoice_download(file_path:str, file_name:str, yearly:bool=False):
    """
    downloads invoice excel file and deletes in local after serving file to user

    Params
    -------
        file_path:  str
            local path of downloaded invoice file from s3
        file_name: str
            invoice filename
        yearly: bool
            checks yearly or monthly invoice

    Returns
    -------
    file
        invoice file
    """
    # this will delete the s3 downloaded invoice from local after serving the request
    @after_this_request
    def remove_file(response):
        """
        removes downloaded invoice excel file in the service locally

        Params
        -------
            response:
               response of the downloaded invoice file
        
        raises:
        -------
            S3handlerException
            OSError
            IOError
        """
        logging.info(f"Invoice file {file_name} served successfully")
        try:
            if yearly:
               shutil.rmtree(INVOICE_YEARLY_ROOT_PATH)
               shutil.rmtree(INVOICE_MERGE_ROOT_PATH)
            else:
                shutil.rmtree(INVOICE_MONTHLY_ROOT_PATH)
        except (OSError, IOError):
            logging.exception("Error occured while closing and removing the invoice after downloading from s3.")
        return response
    try:
        with open(file_path, 'rb') as file_handler:
            return Response(file_handler.read(), 
                            mimetype="application/vnd.ms-excel",
                            headers={"Content-disposition": f"attachment; filename={file_name}"})
    except OSError:
        return {"error": "Error occured while serving the invoice after downloading from s3."}, 500
    
def download_monthly_file(file_name:str, file_path:str, overlap:bool=False):
    """
    downloads invoice excel file

    Params
    -------
        file_name: str
            invoice filename
        file_path:  str
            local path of downloaded invoice file from s3
        overlap: bool
           overlap if month is jan and it is yearly invoice

    Returns
    -------
    file
        invoice file
    
    raises:
    -------
        S3handlerException
    """
    try:
        s3_handler().download_file_from_s3(file_path, f"invoices/{file_name}")
    except S3HandlerException:
        if overlap:
            raise S3HandlerException("Failed to download the invoice file for jan month from s3")
        return {"error": "Failed to download the invoice from s3"}, 500
    if overlap:
       return 
    return execute_invoice_download(file_path, file_name)



def download_yearly_file(file_name: str, file_path: str, year:int):
    """
    downloads invoice excel file

    Params
    -------
        file_name: str
            invoice filename
        file_path:  str
            local path of downloaded invoice file from s3
        year: int
           invoice year(format of %y) i.e. example: 22
    Returns
    -------
    file
        invoice file
    
    raises:
    -------
        S3handlerException
    """
    try:
        s3_handler().download_multiple_files_from_s3(file_path, file_name, year)
    except S3HandlerException:
        return {"error": "Failed to download the invoice from s3"}, 500
    return execute_invoice_download(f"{INVOICE_MERGE_ROOT_PATH}/{file_name}", file_name, True)