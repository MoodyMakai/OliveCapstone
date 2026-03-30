from datetime import datetime

from src.app import adapt_datetime, convert_datetime


def test_adapt_datetime():
    """Verify that a datetime object is converted to a string in ISO format."""
    dt = datetime(2023, 10, 27, 12, 0, 0)
    iso_str = adapt_datetime(dt)
    assert iso_str == "2023-10-27T12:00:00"


def test_convert_datetime():
    """Verify that an ISO format byte string is converted back to a datetime object."""
    iso_bytes = b"2023-10-27T12:00:00"
    dt = convert_datetime(iso_bytes)
    assert isinstance(dt, datetime)
    assert dt.year == 2023
    assert dt.month == 10
    assert dt.day == 27
    assert dt.hour == 12


def test_convert_datetime_with_microseconds():
    """Verify that an ISO format byte string with microseconds is correctly handled."""
    iso_bytes = b"2023-10-27T12:00:00.123456"
    dt = convert_datetime(iso_bytes)
    assert dt.microsecond == 123456
