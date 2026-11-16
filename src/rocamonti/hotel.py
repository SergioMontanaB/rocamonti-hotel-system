from .exceptions import ConflictError, NotFoundError, RoomNotFoundError
from .models import Guest, Reservation, Room


class Hotel:
    def __init__(self) -> None:
        self._rooms: dict[int, Room] = {}
        self._guests: dict[str, Guest] = {}
        self._reservations: list[Reservation] = []

    def add_room(self, room: Room) -> Room:
        if room.number in self._rooms:
            raise ConflictError("Room exists")
        self._rooms[room.number] = room
        return room

    def get_room(self, number: int) -> Room:
        if number not in self._rooms:
            raise RoomNotFoundError()
        return self._rooms[number]

    def register_guest(self, guest: Guest) -> Guest:
        if guest.id in self._guests:
            raise ConflictError("Guest exists")
        self._guests[guest.id] = guest
        return guest

    def get_guest(self, guest_id: str) -> Guest:
        if guest_id not in self._guests:
            raise NotFoundError("Guest not found")
        return self._guests[guest_id]

    def list_all_guests(self) -> list[Guest]:
        return list(self._guests.values())