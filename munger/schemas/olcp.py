import datetime

from cerberus import Validator

from ..validations import has_only_ascii, is_upper, uds_style_path

OLCP_STATE_ABBREVIATIONS = [
    "AL",
    "AR",
    "AZ",
    "CA",
    "CO",
    "CT",
    "CZ",
    "DC",
    "DE",
    "FL",
    "GA",
    "GU",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "MT",
    "MX",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "PR",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VA",
    "VI",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
    "AK",
]

ILLEGAL_EXTENSIONS = [
    "BAT",
    "C",
    "CDA",
    "CMD",
    "COM",
    "CPL",
    "DAT",
    "DB",
    "DLL",
    "DOT",
    "DSS",
    "ESX",
    "EXE",
    "FILE",
    "HTA",
    "JOB",
    "JPE",
    "LNK",
    "LOG",
    "M4A",
    "MDI",
    "MHT",
    "MPG",
    "MSG",
    "OCX",
    "PAK",
    "PIF",
    "PKG",
    "PRN",
    "RAR",
    "SCR",
    "SDA",
    "SHS",
    "SNP",
    "URL",
    "V1",
    "VBS",
    "VCF",
    "VPS",
    "VPT",
    "XPS",
    "ZIP",
    "",
]


def has_date_format(format_str: str):
    def date_format_checker(field, value, error):
        try:
            datetime.datetime.strptime(value, format_str)
        except ValueError:
            error(field, f"Date must be in {format_str} format")

    return date_format_checker


def no_cr_lf(field, value, error):
    if "\r" in value or "\n" in value:
        error(field, "Cannot contain CR or LF characters")


