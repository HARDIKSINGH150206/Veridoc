"""Integrity primitives: hashing, canonical JSON, Merkle tree, echo code, version chain.

Pure functions only (no I/O, no clock, no randomness). The rules are in docs/INTEGRITY_SPEC.md.
"""

from .canonical import (
    CanonicalizationError,
    JsonValue,
    canonical_record,
    canonicalize,
    normalize_strings,
    normalize_text,
)
from .chain import GENESIS_LINK, chain_link, chain_links, terms_digest
from .echo import CROCKFORD, derive_echo_code, normalize_code
from .hashing import (
    PLAIN_RECORD_PREFIXES,
    PREFIXES,
    SALTED_LEAF_PREFIXES,
    domain_hash,
    export_digest,
    from_hex,
    sha256,
    to_hex,
)
from .merkle import (
    MerkleError,
    ProofStep,
    file_leaf,
    inclusion_proof,
    leaf_hash,
    merkle_root,
    node_hash,
    payload_digest,
    record_leaf,
    verify_inclusion,
)
from .records import import_record_hash, plain_record_hash, recap_hash, receipt_hash
from .timestamp import TimestampError, format_timestamp, parse_timestamp

__all__ = [
    "CROCKFORD",
    "GENESIS_LINK",
    "PLAIN_RECORD_PREFIXES",
    "PREFIXES",
    "SALTED_LEAF_PREFIXES",
    "CanonicalizationError",
    "JsonValue",
    "MerkleError",
    "ProofStep",
    "TimestampError",
    "canonical_record",
    "canonicalize",
    "chain_link",
    "chain_links",
    "derive_echo_code",
    "domain_hash",
    "export_digest",
    "file_leaf",
    "format_timestamp",
    "from_hex",
    "import_record_hash",
    "inclusion_proof",
    "leaf_hash",
    "merkle_root",
    "node_hash",
    "normalize_code",
    "normalize_strings",
    "normalize_text",
    "parse_timestamp",
    "payload_digest",
    "plain_record_hash",
    "receipt_hash",
    "recap_hash",
    "record_leaf",
    "sha256",
    "terms_digest",
    "to_hex",
    "verify_inclusion",
]
