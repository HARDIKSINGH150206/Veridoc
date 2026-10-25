"""Echo code, version chain and plain records (written before the code)."""

import hashlib

import pytest
from hypothesis import given
from hypothesis import strategies as st

from packages.integrity import chain, echo, records
from packages.integrity.canonical import JsonValue, canonical_record

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

DECOMPOSED = "e" + chr(0x301)  # e followed by a combining acute accent


def sha(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


# ---- echo code ----


def independent_code(recap_hash: bytes) -> str:
    digest = sha(b"\x50", recap_hash)
    bits = "".join(f"{byte:08b}" for byte in digest[:3])[:20]
    return "".join(ALPHABET[int(bits[i : i + 5], 2)] for i in range(0, 20, 5))


def test_alphabet_is_crockford_without_i_l_o_u() -> None:
    assert echo.CROCKFORD == ALPHABET
    assert not set("ILOU") & set(echo.CROCKFORD)
    assert len(echo.CROCKFORD) == 32


def test_code_derivation_matches_an_independent_calculation() -> None:
    for seed in (b"a", b"b", b"recap one", "नमस्ते".encode()):
        recap_hash = sha(seed)
        assert echo.derive_echo_code(recap_hash) == independent_code(recap_hash)


def test_code_has_four_alphabet_characters() -> None:
    code = echo.derive_echo_code(sha(b"x"))
    assert len(code) == 4 and set(code) <= set(ALPHABET)


def test_code_uses_the_raw_hash_not_its_hex_text() -> None:
    recap_hash = sha(b"x")
    hex_based = sha(b"\x50", recap_hash.hex().encode())
    assert echo.derive_echo_code(recap_hash) != independent_code_from_digest(hex_based)


def independent_code_from_digest(digest: bytes) -> str:
    bits = "".join(f"{byte:08b}" for byte in digest[:3])[:20]
    return "".join(ALPHABET[int(bits[i : i + 5], 2)] for i in range(0, 20, 5))


def test_recap_hash_must_be_32_bytes() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        echo.derive_echo_code(b"short")


@given(st.binary(min_size=32, max_size=32))
def test_derivation_is_deterministic_and_valid(recap_hash: bytes) -> None:
    code = echo.derive_echo_code(recap_hash)
    assert code == echo.derive_echo_code(recap_hash)
    assert echo.normalize_code(code) == code


def test_one_changed_recap_changes_the_hash_and_almost_always_the_code() -> None:
    codes = {echo.derive_echo_code(records.recap_hash({"text": f"line {i}"})) for i in range(300)}
    assert len(codes) > 250  # 20 bits: a few collisions are expected, not many


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("7f3k", "7F3K"),
        (" 7F3K ", "7F3K"),
        ("7F3k", "7F3K"),
        ("OF3K", "0F3K"),
        ("of3k", "0F3K"),
        ("7FIK", "7F1K"),
        ("7FLK", "7F1K"),
        ("7F3U", None),
        ("7F3", None),
        ("7F3KK", None),
        ("", None),
        ("7F-K", None),
    ],
)
def test_normalize_code_follows_the_spec(raw: str, expected: str | None) -> None:
    assert echo.normalize_code(raw) == expected


# ---- version chain ----


def test_genesis_previous_link_is_32_zero_bytes() -> None:
    assert bytes(32) == chain.GENESIS_LINK


def test_terms_digest_is_a_domain_hash_of_the_canonical_terms_set() -> None:
    terms = [{"key": "price", "value": "4800000"}, {"key": "qty", "value": "200"}]
    assert chain.terms_digest(terms) == sha(b"\x20", canonical_record(terms))


def test_terms_digest_is_independent_of_object_key_order() -> None:
    a = [{"key": "price", "value": "1"}]
    b = [{"value": "1", "key": "price"}]
    assert chain.terms_digest(a) == chain.terms_digest(b)


def test_first_link_uses_the_genesis_value() -> None:
    td, root = sha(b"t0"), sha(b"r0")
    expected = sha(b"\x30", bytes(32), td, root)
    assert chain.chain_link(None, td, root) == expected
    assert chain.chain_link(bytes(32), td, root) == expected


def test_next_link_includes_the_previous_link() -> None:
    link0 = chain.chain_link(None, sha(b"t0"), sha(b"r0"))
    link1 = chain.chain_link(link0, sha(b"t1"), sha(b"r1"))
    assert link1 == sha(b"\x30", link0, sha(b"t1"), sha(b"r1"))


def test_chain_links_builds_all_links_in_order() -> None:
    pairs = [(sha(b"t0"), sha(b"r0")), (sha(b"t1"), sha(b"r1")), (sha(b"t2"), sha(b"r2"))]
    links = chain.chain_links(pairs)
    expected0 = sha(b"\x30", bytes(32), *pairs[0])
    expected1 = sha(b"\x30", expected0, *pairs[1])
    expected2 = sha(b"\x30", expected1, *pairs[2])
    assert links == [expected0, expected1, expected2]
    assert chain.chain_links([]) == []


@given(st.lists(st.tuples(st.binary(min_size=32, max_size=32), st.binary(min_size=32, max_size=32)),
                min_size=2, max_size=12, unique=True), st.data())  # fmt: skip
def test_changing_an_early_entry_changes_every_later_link(
    pairs: list[tuple[bytes, bytes]], data: st.DataObject
) -> None:
    index = data.draw(st.integers(0, len(pairs) - 2))
    new_digest = data.draw(
        st.binary(min_size=32, max_size=32).filter(lambda b: b != pairs[index][0])
    )
    changed = list(pairs)
    changed[index] = (new_digest, pairs[index][1])
    before, after = chain.chain_links(pairs), chain.chain_links(changed)
    assert before[:index] == after[:index]
    assert all(b != a for b, a in zip(before[index:], after[index:], strict=True))


def test_chain_inputs_must_be_32_bytes() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        chain.chain_link(None, b"short", sha(b"r"))
    with pytest.raises(ValueError, match="32 bytes"):
        chain.chain_link(b"short", sha(b"t"), sha(b"r"))


# ---- plain records ----


def test_plain_record_hash_is_prefix_then_canonical_record() -> None:
    record: JsonValue = {"b": DECOMPOSED, "a": 1}
    assert records.plain_record_hash(0x21, record) == sha(b"\x21", canonical_record(record))


def test_recap_receipt_and_import_helpers_use_their_prefixes() -> None:
    record: JsonValue = {"k": "v"}
    assert records.recap_hash(record) == sha(b"\x21", canonical_record(record))
    assert records.receipt_hash(record) == sha(b"\x40", canonical_record(record))
    assert records.import_record_hash(record) == sha(b"\x16", canonical_record(record))


@pytest.mark.parametrize("prefix", [0x10, 0x11, 0x30, 0x50, 0x01, 0x00])
def test_only_plain_record_prefixes_are_allowed(prefix: int) -> None:
    with pytest.raises(ValueError, match="plain record"):
        records.plain_record_hash(prefix, {"k": "v"})


def test_rejected_numbers_propagate_from_record_builders() -> None:
    from packages.integrity.canonical import CanonicalizationError

    with pytest.raises(CanonicalizationError):
        records.recap_hash({"n": 2**60})
