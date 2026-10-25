"""Salted leaves, Merkle root and inclusion proofs (docs/INTEGRITY_SPEC.md sections 5 and 6).

Pure functions. An odd node on a level is carried up unchanged, never duplicated. An empty tree is
rejected. A one-leaf tree has the leaf as its root and an empty proof.
"""

from collections.abc import Sequence
from typing import Literal, NamedTuple

from .canonical import JsonValue, canonical_record
from .hashing import (
    DIGEST_SIZE,
    PREFIXES,
    SALT_SIZE,
    SALTED_LEAF_PREFIXES,
    domain_hash,
    sha256,
)

_NODE = PREFIXES["MERKLE_NODE"]


class MerkleError(ValueError):
    """Invalid input to a Merkle function (empty tree, bad hash length, bad index)."""


class ProofStep(NamedTuple):
    """One sibling hash on the path from a leaf to the root, and the side it is on."""

    sibling: bytes
    side: Literal["left", "right"]


def payload_digest(payload: bytes) -> bytes:
    """H(payload): canonical JSON bytes, or raw file bytes for audio and attachments."""
    return sha256(payload)


def leaf_hash(prefix: int, salt: bytes, digest: bytes) -> bytes:
    """leaf = H(prefix || salt || payload_digest) for a salted-leaf record type."""
    if prefix not in SALTED_LEAF_PREFIXES:
        raise ValueError(f"prefix {prefix!r} is not a salted leaf record type")
    if not isinstance(salt, bytes) or len(salt) != SALT_SIZE:
        raise ValueError(f"salt must be {SALT_SIZE} bytes")
    if not isinstance(digest, bytes) or len(digest) != DIGEST_SIZE:
        raise ValueError(f"payload digest must be {DIGEST_SIZE} bytes")
    return domain_hash(prefix, salt, digest)


def record_leaf(prefix: int, salt: bytes, record: JsonValue) -> bytes:
    """Leaf for a JSON record: normalise strings, canonicalise, digest, then leaf_hash."""
    return leaf_hash(prefix, salt, payload_digest(canonical_record(record)))


def file_leaf(prefix: int, salt: bytes, raw: bytes) -> bytes:
    """Leaf for a file (audio or attachment): the payload is the raw bytes, unchanged."""
    return leaf_hash(prefix, salt, payload_digest(raw))


def node_hash(left: bytes, right: bytes) -> bytes:
    """Inner node: H(0x01 || left || right)."""
    return domain_hash(_NODE, left, right)


def _check_leaves(leaves: Sequence[bytes]) -> None:
    if len(leaves) == 0:
        raise MerkleError("a Merkle tree cannot be empty")
    for leaf in leaves:
        if not isinstance(leaf, bytes) or len(leaf) != DIGEST_SIZE:
            raise MerkleError(f"every leaf must be {DIGEST_SIZE} bytes")


def _next_level(level: Sequence[bytes]) -> list[bytes]:
    paired = [node_hash(level[i], level[i + 1]) for i in range(0, len(level) - 1, 2)]
    if len(level) % 2 == 1:
        paired.append(level[-1])
    return paired


def merkle_root(leaves: Sequence[bytes]) -> bytes:
    """Root of the tree over the leaves, in order."""
    _check_leaves(leaves)
    level = list(leaves)
    while len(level) > 1:
        level = _next_level(level)
    return level[0]


def inclusion_proof(leaves: Sequence[bytes], index: int) -> tuple[ProofStep, ...]:
    """Sibling hashes from the leaf at `index` up to the root, bottom first."""
    _check_leaves(leaves)
    if not 0 <= index < len(leaves):
        raise MerkleError("leaf index out of range")
    proof: list[ProofStep] = []
    level = list(leaves)
    while len(level) > 1:
        if index % 2 == 0:
            if index + 1 < len(level):
                proof.append(ProofStep(level[index + 1], "right"))
        else:
            proof.append(ProofStep(level[index - 1], "left"))
        level = _next_level(level)
        index //= 2
    return tuple(proof)


def verify_inclusion(leaf: bytes, proof: Sequence[ProofStep], root: bytes) -> bool:
    """True if hashing the leaf up through the proof gives the root. Never raises on bad input."""
    if not isinstance(leaf, bytes) or len(leaf) != DIGEST_SIZE:
        return False
    current = leaf
    for step in proof:
        if not isinstance(step.sibling, bytes) or len(step.sibling) != DIGEST_SIZE:
            return False
        if step.side == "left":
            current = node_hash(step.sibling, current)
        elif step.side == "right":
            current = node_hash(current, step.sibling)
        else:
            return False
    return current == root
