import boto3
import logging
from botocore.exceptions import InvalidRegionError, EndpointConnectionError,\
    ClientError
from boto3.exceptions import S3UploadFailedError

from base.config import Config
from service.utils.excel_operations import merge_excel

CONFIG = Config().get_config()


class S3HandlerException(Exception):
    """
        Exception class to handle S3 Exceptions
    """
    pass

class s3_handler:
    def __init__(self):
        """ method returns s3_handler object, which can be used to interact conviniently with AWS S3
        
        Returns
        --------
            s3_handler 's3_handler'
        
        Raises
        -------
            S3handlerException
        """

        self.region = CONFIG["S3REGION"]
        self.s3_bucket_name = CONFIG["S3BUCKET"]
        self.set_s3_client()
    
    def set_s3_client(self):
        """ method creates s3 client connection
                s3client 'boto3.client('s3')'

        Raises
        -------
            S3handlerException
        """

        try:
            self.client = boto3.client('s3', 
                        region_name = self.region,
                        aws_access_key_id="AKIA4XPLOTLLW6DG6MMB",
                        aws_secret_access_key="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"
            )
        except InvalidRegionError:
            logging.exception("Error occured due to invalid region")
            raise S3HandlerException("error occured due to invalid region")
            
        
    def upload_file_to_s3(self, local_file_path:str, file_name:str):
        """ uploads file from local path to S3 path
        
        Usage
        ------
        s3_handler.upload_file_to_s3(s3_path="s3://BUCKET/PREFIX/filename",
                                     local_path="local_folder/filename") 
        
        Params
        -------
            local_file_path: str
                local path for file upload
            file_name: str
                name of file that to be uploaded to s3
                    
        Raises
        -------
            S3handlerException
        """

        try:
            self.client.upload_file(local_file_path, self.s3_bucket_name, file_name,  ExtraArgs={'ACL':'bucket-owner-full-control'})
            logging.info(f"File {file_name} uploaded successfully to s3.")
        except EndpointConnectionError as e:
            logging.exception("Endpoint connection error occured while uploading file to s3")
            raise S3HandlerException(f"Endpoint connection error occured while uploading file to s3: {e}")
        except S3UploadFailedError as e:
            logging.exception("Client error occured while uploading file to s3")
            raise S3HandlerException(f"Client error occured while uploading file to s3: {e}")
    
    def download_file_from_s3(self, local_file_path:str, file_name:str):
        """ downloads file from S3 path into local path
        
        Usage
        ------
        s3_handler.download_file_from_s3(s3_path="s3://BUCKET/PREFIX/filename",
                                         local_path="local_folder/filename") 
        
        Params
        ------- 
            local_path: str
                local path for file download
            file_name: str
                name of file that to be downloaded from s3
                    
        Raises
        -------
            S3handlerException
        """

        try:
            self.client.download_file(self.s3_bucket_name, file_name, local_file_path)
            logging.info(f"File {file_name} downloaded successfully from s3.")
        except EndpointConnectionError as e:
            logging.exception(f"Endpoint connection error occured while downloading file from s3: {file_name}")
            raise S3HandlerException(f"Endpoint connection error occured while downloading file from s3: {e}")
        except ClientError as e:
            logging.exception(f"Client error occured while downloading file from s3: {file_name}")
            raise S3HandlerException(f"Client error occured while downloading file from s3: {e}")
    

    def download_multiple_files_from_s3(self, local_file_path:str, dest_file_name:str, year:int):
        """ downloads multiple files from S3 path into local path
        
        Usage:
        ------
        s3_handler.download_file_from_s3(s3_path="s3://BUCKET/PREFIX/filename",
                                         local_path="local_folder/filename") 
        
        Params
        ------- 
            local_file_path: str
                local path for file download
            dest_file_name: str
                file name of the yearly invoice that is served to user
            year: int
              invoice year(format of %y) i.e. example: 22     
        
        Raises
        -------
            S3handlerException
        """
        try:
            object_responses = self.client.list_objects(Bucket = self.s3_bucket_name)["Contents"]
        except ClientError as e:
            logging.exception(f"Client error occured while accessing s3 bucket {self.s3_bucket_name} contents")
            raise S3HandlerException(f"Client error occured while downloading file from s3: {e}")
        for object_response in object_responses:
            file_name = object_response["Key"]
            invoice_monthly_postfix = "gesamt.xlsx"
            if file_name.endswith(invoice_monthly_postfix):
                try:
                    invoice_year = int(file_name.split("_")[1][-2:])
                    file_name_without_prefix = file_name.partition("/")[2]
                except IndexError:
                    logging.exception(f"file_name is not in the correct format:{file_name}")
                    raise 
                if invoice_year == year:
                    file_path = f"{local_file_path}/{file_name_without_prefix}"
                    self.download_file_from_s3(file_path, file_name)
        merge_excel(dest_file_name)
        