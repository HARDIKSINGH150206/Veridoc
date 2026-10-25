"""The walking-skeleton screen (issue #32): static checks of the page and its script."""

import re
from html.parser import HTMLParser
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
SCREEN = WEB / "screens" / "skeleton"
HTML = (SCREEN / "index.html").read_text(encoding="utf-8")
SCRIPTS = {p.name: p.read_text(encoding="utf-8") for p in SCREEN.glob("*.js")}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data: str) -> None:
        self.text.append(data)


PAGE = Page()
PAGE.feed(HTML)


def test_page_basics() -> None:
    tags = [t for t, _ in PAGE.tags]
    assert HTML.lstrip().lower().startswith("<!doctype html>")
    assert dict(next(a for t, a in PAGE.tags if t == "html")).get("lang") == "en"
    assert tags.count("h1") == 1 and tags.count("main") == 1 and "<title>" in HTML
    assert any(a.get("name") == "viewport" for t, a in PAGE.tags if t == "meta")
    assert 'class="skip-link"' in HTML and 'href="#main"' in HTML


def test_it_uses_the_shared_stylesheets_and_one_screen_css_file() -> None:
    hrefs = [str(a["href"]) for t, a in PAGE.tags if t == "link" and a.get("rel") == "stylesheet"]
    assert [h.rsplit("/", 1)[-1] for h in hrefs] == [
        "fonts.css", "design-tokens.css", "components.css", "skeleton.css",
    ]  # fmt: skip
    for href in hrefs:
        assert (SCREEN / href).resolve().is_file(), href


def test_nothing_leaves_the_device_and_nothing_is_styled_inline() -> None:
    assert not re.search(r"https?://|//cdn", HTML)
    assert all("style" not in a for _, a in PAGE.tags)
    assert "style" not in [t for t, _ in PAGE.tags]
    scripts = [a for t, a in PAGE.tags if t == "script"]
    assert [a.get("type") for a in scripts] == ["module"]
    assert all(not str(a.get("src")).startswith(("http", "//")) for a in scripts)
    for name, source in SCRIPTS.items():
        assert not re.search(r"https?://", source), name


def test_the_page_says_it_is_demo_data_not_evidence() -> None:
    text = " ".join(PAGE.text).lower()
    assert "demo" in text and "not" in text and "evidence" in text
    assert any("placeholder-banner" in str(a.get("class")) for _, a in PAGE.tags)


def test_buttons_and_inputs_are_accessible() -> None:
    for tag, attrs in PAGE.tags:
        if tag == "button":
            assert attrs.get("type") == "button"
    labels_for = {a["for"] for t, a in PAGE.tags if t == "label" and a.get("for")}
    for tag, attrs in PAGE.tags:
        if tag in {"select", "input", "textarea"}:
            assert attrs.get("id") in labels_for or attrs.get("aria-label"), attrs


def test_the_script_never_turns_chat_text_into_markup() -> None:
    for name, source in SCRIPTS.items():
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            assert banned not in source, f"{name} uses {banned}"


def test_the_script_talks_only_to_the_local_api_path_from_the_page() -> None:
    script = SCRIPTS["skeleton.js"]
    assert "fetch(" in script
    assert 'name="api-base"' in HTML
    assert not re.search(r"""fetch\(\s*['"`]https?:""", script)


def test_a_status_always_has_a_symbol_and_a_word() -> None:
    script = SCRIPTS["skeleton.js"]
    assert "status__symbol" in script and "statusView" in script
