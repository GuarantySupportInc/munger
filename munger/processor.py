from collections.abc import Iterable
import cerberus


class Processor(cerberus.Validator):
    """Base class for Munger Processors.

    Includes commonly needed functionality such as field mapping
    """

    ## How does cerberus parse the schema? I need to hijack that to set up mapping
    def __init__(self, schema, *args, **kwargs):
        self._field_mappings = {}
        schema = self._handle_field_mappings(schema)

        super().__init__(schema, *args, **kwargs)

    def _handle_field_mappings(self, schema):
        for key in schema:
            if not isinstance(schema[key], Iterable):
                raise ValueError("Schema is invalid")

            if "map_to" in schema[key]:
                source_column = key
                target_columns = schema[key]["map_to"]

                if not isinstance(target_columns, str) and not isinstance(
                    target_columns, Iterable
                ):
                    raise ValueError(
                        "map_to value must be string or iterable of strings"
                    )

                if isinstance(target_columns, str):
                    target_columns = [target_columns]

                self._field_mappings[source_column] = target_columns
                del schema[source_column]["map_to"]
                schema[source_column]["rename_handler"] = "map_field"

        return schema

    def _normalize_coerce_map_field(self, field):
        """Copies the field to keys defined in the map_to rule"""
        if field not in self._field_mappings:
            return False

        # first key becomes "main" key which is passed back
        # to Cerberus's built-in renaming function
        main_key = self._field_mappings[field][0]

        # copy to all others
        for key in self._field_mappings[field][1:]:
            self.document[key] = self.document[field]

        # logger.debug(f"copy_fields: Document after renames: {self.document}")
        # rename original to main
        return main_key
