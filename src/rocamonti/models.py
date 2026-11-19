import re
from datetime import date, datetime
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

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+"
PHONE_REGEX = r"\+?[0-9]{7,15}"


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
    PASSPORT = "Passport"
    COLOMBIAN_ID_CARD = "ID Card"


class Guest:
    def __init__(self, name: str, email: str, phone_number: str, document_type: DocumentType, document_number: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise DataValidationError("Name must be a non-empty string.")
        
        if not isinstance(email, str) or not re.fullmatch(EMAIL_REGEX, email.strip()):
            raise DataValidationError("Email must be a valid email address.")
        
        if not isinstance(phone_number, str):   
            raise DataValidationError("Phone number must have a valid format.")
        cleaned_phone = re.sub(r"[ \.\-\(\)]", "", phone_number).strip()
        if not re.fullmatch(PHONE_REGEX, cleaned_phone):
            raise DataValidationError("Phone number must have a valid format.")
        
        if not isinstance(document_type, DocumentType):
            raise DataValidationError("Invalid document type.")
        
        if not isinstance(document_number, str) or not document_number.strip():
            raise DataValidationError("Document number must be a non-empty string.")

        self.name = name.strip()
        self.email = email.strip().lower()
        self.phone_number = cleaned_phone.strip()
        self.document_type = document_type
        self.document_number = document_number.strip().upper()

    @property
    def guest_id(self):
        return f"{self.document_type.name}-{self.document_number}"


class Reservation:
    reservation_counter = 0
    def __init__(self, guest: Guest, room: Room, check_in: date, check_out: date, status=ReservationStatus.CONFIRMED, reservation_id=None):
        if not isinstance(guest, Guest):
            raise DataValidationError("Guest must be a valid Guest instance.")
        if not isinstance(room, Room):
            raise DataValidationError("Room must be a valid Room instance.")
        if not isinstance(check_in, date) or isinstance(check_in, datetime):
            raise DataValidationError("Check-in must be a date.")
        if not isinstance(check_out, date) or isinstance(check_out, datetime):
            raise DataValidationError("Check-out must be a date.")
        if check_out <= check_in:
            raise DataValidationError("Check-out must be after check-in.")
        if not isinstance (status, ReservationStatus):
            raise DataValidationError("Reservation status must be a valid ReservationStatus enum.")    
        
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
       
        self.status = status 

        self._nightly_rate_snapshot = room.nightly_rate

        if  reservation_id is not None:
            if not isinstance(reservation_id, str) or not reservation_id.strip():
                raise DataValidationError("Reservation ID must be a valid string.")
            self._reservation_id = reservation_id.strip()
        else:    
            Reservation.reservation_counter += 1
            self._reservation_id = reservation_id or f"R{Reservation.reservation_counter}"

   
    @property
    def reservation_id(self):
        return self._reservation_id.upper().strip()
    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days
    @property
    def total_cost(self) -> Decimal:
        cost = self._nightly_rate_snapshot * Decimal(self.nights)
        return cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
 

    