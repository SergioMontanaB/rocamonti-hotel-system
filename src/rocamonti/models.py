from decimal import ROUND_HALF_UP, Decimal
from enum import Enum

from .exceptions import DataValidationError


class ReservationStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    CHECKED_IN = "Checked In"
    CHECKED_OUT = "Checked Out"


class RoomType(Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    APARTMENT = "Apartment"
    FAMILY = "Family"


class Room:
    def __init__(self, room_number: int, room_type: RoomType, nightly_rate: Decimal) -> None:
        if not isinstance(room_number, int) or isinstance(room_number, bool):
            raise DataValidationError("Room number must be an integer.")
        if room_number <= 0:
            raise DataValidationError("Room number must be positive.")
        if not isinstance(room_type, RoomType):
            raise DataValidationError("Invalid room type.")
        if not isinstance(nightly_rate, Decimal):
            raise DataValidationError("Nightly rate must be a Decimal.")
        if not nightly_rate.is_finite():
            raise DataValidationError("Nightly rate must be a finite number.")

        rate = nightly_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rate <= 0:
            raise DataValidationError("Nightly rate must be positive.")

        self.room_number = room_number
        self.room_type = room_type
        self.nightly_rate = rate