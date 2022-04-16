"""
The gist is that I can write three schemas and feed them into an object and it will handle all the munging at once.
Including writing to different files for different errors.

SCHEMA 1 = Filter schema. Failing validation means it doesn't move on to the others.
SCHEMA 2 = Coercion schema. No validation, so just calls the normalized() method.
SCHEMA 3 = Validation schema. Ensures data conforms to the the target.

registered writers can be passed with conditional functions to check for certain errors and split the writing

Required writers:
    valid_writer -- for a row that makes it through everything

All others optional.

Built-in
    error_writer -- catch-all; writes any row that doesn't go all the way through to validation
    validation_errors_writer -- for rows that fail final validation. includes a validation error description field (maybe? maybe that should go to a tangential log)
    coercion_errors_writer -- this probably represents some unknown case with the source code which caused a coercion function to crash

Ideas
    filtered writer -- catches everything that a filter function would exclude
    changed filenames writer -- hook into post-validation with a conditional to check if Orig_DocumentFileName and DocumentFileName are different, then write to a diff file
    illegal entries writer -- hook into validation failures and look for a specific one to divert

"""
import csv
from enum import Enum, auto
from pathlib import Path

from cerberus import Validator


class MungeFailureException(Exception):
    pass


class Hook(Enum):
    FAILED_FILTER = auto()
    FAILED_COERCION = auto()
    FAILED_VALIDATION = auto()
    VALID = auto()


class Munger:
    """Filters, coerces and validates one document (row of data)"""

    def __init__(self):
        self.hooks = {}
        self.writer_files = []
        self._source_data_initialized = None

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._close_all_files()

    def __del__(self):
        self._close_all_files()

    def _close_all_files(self):
        files = self.writer_files
        if self._source_data_initalized:
            files.append(self.source_file)

        for file in files:
            if not file.closed:
                file.close()

    def set_source_data(self, filename):
        self.source_file = open(filename, "r")
        self.source_reader = csv.DictReader(self.source_file)
        self._source_data_initalized = True

    def register_writer(
        self,
        event,
        filename=None,
        suffix=None,
        condition=None,
        include_errors: bool = False,
    ):
        """Registers a writer to a specific hook to listen for the given condition, if any.

        Arguments:
            event = the Hook to attach to
            filename = full str or Path to file to write to
            suffix = just a suffix to write to
            condition = a function that will be passed the validator object
            include_errors = if True, adds a field ValidationErrors to the end of the writer headers
        """
        # Check for prereqs
        if not self._source_data_initialized:
            raise RuntimeError(
                "Cannot register a writer until source data is intialized"
            )

        if filename is None and suffix is None:
            raise TypeError("filename OR suffix must be given")

        if filename is not None and suffix is not None:
            raise TypeError("Only one of filename or suffix may be given")

        # Initialize the hook
        if event not in self.hooks:
            self.hooks[event] = []

        # Initialize the writer
        if not filename:
            sf_path = Path(self.source_file)
            filename = sf_path.parent / (sf_path.stem + suffix + sf_path.suffix)

        fieldnames = self.source_reader.fieldnames[:]
        if include_errors and event in (
            Hook.FAILED_VALIDATION,
            Hook.FAILED_COERCION,
            Hook.FAILED_FILTER,
        ):
            fieldnames.append("ValidationErrors")

        writer_file = open(filename, "w")
        writer = csv.DictWriter(writer_file, fieldnames=fieldnames)
        self.writer_files.append(writer_file)

        # Register the function
        self.hooks[event].append(
            self._write_func(writer, condition=condition, include_errors=include_errors)
        )

    def _write_func(self, writer, condition=None, include_errors=False):
        def write(validator):
            output = validator.document.copy()
            if include_errors:
                output["ValidationErrors"] = str(validator.document_error_tree)

            if condition is None:
                writer.writerow(output)
            else:
                if condition(validator):
                    writer.writerow(output)

        return write

    def munge(self, data):
        try:
            data = self.filter(data)
            data = self.coerce(data)
            data = self.validate(data)
        except MungeFailureException:
            return None

        return data

    def filter(self, data):
        filtered = self.filterer.validated(data)

        if filtered is None:
            # hook to filter_fail registered callback/writer to output this row
            for func in self.hooks[Hook.FAILED_FILTER]:
                func(self.filterer)

            raise MungeFailureException("Failed during filter")

        return filtered

    def coerce(self, data):
        coerced = self.coercer.normalized(data)

        if coerced is None:
            # hook to coercion_fail registered stuff
            for func in self.hooks[Hook.FAILED_COERCION]:
                func(self.coercer)

            raise MungeFailureException("Failed during coercion")

        return coerced

    def validate(self, data):
        validated = self.validator.validated(data)

        if validated is None:
            for func in self.hooks[Hook.FAILED_VALIDATION]:
                func(self.validator)

            raise MungeFailureException("Failed validation")

        for func in self.hooks[Hook.VALID]:
            func(self.validator)

        return validated


# Usage:
if __name__ == "__main__":
    # from munger import Munger, validation_schemas, hooks

    # create filter schema
    filter_schema = {...}
    # create coercion schema
    coercion_schema = {...}

    m = Munger()

    """
    A schema or validator object must be registered for each step:
    1. Filter -- Strip the source data down to the relevant documents
    2. Coercion -- All the steps of converting the data to the form that you need (defined in validation schema)
    3. Validation -- Compare the coerced data to the validation schema

    Attempting to call munge() will raise an exception if these three are not set.
    """
    m.register_schema("filter", filter_schema)
    m.register_validator("coercion", CustomCoercionValidator(coercion_schema))
    m.register_schema("validation", validation_schemas.UDS_A_RECORD)

    """
    Multiple writers can be registered and attached to various hooks in the munging process.
    Writers can also be registered with a conditional function. If the function returns True,
    the document is written to that registered writer instead of any others.

    (NOTE: Maybe that should be an argument like cascade=False and if it's True then the document can be written with later writers.)

    At minimum a writer must be registered to the hooks.VALID hook, so that fully cleaned and validated data has an outlet.

    Available writer hooks:
    VALID - for rows that made it all the way to the end
    FAILED_FILTER - for rows that were filtered out
    FAILED_COERCION - since there's no validation here, this would be for rows that raise an error with the given coercion functions. Maybe pointless?
    FAILED_VALIDATION - for rows that were coerced but still don't fit the data

    (NOTE: I'd like to include the validator.errors or validator.document_error_tree in the writer for FAILED_VALIDATION.)
    (NOTE: Where is the responsibility for assigning filename, fieldnames, etc? If I add the errors, I feel like the register_writer() function should
        add the error-holding field so it nows where to put them.)

    Can be given either a filename (str or Path) or a suffix. If given suffix, it will be appended to the source file name before the extension.
    """

    # writer for CSV output
    m.register_writer(hook=hooks.VALID, suffix="valid")

    # writer to catalogue validation errors
    m.register_writer(hooks.FAILED_VALIDATION, filename="invalid_items.csv")

    # writer that captures rows that didn't make the filter
    m.register_writer(hooks.FAILED_FILTER, suffix="filtered")

    def has_changed_filename(validator: cerberus.Validator) -> bool:
        return (
            validator.document["Orig_DocumentFileName"]
            != validator.document["DocumentFileName"]
        )

    # writer that diverts valid rows with differing filenames
    m.register_writer(
        hooks.VALID, suffix="file_changed", condition=has_changed_filename
    )

    # assign the input file
    m.source_file = inputfile

    # kick off the full process
    # REQUIRES all mandatory options set or will raise an exception
    m.munge_all()
