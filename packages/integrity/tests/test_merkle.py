"""Leaves, Merkle root, inclusion proofs (written before the code)."""

import hashlib

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from packages.integrity import merkle as m
from packages.integrity.canonical import JsonValue
from packages.integrity.hashing import PREFIXES, sha256

SALT = bytes([1]) * 16

DECOMPOSED = "e" + chr(0x301)  # e followed by a combining acute accent


def sha(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


def node(left: bytes, right: bytes) -> bytes:
    return sha(b"\x01", left, right)


def leaves(count: int) -> list[bytes]:
    return [sha(f"leaf-{i}".encode()) for i in range(count)]


# ---- leaves ----


def test_leaf_hash_follows_the_spec_formula() -> None:
    payload = b"payload"
    digest = sha(payload)
    assert m.payload_digest(payload) == digest
    assert m.leaf_hash(0x10, SALT, digest) == sha(b"\x10", SALT, digest)


def test_salted_leaf_from_a_json_record_normalises_and_canonicalises() -> None:
    record: JsonValue = {"text": DECOMPOSED, "id": 1}
    expected_payload = b'{"id":1,"text":"\xc3\xa9"}'
    assert m.record_leaf(0x10, SALT, record) == sha(b"\x10", SALT, sha(expected_payload))


def test_file_leaf_hashes_the_raw_bytes_without_changes() -> None:
    raw = b"RIFF....\r\n\xff"
    assert m.file_leaf(0x11, SALT, raw) == sha(b"\x11", SALT, sha(raw))


def test_salt_and_prefix_change_the_leaf() -> None:
    digest = sha(b"x")
    base = m.leaf_hash(0x10, SALT, digest)
    assert m.leaf_hash(0x10, bytes([2]) * 16, digest) != base
    assert m.leaf_hash(0x11, SALT, digest) != base


@pytest.mark.parametrize("prefix", [0x01, 0x16, 0x20, 0x21, 0x30, 0x40, 0x50, 0x00, 0x77])
def test_only_salted_leaf_prefixes_may_make_leaves(prefix: int) -> None:
    with pytest.raises(ValueError, match="salted leaf"):
        m.leaf_hash(prefix, SALT, sha(b"x"))


def test_salt_must_be_16_bytes_and_digest_32() -> None:
    with pytest.raises(ValueError, match="salt"):
        m.leaf_hash(0x10, b"short", sha(b"x"))
    with pytest.raises(ValueError, match="digest"):
        m.leaf_hash(0x10, SALT, b"short")


def test_every_salted_prefix_can_make_a_leaf() -> None:
    for name, prefix in PREFIXES.items():
        if name in {"MESSAGE", "VOICE_AUDIO", "TRANSCRIPT_SPAN", "HANDSHAKE_SEAL", "ATTACHMENT",
                    "TERM", "CONFIRMATION"}:  # fmt: skip
            assert len(m.leaf_hash(prefix, SALT, sha(b"x"))) == 32


# ---- root ----


def test_empty_tree_is_rejected() -> None:
    with pytest.raises(m.MerkleError, match="empty"):
        m.merkle_root([])
    with pytest.raises(m.MerkleError):
        m.inclusion_proof([], 0)


def test_single_leaf_root_is_the_leaf_and_proof_is_empty() -> None:
    [only] = leaves(1)
    assert m.merkle_root([only]) == only
    assert m.inclusion_proof([only], 0) == ()
    assert m.verify_inclusion(only, (), only)


def test_two_leaves() -> None:
    a, b = leaves(2)
    assert m.merkle_root([a, b]) == node(a, b)


def test_three_leaves_carry_the_odd_node_up_unchanged() -> None:
    a, b, c = leaves(3)
    assert m.merkle_root([a, b, c]) == node(node(a, b), c)


def test_explicit_shapes_for_four_five_and_seven_leaves() -> None:
    l = leaves(7)  # noqa: E741
    assert m.merkle_root(l[:4]) == node(node(l[0], l[1]), node(l[2], l[3]))
    assert m.merkle_root(l[:5]) == node(node(node(l[0], l[1]), node(l[2], l[3])), l[4])
    assert m.merkle_root(l[:7]) == node(
        node(node(l[0], l[1]), node(l[2], l[3])), node(node(l[4], l[5]), l[6])
    )


def test_odd_nodes_are_never_duplicated() -> None:
    a, b, c = leaves(3)
    assert m.merkle_root([a, b, c]) != node(node(a, b), node(c, c))


def test_leaves_must_be_32_bytes() -> None:
    with pytest.raises(m.MerkleError, match="32 bytes"):
        m.merkle_root([b"short"])


def test_the_input_is_not_modified() -> None:
    items = leaves(5)
    snapshot = list(items)
    m.merkle_root(items)
    m.inclusion_proof(items, 2)
    assert items == snapshot


# ---- proofs ----


def test_proof_for_a_three_leaf_tree() -> None:
    a, b, c = leaves(3)
    assert m.inclusion_proof([a, b, c], 0) == (m.ProofStep(b, "right"), m.ProofStep(c, "right"))
    assert m.inclusion_proof([a, b, c], 1) == (m.ProofStep(a, "left"), m.ProofStep(c, "right"))
    assert m.inclusion_proof([a, b, c], 2) == (m.ProofStep(node(a, b), "left"),)


def test_proof_index_must_be_in_range() -> None:
    for bad in (-1, 3):
        with pytest.raises(m.MerkleError, match="index"):
            m.inclusion_proof(leaves(3), bad)


@pytest.mark.parametrize("count", list(range(1, 18)))
def test_every_proof_verifies_for_every_size_up_to_seventeen(count: int) -> None:
    items = leaves(count)
    root = m.merkle_root(items)
    for index, leaf in enumerate(items):
        assert m.verify_inclusion(leaf, m.inclusion_proof(items, index), root)


def test_wrong_leaf_wrong_root_or_wrong_side_fails() -> None:
    items = leaves(6)
    root = m.merkle_root(items)
    proof = m.inclusion_proof(items, 2)
    assert not m.verify_inclusion(items[3], proof, root)
    assert not m.verify_inclusion(items[2], proof, sha(b"other root"))
    flipped = (m.ProofStep(proof[0].sibling, "left" if proof[0].side == "right" else "right"),
               *proof[1:])  # fmt: skip
    assert not m.verify_inclusion(items[2], flipped, root)
    assert not m.verify_inclusion(items[2], proof[:-1], root)
    assert not m.verify_inclusion(items[2], (*proof, m.ProofStep(sha(b"x"), "right")), root)


def test_verify_inclusion_rejects_malformed_proof_steps_without_raising() -> None:
    items = leaves(4)
    root = m.merkle_root(items)
    assert not m.verify_inclusion(items[0], (m.ProofStep(b"short", "right"),), root)
    assert not m.verify_inclusion(b"short", (), root)


# ---- properties ----

hashes = st.binary(min_size=32, max_size=32)
leaf_lists = st.lists(hashes, min_size=1, max_size=40, unique=True)


@settings(max_examples=150)
@given(leaf_lists, st.data())
def test_changing_any_leaf_changes_the_root(items: list[bytes], data: st.DataObject) -> None:
    index = data.draw(st.integers(0, len(items) - 1))
    replacement = data.draw(hashes.filter(lambda x: x != items[index]))
    changed = list(items)
    changed[index] = replacement
    assert m.merkle_root(changed) != m.merkle_root(items)


@settings(max_examples=150)
@given(st.lists(hashes, min_size=2, max_size=40, unique=True), st.data())
def test_changing_the_order_changes_the_root(items: list[bytes], data: st.DataObject) -> None:
    i = data.draw(st.integers(0, len(items) - 1))
    j = data.draw(st.integers(0, len(items) - 1).filter(lambda x: x != i))
    swapped = list(items)
    swapped[i], swapped[j] = swapped[j], swapped[i]
    assert m.merkle_root(swapped) != m.merkle_root(items)


@settings(max_examples=150)
@given(leaf_lists, st.data())
def test_adding_or_removing_a_leaf_changes_the_root(
    items: list[bytes], data: st.DataObject
) -> None:
    extra = data.draw(hashes.filter(lambda x: x not in items))
    assert m.merkle_root([*items, extra]) != m.merkle_root(items)
    if len(items) > 1:
        assert m.merkle_root(items[:-1]) != m.merkle_root(items)


@settings(max_examples=150)
@given(leaf_lists)
def test_every_inclusion_proof_verifies(items: list[bytes]) -> None:
    root = m.merkle_root(items)
    for index, leaf in enumerate(items):
        assert m.verify_inclusion(leaf, m.inclusion_proof(items, index), root)


@settings(max_examples=150)
@given(st.lists(hashes, min_size=2, max_size=40, unique=True), st.data())
def test_tampered_proofs_fail(items: list[bytes], data: st.DataObject) -> None:
    root = m.merkle_root(items)
    index = data.draw(st.integers(0, len(items) - 1))
    proof = m.inclusion_proof(items, index)
    assert proof, "trees with two or more leaves have non-empty proofs"
    step = data.draw(st.integers(0, len(proof) - 1))
    kind = data.draw(st.sampled_from(["sibling", "side", "drop", "leaf"]))
    if kind == "sibling":
        bad_sibling = bytearray(proof[step].sibling)
        bad_sibling[data.draw(st.integers(0, 31))] ^= 1 << data.draw(st.integers(0, 7))
        tampered = (
            *proof[:step],
            m.ProofStep(bytes(bad_sibling), proof[step].side),
            *proof[step + 1 :],
        )
        assert not m.verify_inclusion(items[index], tampered, root)
    elif kind == "side":
        other = "left" if proof[step].side == "right" else "right"
        tampered = (*proof[:step], m.ProofStep(proof[step].sibling, other), *proof[step + 1 :])  # type: ignore[arg-type]
        assert not m.verify_inclusion(items[index], tampered, root)
    elif kind == "drop":
        assert not m.verify_inclusion(items[index], (*proof[:step], *proof[step + 1 :]), root)
    else:
        wrong = data.draw(hashes.filter(lambda x: x != items[index]))
        assert not m.verify_inclusion(wrong, proof, root)


@given(leaf_lists, st.data())
def test_proof_length_is_at_most_log2_of_the_leaf_count(
    items: list[bytes], data: st.DataObject
) -> None:
    index = data.draw(st.integers(0, len(items) - 1))
    assert len(m.inclusion_proof(items, index)) <= max(0, (len(items) - 1).bit_length())


def test_sha256_helper_is_used_for_nodes() -> None:
    a, b = leaves(2)
    assert m.node_hash(a, b) == sha256(b"\x01" + a + b)
