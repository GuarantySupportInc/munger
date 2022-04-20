from collections.abc import Iterable
import cerberus


class Processor(cerberus.Validator):
    """Base class for Munger Processors.

    Includes commonly needed functionality such as field mapping
    """

    def _normalize_rename(self, mapping, schema, field):
        """Overriding built-in rename handler to allow lists of fields

        The rule's arguments are validated against this schema:
        {'type': 'hashable'}
        """
        if "rename" in schema[field]:
            target_fields = schema[field]["rename"]
            if isinstance(target_fields, str):
                mapping[target_fields] = mapping[field]
                del mapping[field]
            elif isinstance(target_fields, Iterable):
                for target_field in target_fields:
                    mapping[target_field] = mapping[field]
                if field not in target_fields:
                    del mapping[field]
            else:
                raise ValueError("Rename only accepts a string or iterable of strings")
