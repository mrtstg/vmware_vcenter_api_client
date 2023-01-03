from .exceptions import *
from typing import Type


class ApiDataClass:
    @staticmethod
    def _validate_fields(
        obj, data: dict, fields: list[tuple[str, Type]], raise_missing: bool = True
    ):
        for field, field_type in fields:
            if field not in data:
                if raise_missing:
                    raise MissingDataField("Missing %s required attribute!" % field)
                else:
                    setattr(obj, field, None)

            if not isinstance(data[field], field_type):
                raise InvalidDataTypeField(
                    "Field %s must have %s type!", field, field_type
                )

            setattr(obj, field, data[field])
