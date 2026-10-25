"""Canonical JSON (RFC 8785) and text normalisation (docs/INTEGRITY_SPEC.md sections 2 and 4).

`canonicalize` is pure RFC 8785 through the `rfc8785` library: it normalises nothing.
Record builders call `normalize_strings` first (via `canonical_record`).
"""

import unicodedata
from collections.abc import Mapping, Sequence
from typing import TypeAlias

import rfc8785

JsonValue: TypeAlias = (
    None | bool | int | float | str | Sequence["JsonValue"] | Mapping[str, "JsonValue"]
)
"""Any JSON value. Lists, tuples and mappings are accepted; strings are values, not sequences."""


class CanonicalizationError(ValueError):
    """The value cannot be canonicalised (out-of-range integer, NaN, unsupported type)."""


def canonicalize(value: JsonValue) -> bytes:
    """RFC 8785 canonical UTF-8 bytes of a JSON value.

    Integers outside -(2**53 - 1) .. 2**53 - 1, NaN, infinities, non-string keys and
    non-JSON types are rejected with CanonicalizationError.
    """
    try:
        return rfc8785.dumps(_plain(value))
    except (rfc8785.CanonicalizationError, TypeError, ValueError) as error:
        raise CanonicalizationError(str(error)) from error


def _plain(value: JsonValue) -> JsonValue:
    """Turn tuples and other sequences or mappings into lists and dicts for the library."""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return [_plain(item) for item in value]
    return value


def normalize_text(text: str) -> str:
    """Unicode NFC, then every CRLF and lone CR becomes LF."""
    return unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")


def normalize_strings(value: JsonValue) -> JsonValue:
    """A copy of value with normalize_text applied to every string value. Keys are never changed."""
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, Mapping):
        return {key: normalize_strings(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return [normalize_strings(item) for item in value]
    return value


def canonical_record(value: JsonValue) -> bytes:
    """Canonical bytes of a record: normalize_strings, then canonicalize."""
    return canonicalize(normalize_strings(value))
