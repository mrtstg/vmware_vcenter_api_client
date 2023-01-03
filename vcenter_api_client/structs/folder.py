import enum
from typing import Type
from .exceptions import InvalidFieldValue
from .api_object_class import ApiDataClass


class FolderType(enum.Enum):
    DATACENTER, DATASTORE, HOST, NETWORK, VIRTUAL_MACHINE = range(5)


class Folder(ApiDataClass):
    folder: str
    name: str
    type: int

    def __init__(self, data: dict):
        self._validate_fields(
            self, data, [("folder", str), ("name", str), ("type", str)]
        )
        match data["type"]:
            case "DATACENTER":
                self.type = FolderType.DATACENTER
            case "DATASTORE":
                self.type = FolderType.DATASTORE
            case "HOST":
                self.type = FolderType.HOST
            case "NETWORK":
                self.type = FolderType.NETWORK
            case "VIRTUAL_MACHINE":
                self.type = FolderType.VIRTUAL_MACHINE
            case _:
                raise InvalidFieldValue("Invalid type field value")
