# Business rules (v1)

This document defines the rules that `Rocamonti-Hotel-System` must enforce. Every rule here
should have at least one test in `tests/test_hotel.py`.

## 1. Dates and nights

- A reservation covers **nights**, not days. `check_in` is the arrival date
  and `check_out` is the departure date.
- `check_out` must be strictly after `check_in` (minimum one night).
- Number of nights = `check_out - check_in` in days.
- Total cost = nightly rate at booking time x number of nights.
  The rate is copied when the reservation is created, so later price changes
  do not alter existing reservations.
- A new reservation cannot start in the past: `check_in >= today`.
  This is validated in `Hotel`, not in `Reservation`, so that old reservations
  can still be loaded from storage.

## 2. Overlap rule

Two reservations conflict only if they are for the **same room** and both are
**not cancelled**, and their night ranges intersect:

```
new.check_in < existing.check_out  AND  existing.check_in < new.check_out
```

The range is half-open: the departure day is not an occupied night.
A guest can arrive on the same day another guest departs (same-day turnover).

### Test cases

Existing reservation: room 101, **June 10 -> June 15**, status CONFIRMED.

| # | New reservation (room 101)       | Situation                        | Overlap? |
|---|----------------------------------|----------------------------------|----------|
| 1 | June 5 -> June 12                | Overlaps the start               | Yes      |
| 2 | June 13 -> June 20               | Overlaps the end                 | Yes      |
| 3 | June 11 -> June 14               | Fully inside the existing one    | Yes      |
| 4 | June 8 -> June 18                | Fully contains the existing one  | Yes      |
| 5 | June 10 -> June 15               | Identical dates                  | Yes      |
| 6 | June 5 -> June 10                | Departs the day the other arrives| No       |
| 7 | June 15 -> June 20               | Arrives the day the other departs| No       |
| 8 | June 1 -> June 5                 | Completely before                | No       |
| 9 | June 16 -> June 20               | Completely after                 | No       |
| 10| June 10 -> June 15, room 102     | Same dates, different room       | No       |
| 11| June 10 -> June 15, room 101     | Existing one is CANCELLED        | No       |

## 3. Reservation states

States: `CONFIRMED`, `CHECKED_IN`, `CHECKED_OUT`, `CANCELLED`.
A new reservation starts as `CONFIRMED`.

| From \ To       | CONFIRMED | CHECKED_IN | CHECKED_OUT | CANCELLED |
|-----------------|-----------|------------|-------------|-----------|
| **CONFIRMED**   | -         | Allowed    | Not allowed | Allowed   |
| **CHECKED_IN**  | Not allowed | -        | Allowed     | Not allowed |
| **CHECKED_OUT** | Not allowed | Not allowed | -        | Not allowed |
| **CANCELLED**   | Not allowed | Not allowed | Not allowed | -       |

Notes:
- A reservation cannot be cancelled after check-in.
- `CHECKED_OUT` and `CANCELLED` are final states.
- Any other transition raises `InvalidTransitionError`.
- v1 does not restrict check-in/check-out by calendar date.
  (Decision: reception decides the real arrival and departure.)

## 4. Identity

- Room: identified by `room_number`. Duplicates are not allowed.
- Guest: identified by `guest_id` (`DOCUMENT_TYPE-DOCUMENT_NUMBER`).
  Duplicates are not allowed.
- Reservation: identified by an integer `reservation_id` assigned by `Hotel`
  (1, 2, 3, ...). Cancel, check-in and check-out use this id.

## 5. Errors

| Situation                                             | Exception                  |
|-------------------------------------------------------|----------------------------|
| Invalid data (types, formats, dates out of order)     | `DataValidationError`      |
| Check-in date in the past (new reservation)           | `DataValidationError`      |
| Room, guest or reservation does not exist             | `NotFoundError` (`RoomNotFoundError` for rooms) |
| Duplicate room or guest                               | `ConflictError`            |
| Dates overlap with another active reservation         | `OverlapError`             |
| Invalid state change                                  | `InvalidTransitionError`   |
| File read/write or corrupt JSON                       | `StorageError`             |

## 6. Order of checks when creating a reservation

1. Guest exists.
2. Room exists.
3. Dates are valid and `check_in >= today`.
4. Room is available for the date range.
5. Create the reservation, assign its id, store it.