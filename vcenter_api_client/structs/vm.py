import enum
from typing import Type
from .exceptions import MissingDataField, InvalidDataTypeField, InvalidFieldValue
from .api_object_class import ApiDataClass


class VMPowerState(enum.Enum):
    POWERED_OFF, POWERED_ON, SUSPENDED = range(3)


class VM(ApiDataClass):
    cpu_count: int | None
    memory_size_MiB: int | None
    name: str
    power_state: int
    vm: str

    def __init__(self, data: dict):
        self._validate_fields(
            self, data, [("name", str), ("power_state", str), ("vm", str)]
        )
        self._validate_fields(
            self, data, [("cpu_count", int), ("memory_size_MiB", int)], False
        )
        match data["power_state"]:
            case "POWERED_OFF":
                self.power_state = VMPowerState.POWERED_OFF
            case "POWERED_ON":
                self.power_state = VMPowerState.POWERED_ON
            case "SUSPENDED":
                self.power_state = VMPowerState.SUSPENDED
            case _:
                raise InvalidFieldValue("Invalid power_state field value")

    @property
    def memory_size_mb(self) -> int | None:
        return self.memory_size_MiB
