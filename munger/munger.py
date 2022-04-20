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

from tqdm import tqdm

from .processor import Processor
from .writer import Writer


class MungeFailureException(Exception):
    pass


class SchemaType(Enum):
    FILTER = auto()
    COERCE = auto()
    VALIDATE = auto()


class Hook(Enum):
    FAILED_FILTER = auto()
    FAILED_COERCION = auto()
    FAILED_VALIDATION = auto()
    END = auto()


class Munger:
    """Filters, coerces and validates one document (row of data)"""

    def __init__(self):
        # Initialize all Processors to None; all are optional
        self.filterer = None
        self.coercer = None
        self.validator = None

        # for callback functions?
        self.hooks = {hook_type: [] for hook_type in Hook}

        self.writers = {hook_type: [] for hook_type in Hook}
        self._source_data_initialized = None

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._close_all_files()

    def __del__(self):
        self._close_all_files()

    def _close_all_files(self):
        for _, writers in self.writers.items():
            for writer in writers:
                writer.file.close()

        if self._source_data_initialized:
            self.source_file.close()

    def set_source_data(self, filename):
        self.source_filename = filename
        self.source_file = open(filename, "r")
        self.source_reader = csv.DictReader(self.source_file)
        self._source_data_initialized = True

    def set_schema(self, schema_type: SchemaType, schema: dict, **kwargs):
        """Creates a processor of the chosen type using the passed schema

        Arguments:
            schema_type (SchemaType): The kind of Processor to create
            schema (dict): A Cerberus-style schema dict
            **kwargs: All keyword arguments will be passed directly into the Processor constructor
        """
        if schema_type == SchemaType.FILTER:
            self.filterer = Processor(schema, **kwargs)

        elif schema_type == SchemaType.COERCE:
            self.coercer = Processor(schema, **kwargs)

        elif schema_type == SchemaType.VALIDATE:
            self.validator = Processor(schema, **kwargs)

        else:
            raise TypeError(f"Unrecognized schema type: {schema_type}")

    def set_processor(self, schema_type: SchemaType, processor: Processor):
        """Uses the given processor for the selected SchemaType

        Useful if a custom processor is needed for advanced coercions/checks.
        """
        if schema_type == SchemaType.FILTER:
            self.filterer = processor

        elif schema_type == SchemaType.COERCE:
            self.coercer = processor

        elif schema_type == SchemaType.VALIDATE:
            self.validator = processor

        else:
            raise TypeError(f"Unrecognized schema type: {schema_type}")

    def register_writer(
        self,
        event,
        filename=None,
        suffix=None,
        condition=None,
        include_errors: bool = False,
        use_fieldnames: dict = None,
    ):
        """Registers a writer to a specific hook to listen for the given condition, if any.

        Arguments:
            event = the Hook to attach to
            filename = full str or Path to file to write to
            suffix = just a suffix to write to
            condition = a function that will be passed the validator object
            include_errors = if True, adds a field ValidationErrors to the end of the writer headers
            use_fieldnames = if given, these fieldnames will replace the auto-generated fieldnames in the writer
        """
        # Check for prereqs
        if not self._source_data_initialized:
            raise RuntimeError(
                "Cannot register a writer until source data is intialized"
            )

        # TODO give a warning if hooking to an event for a validator type that isn't registered

        if filename is None and suffix is None:
            raise TypeError("filename OR suffix must be given")

        if filename is not None and suffix is not None:
            raise TypeError("Only one of filename or suffix may be given")

        # Initialize the writer
        if not filename:
            sf_path = Path(self.source_filename)
            filename = sf_path.parent / (sf_path.stem + "-" + suffix + sf_path.suffix)

        # only include errors for failure hooks
        include_errors = include_errors and event in (
            Hook.FAILED_VALIDATION,
            Hook.FAILED_COERCION,
            Hook.FAILED_FILTER,
        )
        writer = Writer(
            filename, condition, include_errors, use_fieldnames=use_fieldnames
        )

        self.writers[event].append(writer)

    def munge(self, data):
        # Bool flag to prevent a doc from being written with multiple writers
        # TODO consider a writer option to allow cascading writes
        self._doc_has_been_written = False

        try:
            if self.filterer is not None:
                data = self.filter(data)
                last_used_processor = self.filterer

            if self.coercer is not None:
                data = self.coerce(data)
                last_used_processor = self.coercer

            if self.validator is not None:
                data = self.validate(data)
                last_used_processor = self.validator

        except MungeFailureException:
            return None

        self._run_hooks(Hook.END, last_used_processor)

        return data

    def munge_all(self):
        if all(
            processor is None
            for processor in (self.filterer, self.coercer, self.validator)
        ):
            raise RuntimeError(
                "Must register at least one schema or validator to munge"
            )

        for row in tqdm(self.source_reader, desc="Munging", unit="rows"):
            try:
                data = self.munge(row)
            except MungeFailureException:
                continue

    def filter(self, data):
        filtered = self.filterer.validated(data)

        if filtered is None:
            # hook to filter_fail registered callback/writer to output this row
            self._run_hooks(Hook.FAILED_FILTER, self.filterer)

            raise MungeFailureException("Failed during filter")

        return filtered

    def coerce(self, data):
        coerced = self.coercer.normalized(data)

        if coerced is None:
            # hook to coercion_fail registered stuff
            self._run_hooks(Hook.FAILED_COERCION, self.coercer)

            raise MungeFailureException("Failed during coercion")

        return coerced

    def validate(self, data):
        validated = self.validator.validated(data)

        if validated is None:
            self._run_hooks(Hook.FAILED_VALIDATION, self.validator)

            raise MungeFailureException("Failed validation")

        return validated

    def _run_hooks(self, event: Hook, processor: Processor):
        for func in self.hooks[event]:
            func(processor)

        for writer in self.writers[event]:
            if not self._doc_has_been_written:
                self._doc_has_been_written = writer.write(processor)


