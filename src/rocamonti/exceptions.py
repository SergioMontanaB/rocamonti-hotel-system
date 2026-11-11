class HotelError(Exception):
    """Base class for exceptions in this module."""
    
class DataValidationError(HotelError):
    """Exception raised when data validation fails."""

class NotFoundError(HotelError):
    """Exception raised when a requested resource is not found."""

class InvalidTransitionError(HotelError):
    """Exception raised when an invalid state transition is attempted."""

class StorageError(HotelError):
    """Exception raised for errors related to data storage or retrieval."""

class ConflictError(HotelError):
    """Exception raised when there is a conflict in the requested operation"""

class OverlapError(HotelError):
    """Exception raised when there is an overlap in bookings or reservations."""
    
class RoomNotFoundError(HotelError):
    """Exception raised when a requested room is not found."""