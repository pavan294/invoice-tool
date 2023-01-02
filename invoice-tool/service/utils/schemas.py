from marshmallow import Schema, fields, ValidationError, validates
from datetime import datetime

class InvoiceRecordSchema(Schema):
    """
    Marshmallow schema to validate records data
    """
    Paid = fields.Bool(required=True, error_messages={
                                  "required": "Paid is required"})

    Markets = fields.Method(error_messages={
                                  "required": "Markets is required"}, deserialize="validate_markets", allow_none=True)
    
    InvoiceNumber = fields.String(required=True, error_messages={
                                  "required": "InvoiceNumber is required"})

    InvoiceDate =  fields.Method(error_messages={
                                  "required": "InvoiceDate is required"}, deserialize="is_valid_date", allow_none=True)

    DueDate =  fields.Method(error_messages={
                                  "required": "DueDate is required"}, deserialize="is_valid_date", allow_none=True)

    CreditBankAccount =  fields.String(required=True, error_messages={
                                  "required": "CreditBankAccount is required"})

    DebitBankAccount =  fields.String(required=True, error_messages={
                                  "required": "DebitBankAccount is required"})

    InvoiceAccount = fields.String(required=True, error_messages={
                                  "required": " InvoiceAccount is required"})

    Currency = fields.String(required=True, error_messages={
                                  "required": "Currency is required"})

    TotalAmount = fields.Float(required=True, error_messages={
                                  "required": "TotalAmount is required"})

    HasPdfDownload =  fields.Bool(required=True, error_messages={
                                  "required": "HasPdfDownload is required"})

    HasXmlDownload =  fields.Bool(required=True, error_messages={
                                  "required": "HasXmlDownload is required"})

    SettlementTransactionIds = fields.List(fields.Int(), required=True, error_messages={
                                  "required": "SettlementTransactionIds is required"})

    FromDeliveryDate = fields.Method(error_messages={
                                  "required": "FromDeliveryDate is required"}, deserialize="is_valid_date", allow_none=True)

    ToDeliveryDate = fields.Method(error_messages={
                                  "required": "ToDeliveryDate is required"}, deserialize="is_valid_date", allow_none=True)

    Country = fields.String(required=True, error_messages={
                                  "required": "Country is required"})

    ReferenceNumber = fields.String(required=True, error_messages={
                                  "required": "ReferenceNumber is required"})

    LegalEntityCode = fields.String(required=True, error_messages={
                                  "required": "LegalEntityCode is required"})

    LegalEntityName = fields.String(required=True, error_messages={
                                  "required": "LegalEntityName is required"})

    OrganizationNumber = fields.String(required=True, error_messages={
                                  "required": "OrganizationNumber is required"})


    def is_valid_date(self, value):
        """
        Method to check if date is valid date or not

        Raises
        ------
        ValidationError
        """
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValidationError("date is not in correct format")
    
    @validates("InvoiceNumber")
    def is_valid_numeric_string(self, value):
        """
        Method to check if string contains all numbers

        Raises
        ------
        ValidationError
        """
        if not value.isnumeric():
            raise ValidationError("string should contain only numbers")
    
    def validate_markets(self, values):
        """
        Method to check if market value contains only strings a-z

        Raises
        ------
        ValidationError
        """
        if type(values) != list:
            raise ValidationError("market value should be list of strings containing characters range from  a-z")
        else:
            for value in values:
                if not value.isalpha():
                  raise ValidationError("market value should be list of strings containing characters only range from a-z")