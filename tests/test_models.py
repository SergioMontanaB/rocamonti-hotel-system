from decimal import Decimal

import pytest

from rocamonti.exceptions import DataValidationError
from rocamonti.models import Room, RoomType

VALID_RATE = Decimal("150000")


def test_valid_room():
    room = Room(101, RoomType.SINGLE, VALID_RATE)
    assert room.room_number == 101
    assert room.nightly_rate == Decimal("150000.00")


@pytest.mark.parametrize("bad_number", [0, -1, "101", True, 1.5])
def test_invalid_room_number(bad_number):
    with pytest.raises(DataValidationError, match="Room number"):
        Room(bad_number, RoomType.SINGLE, VALID_RATE)


@pytest.mark.parametrize("bad_type", ["Single", None, 1])
def test_invalid_room_type(bad_type):
    with pytest.raises(DataValidationError, match="room type"):
        Room(101, bad_type, VALID_RATE)


@pytest.mark.parametrize(
    "bad_rate",
    [100.0, "100", Decimal("0"), Decimal("-5"), Decimal("0.004"),
     Decimal("NaN"), Decimal("Infinity")],
)
def test_invalid_rate(bad_rate):
    with pytest.raises(DataValidationError, match="rate"):
        Room(101, RoomType.SINGLE, bad_rate)


def test_rate_rounds_half_up():
    assert Room(101, RoomType.SINGLE, Decimal("100.005")).nightly_rate == Decimal("100.01")