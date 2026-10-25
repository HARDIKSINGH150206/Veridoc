"""Version chain (docs/INTEGRITY_SPEC.md section 8). Works on bytes and generic JSON, so it does
not depend on the contract shapes. Pure functions."""

from collections.abc import Sequence

from .canonical import JsonValue, canonical_record
from .hashing import PREFIXES, domain_hash, require_digest

GENESIS_LINK = bytes(32)
"""The previous link of version 1: 32 zero bytes."""


def terms_digest(terms_set: JsonValue) -> bytes:
    """H(0x20 || canonical terms set), after string normalisation."""
    return domain_hash(PREFIXES["TERMS_SET"], canonical_record(terms_set))


def chain_link(prev_link: bytes | None, digest: bytes, root: bytes) -> bytes:
    """link_n = H(0x30 || link_(n-1) || terms_digest_n || root_n); None means version 1."""
    previous = GENESIS_LINK if prev_link is None else require_digest(prev_link, "previous link")
    return domain_hash(
        PREFIXES["CHAIN_LINK"],
        previous,
        require_digest(digest, "terms digest"),
        require_digest(root, "root"),
    )


def chain_links(entries: Sequence[tuple[bytes, bytes]]) -> list[bytes]:
    """All links for a list of (terms_digest, root) pairs, version 1 first."""
    links: list[bytes] = []
    previous: bytes | None = None
    for digest, root in entries:
        previous = chain_link(previous, digest, root)
        links.append(previous)
    return links
