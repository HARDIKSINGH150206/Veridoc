"""Hashed-record timestamps: YYYY-MM-DDTHH:MM:SS+HH:MM, never Z (INTEGRITY_SPEC section 4)."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from packages.integrity import TimestampError, format_timestamp, parse_timestamp


def at(offset_minutes: int, *parts: int) -> datetime:
    return datetime(*parts, tzinfo=timezone(timedelta(minutes=offset_minutes)))  # type: ignore[arg-type,misc]


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (at(330, 2026, 9, 1, 14, 0, 0), "2026-09-01T14:00:00+05:30"),
        (at(0, 2026, 9, 1, 14, 0, 0), "2026-09-01T14:00:00+00:00"),
        (at(-210, 2026, 9, 1, 14, 0, 0), "2026-09-01T14:00:00-03:30"),
        (at(330, 2028, 2, 29, 23, 59, 59), "2028-02-29T23:59:59+05:30"),
        (at(330, 2026, 1, 1, 0, 0, 0), "2026-01-01T00:00:00+05:30"),
        (at(-720, 2026, 12, 31, 23, 59, 59), "2026-12-31T23:59:59-12:00"),
        (at(840, 2026, 6, 1, 0, 0, 0), "2026-06-01T00:00:00+14:00"),
    ],
)
def test_format_keeps_the_offset_and_round_trips(value: datetime, text: str) -> None:
    assert format_timestamp(value) == text
    parsed = parse_timestamp(text)
    assert parsed == value and parsed.utcoffset() == value.utcoffset()


def test_utc_is_written_plus_zero_never_z() -> None:
    text = format_timestamp(datetime(2026, 9, 1, 8, 30, 0, tzinfo=UTC))
    assert text == "2026-09-01T08:30:00+00:00" and "Z" not in text


def test_format_does_not_convert_to_utc() -> None:
    assert format_timestamp(at(330, 2026, 9, 1, 1, 0, 0)) == "2026-09-01T01:00:00+05:30"


def test_naive_datetimes_are_rejected() -> None:
    with pytest.raises(TimestampError):
        format_timestamp(datetime(2026, 9, 1, 14, 0, 0))


def test_fractional_seconds_are_rejected() -> None:
    with pytest.raises(TimestampError):
        format_timestamp(datetime(2026, 9, 1, 14, 0, 0, 1, tzinfo=UTC))


def test_an_offset_that_is_not_whole_minutes_is_rejected() -> None:
    odd = datetime(2026, 9, 1, tzinfo=timezone(timedelta(hours=5, seconds=30)))
    with pytest.raises(TimestampError):
        format_timestamp(odd)


@pytest.mark.parametrize(
    "text",
    [
        "2026-09-01T14:00:00Z",
        "2026-09-01T14:00:00z",
        "2026-09-01T14:00:00",
        "2026-09-01T14:00:00.5+05:30",
        "2026-09-01T14:00:00.000+05:30",
        "2026-09-01T14:00+05:30",
        "2026-09-01 14:00:00+05:30",
        "2026-09-01T14:00:00+0530",
        "2026-09-01T14:00:00+05",
        "2026-09-01T14:00:00-00:00",
        "2026-09-01T14:00:00+24:00",
        "2026-09-01T14:00:00+05:60",
        "2026-09-01T24:00:00+05:30",
        "2026-09-01T14:00:60+05:30",
        "2026-02-29T14:00:00+05:30",
        "2026-13-01T14:00:00+05:30",
        "2026-09-01T14:00:00+05:30\n",
        " 2026-09-01T14:00:00+05:30",
        "٢٠٢٦-09-01T14:00:00+05:30",
        "26-09-01T14:00:00+05:30",
        "",
    ],
)
def test_parse_rejects_anything_but_the_exact_format(text: str) -> None:
    with pytest.raises(TimestampError):
        parse_timestamp(text)


def test_timestamp_error_is_a_value_error() -> None:
    assert issubclass(TimestampError, ValueError)
