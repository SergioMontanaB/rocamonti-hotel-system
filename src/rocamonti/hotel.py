from datetime import date

from .exceptions import (
    ConflictError,
    DataValidationError,
    NotFoundError,
    RoomNotFoundError,
)
from .models import Guest, Reservation, ReservationStatus, Room


class Hotel:
    def __init__(self) -> None:
        self._rooms: dict[int, Room] = {}
        self._guests: dict[str, Guest] = {}
        self._reservations: list[Reservation] = []
        self._next_id = 1

    def add_room(self, room: Room) -> Room:
        if room.room_number in self._rooms:
            raise ConflictError(f"Room {room.room_number} exists")
        self._rooms[room.room_number] = room
        return room

    def get_room(self, number: int) -> Room:
        if number not in self._rooms:
            raise RoomNotFoundError(f"Room {number} not found")
        return self._rooms[number]

    def register_guest(self, guest: Guest) -> Guest:
        if guest.guest_id in self._guests:
            raise ConflictError(f"Guest {guest.guest_id} already exists")
        self._guests[guest.guest_id] = guest
        return self._guests[guest.guest_id]

    def get_guest(self, guest_id: str) -> Guest:
        if guest_id not in self._guests:
            raise NotFoundError(f"Guest {guest_id} not found")
        return self._guests[guest_id]

    def list_all_guests(self) -> list[Guest]:
        return list(self._guests.values())

    def list_all_rooms(self) -> list[Room]:
        return list(self._rooms.values())

    def _generate_reservation_id(self) -> str:
        reservation_id = f"R{self._next_id}"
        self._next_id += 1
        return reservation_id

    def is_room_available(
        self, room_number: int, check_in: date, check_out: date
    ) -> bool:
        if check_in >= check_out:
            raise DataValidationError("Check-in must be before check-out")

        self.get_room(room_number)
        for r in self._reservations:
            if (
                r.room.room_number == room_number
                and r.status != ReservationStatus.CANCELLED
                and check_in < r.check_out
                and r.check_in < check_out
            ):
                return False
        return True
