from datetime import date
from decimal import Decimal, ROUND_HALF_UP

class Room:
    def __init__(self, room_number, room_type, nightly_rate):
        if not nightly_rate.is_finite():
            raise ValueError("Nightly rate must be a finite number.")
        
        if nightly_rate <= 0:
            raise ValueError("Nightly rate must be greater than zero.")
        
        
        
        if not isinstance(room_number, int) or isinstance(room_number, bool) or room_number <= 0:
            raise ValueError("Room number must be a positive integer.")
        
        self.room_number = room_number
        self.room_type = room_type

        self.nightly_rate = Decimal(str(nightly_rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class Guest:
    def __init__(self, guest_id, name, email):
        self.guest_id = guest_id
        self.name = name
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Invalid email address.")
        self.email = email  
        

class Reservation:
    def __init__(self, reservation_id, guest, room, check_in_date, check_out_date):
        if not isinstance(check_in_date, date) or not isinstance(check_out_date, date):
            raise TypeError("Check-in and check-out dates must be of type 'date'.")
        if check_in_date >= check_out_date:
            raise ValueError("Check-in date must be before check-out date.")

        self.reservation_id = reservation_id
        self.guest = guest
        self.room = room
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date

    @property
    def duration(self):
        return (self.check_out_date - self.check_in_date).days

    @property
    def total_cost(self):
        cost = self.room.nightly_rate * self.duration
        return cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


