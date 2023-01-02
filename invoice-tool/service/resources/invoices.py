import calendar
import os
from flask_restx import Resource, Namespace, reqparse
from datetime import datetime, timedelta
from base.config import Config
from base.kpi import calculate_elapsed_time
from service.utils.download_invoice import download_yearly_file, download_monthly_file
from service.utils.validators import validate_year_and_month
from service import INVOICE_YEARLY_ROOT_PATH, INVOICE_MONTHLY_ROOT_PATH
from service.utils.nordpool_client import get_yearly_invoice_file_name
from service.utils.s3handler import S3HandlerException

# get config
CONFIG = Config().get_config()

api = Namespace("invoices", description="Invoices API")

parser = reqparse.RequestParser()
parser.add_argument(
    "month",
    required=True,
    help="Month of the year for which invoice is required - Format YYYY-MM",
    type=validate_year_and_month
)
@api.route("invoices")
class Invoices(Resource):

    @api.expect(parser)
    @calculate_elapsed_time(method_name="nordpool invoice")
    def get(self):
        """endpoint to get the invoice for particular month of the year as excel file

        Returns
        -------
        file
            invoice file
        
        int
            HTML statuscode
            200 - Success response i.e, successfuly downloaded invoice file
            500 - Failed to download invoice file
            400 - validation error
        raises:
        -------
            S3handlerException
        """
        folder_path = INVOICE_MONTHLY_ROOT_PATH
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        request_data = parser.parse_args()
        request_date = request_data["month"]
        live_date = datetime.strptime(CONFIG["GOLIVEDATE"], "%Y-%m").date()
        if datetime.strptime(request_date, "%Y-%m").date() > datetime.today().date().replace(day=1):
            return {"error": f"No data available as user requested data for future days {request_date}"}, 400
        if datetime.strptime(request_date, "%Y-%m").date() < live_date:
            return {"error": f"The requested data for time period {request_date} is not available. Data is only available from {live_date} onwards."}, 400
        invoice_date = request_date.split('-')
        year = invoice_date[0][-2::]
        month = calendar.month_abbr[int(invoice_date[1].lstrip("0"))]
        file_name = f"Invoice_{month}{year}_gesamt.xlsx"
        file_path = f"{folder_path}/{file_name}"
        return download_monthly_file(file_name, file_path)

@api.route("auto")
class InvoicesAuto(Resource):
    @calculate_elapsed_time(method_name="nordpool auto")
    def get(self):
        """endpoint to get the invoice for particular year as excel file

        Returns
        -------
        file
            invoice file
        
        int
            HTML statuscode
            200 - Success response i.e, successfuly downloaded invoice file
            500 - Failed to download invoice file
        
        raises:
        -------
            S3handlerException
        """
        file_path = INVOICE_YEARLY_ROOT_PATH
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        go_live_year = int(datetime.strptime(CONFIG["GOLIVEDATE"], "%Y-%m").strftime("%y"))
        to_delivery_date = datetime.now()- timedelta(days=1)
        from_delivery_date = to_delivery_date.replace(day=1)
        year = int(from_delivery_date.strftime("%y"))
        if to_delivery_date.month == 1:
            if year > go_live_year:
                month = "Jan"
                overlap_file_name = f"Invoice_{month}{year}_gesamt.xlsx"
                overlap_file_path = f"{INVOICE_YEARLY_ROOT_PATH}/{overlap_file_name}"
                try:
                    download_monthly_file(overlap_file_name, overlap_file_path, overlap=True)
                except S3HandlerException:
                    return {"error": f"Failed to download the invoice file for {month} month from s3"}, 500
            from_delivery_date = from_delivery_date.replace(year=from_delivery_date.year-1)
        file_name = get_yearly_invoice_file_name(from_delivery_date)
        return download_yearly_file(file_name, file_path, int(from_delivery_date.strftime("%y")))