import re
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



class DocumentType(Enum):
    PASSPORT = "Passport".strip().upper()
    COLOMBIAN_ID_CARD = "ID Card"

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+"
PHONE_REGEX = r"\+?[0-9]{7,15}"
class Guest:
    def __init__(self, name: str, email: str, phone_number: str, document_type: DocumentType, document_number: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise DataValidationError("Name must be a non-empty string.")
        if not isinstance(email, str) or not re.fullmatch(EMAIL_REGEX, email.strip()):
            raise DataValidationError("Email must be a valid email address.")
        if not isinstance(phone_number, str) or not re.fullmatch(PHONE_REGEX, phone_number.strip()):   
            raise DataValidationError("Phone number must have a valid format.")
        
        if not isinstance(document_type, DocumentType):
            raise DataValidationError("Invalid document type.")
        if not isinstance(document_number, str) or not document_number.strip():
            raise DataValidationError("Document number must be a non-empty string.")

        self.name = name.strip()
        self.email = email.strip().lower()
        self.phone_number = phone_number.strip()
        self.document_type = document_type
        self.document_number = document_number.strip()