# Usage:
if __name__ == "__main__":
    # from munger import Munger, validation_schemas, hooks

    # create filter schema
    filter_schema = {...}
    # create coercion schema
    coercion_schema = {...}

    m = Munger()

    """
    A schema or processor object must be registered for each step:
    1. Filter -- Strip the source data down to the relevant documents
    2. Coercion -- All the steps of converting the data to the form that you need (defined in validation schema)
    3. Validation -- Compare the coerced data to the validation schema

    Attempting to call munge() will raise an exception if these three are not set.
    """
    m.set_schema(SchemaType.FILTER, filter_schema)
    m.register_processor(SchemaType.COERCE, CustomCoercionProcessor(coercion_schema))
    m.set_schema(SchemaType.VALIDATE, schemas.UDS_A_RECORD)

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

    (NOTE: I'd like to include the processor.errors or processor.document_error_tree in the writer for FAILED_VALIDATION.)
    (NOTE: Where is the responsibility for assigning filename, fieldnames, etc? If I add the errors, I feel like the register_writer() function should
        add the error-holding field so it nows where to put them.)

    Can be given either a filename (str or Path) or a suffix. If given suffix, it will be appended to the source file name before the extension.

    Writers connected to the same hook should be defined in order of precedence. eg. If you want a writer to preferentially get lines based on a condition,
    register it before the conditionless writer.

    (NOTE: Maybe I should give an optional priority/weight argument for writers?)
    """

    # writer for CSV output
    m.register_writer(hook=Hook.END, suffix="valid")

    # writer to catalogue validation errors
    m.register_writer(Hook.FAILED_VALIDATION, filename="invalid_items.csv")

    # writer that captures rows that didn't make the filter
    m.register_writer(Hook.FAILED_FILTER, suffix="filtered")

    def has_changed_filename(processor: Processor) -> bool:
        return (
            processor.document["Orig_DocumentFileName"]
            != processor.document["DocumentFileName"]
        )

    # writer that diverts valid rows with differing filenames
    m.register_writer(Hook.END, suffix="file_changed", condition=has_changed_filename)

    # assign the input file
    m.source_file = inputfile

    # kick off the full process
    # REQUIRES all mandatory options set or will raise an exception
    m.munge_all()
