"""Hash primitives: SHA-256 vectors, domain separation, hex helpers (written before the code)."""

import hashlib

import pytest

from packages.integrity import hashing as h


def test_sha256_known_vectors() -> None:
    assert h.sha256(b"").hex() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert (
        h.sha256(b"abc").hex() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    long = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
    assert (
        h.sha256(long).hex() == "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
    )
    assert h.sha256(b"a" * 1_000_000).hex() == (
        "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"
    )


def test_prefix_table_matches_the_spec() -> None:
    expected = {
        "MERKLE_NODE": 0x01, "MESSAGE": 0x10, "VOICE_AUDIO": 0x11, "TRANSCRIPT_SPAN": 0x12,
        "HANDSHAKE_SEAL": 0x13, "ATTACHMENT": 0x14, "TERM": 0x15, "IMPORT_RECORD": 0x16,
        "TERMS_SET": 0x20, "RECAP": 0x21, "CONFIRMATION": 0x22, "CHAIN_LINK": 0x30,
        "RECEIPT": 0x40, "ECHO": 0x50,
    }  # fmt: skip
    assert expected == h.PREFIXES
    assert len(set(h.PREFIXES.values())) == len(h.PREFIXES)
    assert 0x00 not in h.PREFIXES.values(), "0x00 is reserved"


def test_salted_and_plain_prefix_sets_follow_the_spec_rule() -> None:
    assert {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x22} == h.SALTED_LEAF_PREFIXES
    assert {0x16, 0x20, 0x21, 0x40} == h.PLAIN_RECORD_PREFIXES
    assert h.SALTED_LEAF_PREFIXES.isdisjoint(h.PLAIN_RECORD_PREFIXES)


def test_domain_hash_is_sha256_of_prefix_then_parts() -> None:
    data = h.domain_hash(0x21, b"abc", b"def")
    assert data == hashlib.sha256(b"\x21" + b"abc" + b"def").digest()
    assert len(data) == 32


def test_domain_hash_separates_record_types() -> None:
    assert h.domain_hash(0x10, b"x") != h.domain_hash(0x11, b"x")
    assert h.domain_hash(0x10, b"x") != h.sha256(b"x")


@pytest.mark.parametrize("bad", [0x00, 0x02, 0x99, -1, 256])
def test_unknown_or_reserved_prefix_is_rejected(bad: int) -> None:
    with pytest.raises(ValueError, match="prefix"):
        h.domain_hash(bad, b"x")


def test_parts_must_be_bytes() -> None:
    with pytest.raises(TypeError):
        h.domain_hash(0x21, "text")  # type: ignore[arg-type]


def test_export_digest_is_plain_sha256_of_the_raw_bytes() -> None:
    raw = "नमस्ते\r\n".encode() + b"\xff\x00"
    assert h.export_digest(raw) == hashlib.sha256(raw).digest()


def test_hex_helpers_round_trip_and_validate() -> None:
    digest = h.sha256(b"abc")
    text = h.to_hex(digest)
    assert text == text.lower() and len(text) == 64
    assert h.from_hex(text) == digest
    for bad in (text.upper(), text[:-1], "zz" * 32, ""):
        with pytest.raises(ValueError):
            h.from_hex(bad)
