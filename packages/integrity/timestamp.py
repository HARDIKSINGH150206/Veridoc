"""Timestamps inside hashed records (docs/INTEGRITY_SPEC.md section 4). Pure functions.

The written form is YYYY-MM-DDTHH:MM:SS+HH:MM: whole seconds, the device's own offset kept (no
conversion to UTC), and never Z (a UTC clock is written +00:00). The clock is never read here.
"""

import re
from datetime import datetime, timedelta, timezone


class TimestampError(ValueError):
    """The value cannot be written, or the text is not in the hashed-record form."""


_FORM = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})([+-])([0-9]{2}):([0-9]{2})"
)
_MINUTES_PER_HOUR = 60


def format_timestamp(value: datetime) -> str:
    """Write an aware datetime with whole seconds and a whole-minute offset, offset kept."""
    offset = value.utcoffset()
    if value.tzinfo is None or offset is None:
        raise TimestampError("a timestamp needs an offset")
    if value.microsecond:
        raise TimestampError("a timestamp has whole seconds only")
    if offset.total_seconds() % _MINUTES_PER_HOUR:
        raise TimestampError("the offset must be a whole number of minutes")
    minutes = int(offset.total_seconds()) // _MINUTES_PER_HOUR
    sign = "-" if minutes < 0 else "+"
    hours, rest = divmod(abs(minutes), _MINUTES_PER_HOUR)
    return (
        f"{value.year:04d}-{value.month:02d}-{value.day:02d}"
        f"T{value.hour:02d}:{value.minute:02d}:{value.second:02d}{sign}{hours:02d}:{rest:02d}"
    )


def parse_timestamp(text: str) -> datetime:
    """Read the exact written form. Rejects Z, a missing offset, fractional seconds, -00:00,
    impossible dates and times, and anything else."""
    match = _FORM.fullmatch(text)
    if match is None:
        raise TimestampError("not in the form YYYY-MM-DDTHH:MM:SS+HH:MM")
    year, month, day, hour, minute, second = (int(match.group(i)) for i in range(1, 7))
    sign, offset_hours, offset_minutes = match.group(7), int(match.group(8)), int(match.group(9))
    if offset_hours > 23 or offset_minutes >= _MINUTES_PER_HOUR:
        raise TimestampError("the offset is out of range")
    total = offset_hours * _MINUTES_PER_HOUR + offset_minutes
    if sign == "-" and total == 0:
        raise TimestampError("a zero offset is written +00:00")
    zone = timezone(timedelta(minutes=-total if sign == "-" else total))
    try:
        return datetime(year, month, day, hour, minute, second, tzinfo=zone)
    except ValueError:
        raise TimestampError("not a real date and time") from None
