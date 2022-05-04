"""Common coercer functions"""
from pathlib import Path
from typing import Callable

import pendulum

## Text operations
def upper(value: str) -> str:
    """Coercer that capitalizes value"""
    return value.upper()


def truncate(maxlength: int):
    """Coercer builder that truncates a string to the given maxlength"""

    def trunc(value: str) -> str:
        return value[0:maxlength]

    return trunc


## Date operations
def datetime_to_format(format: str) -> Callable:
    """Coercer builder that takes a format and returns a datetime coercion function"""

    def formatter(datetime: str) -> str:
        dt = pendulum.parse(datetime, strict=False)
        return dt.format(format)

    return formatter


## Path/filename operations
def relative_to_folder(path: str) -> Callable:
    """Coercer builder that gets the path relative to the passed folder

    In other words, removes earlier folders from the path.
    """

    def _relative_to_folder(value: str) -> str:
        p = Path(value)
        return str(p.relative_to(path))

    return _relative_to_folder


def get_parent_folder(path: str) -> str:
    """Coercer that removes the filename from the DocumentPath"""
    p = Path(path)
    p = p.parent
    return str(p)


def get_filename(value: str) -> str:
    """Coercer that extracts the filename from a given path string"""
    p = Path(value)
    return p.name


def insert_base_folder(folder_name: str) -> Callable:
    """Coercer builder to insert a target base folder"""

    def _insert_base_folder(value: str) -> str:
        p = Path(value)
        return str(folder_name / p)

    return _insert_base_folder


def extract_file_ext(value: str) -> str:
    """Coercer that extracts the file type from a filename"""
    filetype = Path(value).suffix[1:].upper()
    return filetype


def to_uds_path(path: str) -> str:
    """Coercer that delimits paths with backslashes and bookends with backslashes"""
    path = path.replace("/", "\\")
    if path[0] != "\\":
        path = "\\" + path

    if path[-1] != "\\":
        path = path + "\\"

    return path
