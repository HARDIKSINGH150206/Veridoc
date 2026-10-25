"""Canonical JSON: RFC 8785 examples, normalisation and number rules (written before the code)."""

import json
import struct
import unicodedata
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from packages.integrity import canonical as c
from packages.integrity.canonical import JsonValue

# RFC 8785 section 3.2.2 sample and its canonical form (section 3.2.3), kept as files so that
# no formatter can change the escape sequences inside them.
DATA = Path(__file__).resolve().parent / "data"
RFC_SAMPLE = (DATA / "rfc8785_section_3_2_2_sample.json").read_text(encoding="utf-8")
RFC_CANONICAL = (DATA / "rfc8785_section_3_2_3_canonical.txt").read_text(encoding="utf-8")

# RFC 8785 Appendix B, Table 1 (IEEE 754 bits, expected JSON text).
NUMBER_TABLE = [
    ("0000000000000000", "0"),
    ("8000000000000000", "0"),
    ("0000000000000001", "5e-324"),
    ("8000000000000001", "-5e-324"),
    ("7fefffffffffffff", "1.7976931348623157e+308"),
    ("ffefffffffffffff", "-1.7976931348623157e+308"),
    ("4340000000000000", "9007199254740992"),
    ("c340000000000000", "-9007199254740992"),
    ("4430000000000000", "295147905179352830000"),
    ("44b52d02c7e14af5", "9.999999999999997e+22"),
    ("44b52d02c7e14af6", "1e+23"),
    ("44b52d02c7e14af7", "1.0000000000000001e+23"),
    ("444b1ae4d6e2ef4e", "999999999999999700000"),
    ("444b1ae4d6e2ef4f", "999999999999999900000"),
    ("444b1ae4d6e2ef50", "1e+21"),
    ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"),
    ("3eb0c6f7a0b5ed8d", "0.000001"),
    ("41b3de4355555553", "333333333.3333332"),
    ("41b3de4355555554", "333333333.33333325"),
    ("41b3de4355555555", "333333333.3333333"),
    ("41b3de4355555556", "333333333.3333334"),
    ("41b3de4355555557", "333333333.33333343"),
    ("becbf647612f3696", "-0.0000033333333333333333"),
    ("43143ff3c1cb0959", "1424953923781206.2"),
]  # fmt: skip

DECOMPOSED = "e" + chr(0x301)  # e followed by a combining acute accent
COMPOSED = chr(0xE9)  # the single character e with acute


def test_rfc_8785_section_3_2_2_sample() -> None:
    assert c.canonicalize(json.loads(RFC_SAMPLE)) == RFC_CANONICAL.encode("utf-8")


@pytest.mark.parametrize(("bits", "text"), NUMBER_TABLE)
def test_rfc_8785_appendix_b_number_table(bits: str, text: str) -> None:
    (value,) = struct.unpack(">d", bytes.fromhex(bits))
    assert c.canonicalize([value]) == f"[{text}]".encode()


def test_rfc_8785_property_sorting_uses_utf16_code_units() -> None:
    sample = json.loads(
        '{"\\u20ac": "Euro Sign", "\\r": "Carriage Return",'
        ' "\\ufb33": "Hebrew Letter Dalet With Dagesh",'
        ' "1": "One", "\\ud83d\\ude00": "Emoji: Grinning Face", "\\u0080": "Control",'
        ' "\\u00f6": "Latin Small Letter O With Diaeresis"}'
    )
    out = json.loads(c.canonicalize(sample))
    assert list(out.values()) == [
        "Carriage Return",
        "One",
        "Control",
        "Latin Small Letter O With Diaeresis",
        "Euro Sign",
        "Emoji: Grinning Face",
        "Hebrew Letter Dalet With Dagesh",
    ]


def test_sorting_by_utf16_differs_from_sorting_by_code_point() -> None:
    # Sorting is by UTF-16 code units, not code points: the emoji (surrogate pair starting at
    # 0xD83D) sorts before U+E000 even though its code point is larger.
    private_use, emoji = chr(0xE000), chr(0x1F600)
    out = c.canonicalize({private_use: 1, emoji: 2}).decode()
    assert out.index(emoji) < out.index(private_use)


def test_keys_are_sorted_recursively_and_arrays_keep_order() -> None:
    value: JsonValue = {"b": [{"z": 1, "a": 2}, 3], "a": {"d": 1, "c": 2}}
    assert c.canonicalize(value) == b'{"a":{"c":2,"d":1},"b":[{"a":2,"z":1},3]}'


