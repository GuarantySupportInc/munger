import csv
import os
from typing import Callable, Iterable
from pathlib import Path

from .munger import Processor


class Writer:
    def __init__(
        self,
        filename: str,
        condition: Callable,
        include_errors: bool,
        use_fieldnames: Iterable = None,
    ):
        self._open_file(filename)
        self._fields_initialized = False
        self._wrote_line = False
        self.condition = condition
        self.include_errors = include_errors
        self.fieldnames = use_fieldnames

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.cleanup()

    def __del__(self):
        self.cleanup()

    def _open_file(self, filename: str) -> None:
        self.file = open(filename, "w")
        # will initialize fieldnames before first write
        self.writer = csv.DictWriter(self.file, fieldnames=[])

    def cleanup(self) -> None:
        if not self.file.closed:
            self.file.close()
        if Path(self.file.name).is_file() and not self._wrote_line:
            os.unlink(self.file.name)

    def write(self, processor: Processor) -> bool:
        """Writes the document to file, according to initialized parameters

        Returns:
            bool - True if the doc was written
        """
        if not self._fields_initialized:
            if self.fieldnames:
                headers = self.fieldnames
            else:
                headers = list(processor.document.keys())
            if self.include_errors:
                headers.append("ValidationErrors")
            self.writer.fieldnames = headers
            self.writer.writeheader()

            self._fields_initialized = True

        output = processor.document.copy()
        if self.include_errors:
            output["ValidationErrors"] = str(processor.errors)

        if self.condition is None:
            self.writer.writerow(output)
            self._wrote_line = True
            return True
        else:
            if self.condition(processor):
                self.writer.writerow(output)
                self._wrote_line = True
                return True

        return False
