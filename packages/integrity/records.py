"""Plain (unsalted) structural records (docs/INTEGRITY_SPEC.md section 3): H(prefix || JCS(record))
after string normalisation. Pure functions."""

from .canonical import JsonValue, canonical_record
from .hashing import PLAIN_RECORD_PREFIXES, PREFIXES, domain_hash


def plain_record_hash(prefix: int, record: JsonValue) -> bytes:
    """Hash of a plain record type: import record, terms set, recap or receipt."""
    if prefix not in PLAIN_RECORD_PREFIXES:
        raise ValueError(f"prefix {prefix!r} is not a plain record type")
    return domain_hash(prefix, canonical_record(record))


def recap_hash(recap: JsonValue) -> bytes:
    return plain_record_hash(PREFIXES["RECAP"], recap)


def receipt_hash(receipt: JsonValue) -> bytes:
    return plain_record_hash(PREFIXES["RECEIPT"], receipt)


def import_record_hash(import_record: JsonValue) -> bytes:
    return plain_record_hash(PREFIXES["IMPORT_RECORD"], import_record)