def test_literals_empty_containers_and_whitespace() -> None:
    value: JsonValue = {"a": [], "b": {}, "c": None, "d": True, "e": False}
    assert c.canonicalize(value) == b'{"a":[],"b":{},"c":null,"d":true,"e":false}'


def test_hindi_and_kannada_text_is_emitted_as_utf8_not_escaped() -> None:
    value: JsonValue = {"text": "नमस्ते दुनिया", "kn": "ನಮಸ್ಕಾರ"}
    assert c.canonicalize(value) == '{"kn":"ನಮಸ್ಕಾರ","text":"नमस्ते दुनिया"}'.encode()


def test_control_and_quote_escapes() -> None:
    assert c.canonicalize('a"b\\c\n\t\x01') == b'"a\\"b\\\\c\\n\\t\\u0001"'


# ---- numbers ----


@pytest.mark.parametrize("value", [2**53, 2**53 + 1, -(2**53), 10**20, -(10**30)])
def test_integers_outside_the_safe_range_are_rejected(value: int) -> None:
    with pytest.raises(c.CanonicalizationError):
        c.canonicalize({"n": value})


@pytest.mark.parametrize("value", [2**53 - 1, -(2**53 - 1), 0, 1, -1])
def test_integers_inside_the_safe_range_are_kept(value: int) -> None:
    assert c.canonicalize([value]) == f"[{value}]".encode()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nan_and_infinity_are_rejected(value: float) -> None:
    with pytest.raises(c.CanonicalizationError):
        c.canonicalize([value])


def test_unsupported_types_are_rejected() -> None:
    for bad in (b"bytes", {1, 2}, object()):
        with pytest.raises(c.CanonicalizationError):
            c.canonicalize(bad)  # type: ignore[arg-type]
    with pytest.raises(c.CanonicalizationError):
        c.canonicalize({1: "non-string key"})  # type: ignore[dict-item]


def test_large_numbers_as_strings_are_kept_exactly() -> None:
    assert c.canonicalize({"paise": "99999999999999999999"}) == b'{"paise":"99999999999999999999"}'


# ---- normalisation (INTEGRITY_SPEC section 2) ----


def test_normalize_text_applies_nfc_and_unix_line_endings() -> None:
    decomposed = DECOMPOSED  # e + combining acute
    assert c.normalize_text(decomposed) == COMPOSED
    assert c.normalize_text("a\r\nb\rc\nd") == "a\nb\nc\nd"


def test_normalize_text_handles_hindi_composition() -> None:
    # Devanagari QA (U+0958) is a composition exclusion: NFC keeps it decomposed (U+0915 U+093C).
    text = chr(0x0958)
    assert c.normalize_text(text) == unicodedata.normalize("NFC", text)
    assert c.normalize_text(text) == chr(0x0915) + chr(0x093C)


def test_normalize_strings_changes_values_but_never_keys() -> None:
    key = DECOMPOSED  # decomposed key must stay decomposed
    value: JsonValue = {key: [DECOMPOSED, {"k": "x\r\ny"}, 5, None, True]}
    out = c.normalize_strings(value)
    assert list(out) == [key] if isinstance(out, dict) else False
    assert out == {key: [COMPOSED, {"k": "x\ny"}, 5, None, True]}


def test_normalize_strings_does_not_change_the_input() -> None:
    value: JsonValue = {"a": [DECOMPOSED]}
    c.normalize_strings(value)
    assert value == {"a": [DECOMPOSED]}


def test_canonicalize_itself_does_not_normalise() -> None:
    assert c.canonicalize(DECOMPOSED) != c.canonicalize(COMPOSED)
    assert c.canonical_record(DECOMPOSED) == c.canonical_record(COMPOSED)


def test_canonical_record_equals_normalise_then_canonicalize() -> None:
    value: JsonValue = {"text": "a\r\n" + DECOMPOSED, "n": 3}
    assert c.canonical_record(value) == c.canonicalize(c.normalize_strings(value))


@given(st.text())
def test_normalize_text_is_idempotent(text: str) -> None:
    once = c.normalize_text(text)
    assert c.normalize_text(once) == once
    assert "\r" not in once


@given(
    st.dictionaries(st.text(max_size=5), st.integers(-1000, 1000), max_size=8),
    st.randoms(use_true_random=False),
)
def test_key_insertion_order_does_not_change_the_output(value: dict[str, int], rnd: object) -> None:
    items = list(value.items())
    rnd.shuffle(items)  # type: ignore[attr-defined]
    assert c.canonicalize(dict(items)) == c.canonicalize(value)
