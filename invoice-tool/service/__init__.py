import os
from pathlib import Path
ROOT_PATH = str(Path(__file__).parent.parent).replace("\\", "/")
INVOICE_ROOT_PATH = f"{ROOT_PATH}/invoice"
INVOICE_YEARLY_ROOT_PATH = f"{INVOICE_ROOT_PATH}/yearly"
INVOICE_MONTHLY_ROOT_PATH = f"{INVOICE_ROOT_PATH}/monthly"
INVOICE_MERGE_ROOT_PATH = f"{INVOICE_ROOT_PATH}/merged"

def get_local_file_path(file):
    return os.path.join(
        os.path.dirname(os.path.abspath('__file__')), file
    )