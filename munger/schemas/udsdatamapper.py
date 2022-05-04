from ..validations import (
    has_only_ascii,
    is_numeric,
    has_datamapper_date_format,
    has_datamapper_time_format,
    uds_style_path,
    does_not_have_char,
)

IRECORD_MAP_SCHEMA = {
    "insolvent co claim number": {
        "required": True,
        "type": "string",
        "maxlength": 20,
        "check_with": has_only_ascii,
    },
    "claimant number": {
        "required": True,
        "type": "string",
        "maxlength": 5,
        "check_with": is_numeric,
    },
    "capture date": {
        "required": True,
        "type": "string",
        "check_with": has_datamapper_date_format,
    },
    "document path": {
        "required": True,
        "type": "string",
        "check_with": (uds_style_path, has_only_ascii),
        "maxlength": 256,
    },
    "document file name": {
        "required": True,
        "type": "string",
        "check_with": has_only_ascii,
        "maxlength": 256,
    },
    "file type": {
        "required": True,
        "type": "string",
        "maxlength": 4,
        "check_with": does_not_have_char("."),
    },
    "alternate index 1": {
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "alternate index 2": {
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "alternate index 3": {
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "alternate index 4": {
        "required": False,
        "type": "string",
        "maxlength": 50,
    },
    "document id": {
        "required": False,
        "type": "string",
        "maxlength": 30,
    },
    "document page number": {
        "required": False,
        "type": "string",
        "maxlength": 9,
    },
    "capture time": {
        "required": False,
        "type": "string",
        "check_with": has_datamapper_time_format,
    },
    "folder type": {
        "required": False,
        "type": "string",
        "maxlength": 6,
    },
    "document type": {
        "required": False,
        "type": "string",
        "maxlength": 30,
    },
    "fund claim number": {
        "required": False,
        "type": "string",
        "maxlength": 20,
    },
    "doc descriptor or comment": {
        "required": False,
        "type": "string",
        "maxlength": 128,
    },
}
