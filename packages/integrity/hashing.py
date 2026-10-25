"""Hash primitives and domain separation (docs/INTEGRITY_SPEC.md sections 2 and 3).

Pure functions: bytes in, bytes out. No I/O, no clock, no randomness (salts are passed in).
Every hash operand is a raw byte string; hex is for storage and display only.
"""

import hashlib
import re

DIGEST_SIZE = 32
SALT_SIZE = 16

PREFIXES: dict[str, int] = {
    "MERKLE_NODE": 0x01,
    "MESSAGE": 0x10,
    "VOICE_AUDIO": 0x11,
    "TRANSCRIPT_SPAN": 0x12,
    "HANDSHAKE_SEAL": 0x13,
    "ATTACHMENT": 0x14,
    "TERM": 0x15,
    "IMPORT_RECORD": 0x16,
    "TERMS_SET": 0x20,
    "RECAP": 0x21,
    "CONFIRMATION": 0x22,
    "CHAIN_LINK": 0x30,
    "RECEIPT": 0x40,
    "ECHO": 0x50,
}
"""Domain-separation prefix byte per record type. 0x00 is reserved and never used."""

SALTED_LEAF_PREFIXES: frozenset[int] = frozenset(
    PREFIXES[name]
    for name in (
        "MESSAGE",
        "VOICE_AUDIO",
        "TRANSCRIPT_SPAN",
        "HANDSHAKE_SEAL",
        "ATTACHMENT",
        "TERM",
        "CONFIRMATION",
    )
)
"""Records that selective disclosure could hide: salted leaves."""

PLAIN_RECORD_PREFIXES: frozenset[int] = frozenset(
    PREFIXES[name] for name in ("IMPORT_RECORD", "TERMS_SET", "RECAP", "RECEIPT")
)
"""Structural records hashed as H(prefix || canonical JSON), without salt."""

_PREFIX_VALUES = frozenset(PREFIXES.values())
_HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256(data: bytes) -> bytes:
    """SHA-256 of a byte string (32 bytes)."""
    return hashlib.sha256(data).digest()


def check_prefix(prefix: int) -> int:
    """Return the prefix if it is a defined record-type byte, else raise ValueError."""
    if prefix not in _PREFIX_VALUES:
        raise ValueError(f"unknown or reserved domain-separation prefix: {prefix!r}")
    return prefix


def domain_hash(prefix: int, *parts: bytes) -> bytes:
    """H(prefix || part1 || part2 || ...) for a defined prefix byte."""
    check_prefix(prefix)
    for part in parts:
        if not isinstance(part, bytes):
            raise TypeError("hash operands must be bytes")
    return hashlib.sha256(bytes([prefix]).join([b"", b"".join(parts)])).digest()


def export_digest(raw_export: bytes) -> bytes:
    """Digest of the imported export file: plain SHA-256 of the raw bytes, no prefix, no
    normalisation, so `sha256sum` on the original file gives the same value (spec section 4.1)."""
    return sha256(raw_export)


def to_hex(digest: bytes) -> str:
    """Lowercase hex for storage and display."""
    return digest.hex()


def from_hex(text: str) -> bytes:
    """Parse a 64-character lowercase hex hash. Raises ValueError for anything else."""
    if not _HEX64.fullmatch(text):
        raise ValueError("expected 64 lowercase hexadecimal characters")
    return bytes.fromhex(text)


def require_digest(value: bytes, name: str = "value") -> bytes:
    """Return value if it is exactly 32 bytes, else raise ValueError."""
    if not isinstance(value, bytes) or len(value) != DIGEST_SIZE:
        raise ValueError(f"{name} must be {DIGEST_SIZE} bytes")
    return value
