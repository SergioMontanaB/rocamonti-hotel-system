from .exceptions import ConflictError, NotFoundError, RoomNotFoundError
from .models import Guest, Reservation, Room


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