IMAGE_STATION_SCHEMA = {
    "RecordID": {
        # this is an autoID, do they really want us to provide it?
        "required": True,
        "type": "integer",
    },
    "Orig_DocumentEntityIDNbr": {
        "required": False,
        "type": "string",
        "maxlength": 20,
    },
    "DocumentEntityIDNbr": {  # Claim Number (or Policy)
        "required": True,
        "type": "string",
        "maxlength": 20,
    },
    "Orig_DocumentID": {
        "required": False,
        "type": "string",
        "maxlength": 30,
    },
    "DocumentID": {  # "Document Primary Key"
        "required": False,
        "type": "string",
        "maxlength": 30,
    },
    "Orig_DocumentPageNbr": {
        "required": False,
        "type": "string",
        "maxlength": 9,
    },
    "DocumentPageNbr": {  # Page Number, if present
        "required": False,
        "type": "string",
        "maxlength": 9,
    },
    "Orig_DocumentPath": {  # original path (1st 256 characters)
        "required": False,
        "type": "string",
        "maxlength": 256,
    },
    "DocumentPath": {  # Relative path in DRL repo
        "required": True,
        "type": "string",
        "maxlength": 256,
        "combined_maxlength": ("DocumentFileName", 185),
        "check_with": (has_only_ascii, uds_style_path),
    },
    "Orig_DocumentFileName": {  # File name in source
        "required": False,
        "type": "string",
        "maxlength": 256,
    },
    "DocumentFileName": {  # File name in UDS I (and DRL); NO ASCII
        "required": True,
        "type": "string",
        "maxlength": 256,
        "combined_maxlength": ("DocumentPath", 185),
        "check_with": has_only_ascii,
    },
    "Orig_DocumentDate": {  # Original system date (of creation, not extraction)
        "required": False,
        "type": "string",
        "maxlength": 20,
    },
    "DocumentDate": {  # Time of creation in MMDDYYYY format
        "required": True,
        "type": "string",
        "maxlength": 8,
        "check_with": has_date_format("%m%d%Y"),
    },
    "Orig_DocumentTime": {  # Original system time (of creation, not extraction)
        "required": False,
        "type": "string",
        "maxlength": 20,
    },
    "DocumentTime": {  # Time of creation fit to 8 characters
        "required": True,
        "type": "string",
        "maxlength": 8,
    },
    "Orig_DocumentType": {  # Original type for reference, eg. "Closed Claims"
        "required": False,
        "type": "string",
        "maxlength": 30,
    },
    "DocumentType": {  # Logical description assigned by DRL, eg. "Closed Claims"
        "required": True,
        "type": "string",
        "maxlength": 30,
    },
    "Orig_DocumentDescription": {  # Company-provided description
        "required": False,
        "type": "string",
        "maxlength": 128,
    },
    "DocumentDescription": {  # Company-proviced description; ASCII only!
        "required": True,
        "type": "string",
        "maxlength": 128,
        "check_with": (has_only_ascii, no_cr_lf),
    },
    "Orig_DocumentFileType": {  # Company-provided extension forced to 4 characters
        "required": False,
        "type": "string",
        "maxlength": 4,
    },
    "DocumentFileType": {  # Extension of file
        "required": True,
        "type": "string",
        "maxlength": 4,
        "check_with": (has_only_ascii, is_upper),
        "forbidden": ILLEGAL_EXTENSIONS,
    },
    "DocumentFolderType": {  # policy vs claim
        "required": True,
        "type": "string",
        "maxlength": 6,
        "allowed": ["POLICY", "CLAIM"],
    },
    "DocumentState": {
        "required": True,
        "type": "string",
        "maxlength": 2,
        "allowed": OLCP_STATE_ABBREVIATIONS,
    },
    "DocumentComments": {  # Long document description, if it's present in the data
        "required": False,
        "type": "string",
        "maxlength": 500,
    },
    "DocumentDatetime": {  # timestamp translation of company document date (SQL timestamp?)
        "required": True,
        "type": "datetime",  # maybe should be string with a SQL format check_with
    },
    "Orig_Index1": {  # primary key of source data, if present
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "Index1": {  # primary key from vendor provided index, if present
        "required": True,
        "type": "string",
        "maxlength": 50,
    },
    "Orig_Index2": {  # Alternate key if present
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "Index2": {
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "Orig_Index3": {  # Alternate key if present
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "Index3": {
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "Orig_Index4": {  # Alternate key if present
        "required": True,
        "type": "string",
        "maxlength": 50,
    },
    "Index4": {
        "required": True,
        "type": "string",
        "maxlength": 50,
    },
    "Orig_DocumentDrawer": {  # Only for ImageRight companies
        "required": True,
        "type": "string",
        "maxlength": 500,
    },
    "DocumentDrawer": {  # Only for ImageRight companies
        "required": True,
        "type": "string",
        "maxlength": 500,
    },
    "Orig_DocumentNumberofPages": {  # Only for ImageRight companies
        "required": True,
        "type": "string",
        "maxlength": 50,
    },
    "DocumentNumberofPages": {  # Only for ImageRight companies
        "required": True,
        "type": "string",
        "maxlength": 50,
    },
    "ExceptionRecord": {  # If index points to a bad docuent or unusable file type, set to 1
        "required": True,
        "type": "boolean",
    },
    "ExceptionDescription": {  # If above is 1, describe the exception, eg. "Invalid File Type"
        "required": True,
        "type": "string",
        "maxlength": 100,
    },
    "Processed": {  # Set to 0 on initial load
        "required": True,
        "type": "boolean",
        "allowed": [False],  # amazing
    },
    "DataSource": {  # Fill with something meaningful and not blank
        "required": True,
        "type": "string",
        "maxlength": 50,
    },
    "Updatedate": {  # DRL load date (can probably exclude
        "required": True,
        "type": "datetime",
    },
    "Updatedby": {  # DRL load user
        "required": True,
        "type": "string",
        "maxlength": 30,
    },
    "Createdate": {  # DRL create date (can probably exclude
        "required": True,
        "type": "datetime",
    },
    "Createdby": {  # DRL create user
        "required": True,
        "type": "string",
        "maxlength": 30,
    },
    "pdfContent": {  # Set to NULL
        "required": False,
        "type": "string",
        "allowed": ["NULL"],
    },
}


class ImageStationValidator(Validator):
    def _validate_combined_maxlength(self, constraint, field, value):
        """Test that two fields' lengths add up to less than the max

        The rule's arguments are validated against this schema:
        {'type': 'list'}
        """
        partner_field, combined_max = constraint

        if partner_field not in self.document:
            return False

        if len(value) + len(self.document[partner_field]) > combined_max:
            self._error(
                field,
                f"Length of {field} and {partner_field} together must be less than {combined_max}",
            )
