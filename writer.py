import csv
from typing import Callable

from munger import Processor


class Writer:
    def __init__(self, filename: str, condition: Callable, include_errors: bool):
        self._open_file(filename)
        self.condition = condition
        self.include_errors = include_errors

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.file.close()

    def __del__(self):
        self.file.close()

    def _open_file(self, filename: str):
        self.file = open(filename, "w")
        # will initialize fieldnames before first write
        self.writer = csv.DictWriter(self.file, fieldnames=[])
        self._fields_intialized = False

    def write(self, processor: Processor):
        if not self._fields_initialized:
            headers = list(processor.document.keys())
            if self.include_errors:
                headers.append("ValidationErrors")
            self.writer.fieldnames = headers
            self.writer.writeheader()

        output = processor.document.copy()
        if self.include_errors:
            output["ValidationErrors"] = str(processor.errors)

        if self.condition is None:
            self.writer.writerow(output)
            # self._doc_has_been_written = True
        else:
            if self.condition(processor):
                self.writer.writerow(output)
                # self._doc_has_been_written = True
