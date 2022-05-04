"""
Validation functions that are common across multiple schemas
"""
import re
import datetime

NONASCII = r"[^\x00-\x7F]"


def has_only_ascii(field, value, error):
    if re.search(NONASCII, value):
        error(field, "Contains non-ASCII character(s)")


def is_upper(field, value, error):
    if value.upper() != value:
        error(field, "Should be uppercase")


def uds_style_path(field, value, error):
    if "/" in value or value[0] != "\\" or value[-1] != "\\":
        error(field, "Must use UDS path standard")


def is_numeric(field, value, error):
    """Validates for strings that only contain numeric characters

    Interesting aside, Python has an isnumeric() function for strings.
    This works the same as isdigit() but also allows numbers from foreign
    writing systems, eg. "一二三四五".isnumeric() is True.
    We don't want that so I use isdigit().
    """
    if not value.isdigit():
        error(field, "Should be only numbers")


def has_datamapper_date_format(field, value, error):
    """Validates that the value uses one of the accepted Mapper date formats"""
    mapper_formats = (
        "%Y%m%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%d %B %Y",
        "%d %B %y",
        "%d %b %y",
    )
    match = False
    for fmt in mapper_formats:
        try:
            datetime.datetime.strptime(value, fmt)
            match = True
            break
        except ValueError:
            continue

    if not match:
        error(field, "Must use one of the accepted DataMapper date formats")


def has_datamapper_time_format(field, value, error):
    """Validates that the value uses one of the accepted Mapper time formats"""
    mapper_formats = ("%H:%M %p", "%H:%M:%S %p", "%H:%M", "%H:%M:%S", "%H%M%S")
    match = False
    for fmt in mapper_formats:
        try:
            datetime.datetime.strptime(value, fmt)
            match = True
            break
        except ValueError:
            continue

    if not match:
        error(field, "Must use one of the accepted DataMapper time formats")


def does_not_have_char(char):
    """Validation builder that disallows the given character"""

    def _no_char(field, value, error):
        if char in value:
            error(field, f"{char} not allowed")

    return _no_char
