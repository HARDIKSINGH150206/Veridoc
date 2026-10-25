"""Echo code derivation (docs/INTEGRITY_SPEC.md section 7). Pure functions."""

from .hashing import PREFIXES, domain_hash, require_digest

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
CODE_LENGTH = 4
_ECHO = PREFIXES["ECHO"]
_LOOKALIKES = str.maketrans({"O": "0", "I": "1", "L": "1"})


def derive_echo_code(recap_hash: bytes) -> str:
    """The 4-character code for a recap: the first 20 bits of H(0x50 || recap_hash), five bits per
    Crockford base32 character. recap_hash is the raw 32-byte recap hash, not hex text."""
    digest = domain_hash(_ECHO, require_digest(recap_hash, "recap hash"))
    bits = int.from_bytes(digest[:3], "big") >> 4
    return "".join(CROCKFORD[(bits >> shift) & 31] for shift in (15, 10, 5, 0))


def normalize_code(raw: str) -> str | None:
    """Clean a typed code (trim, upper-case, O to 0, I and L to 1); None if not a valid code."""
    code = raw.strip().upper().translate(_LOOKALIKES)
    if len(code) == CODE_LENGTH and all(char in CROCKFORD for char in code):
        return code
    return None
