"""Layout tests for the static screens S1, S2 and S3 (written before the pages)."""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parent.parent
SCREENS = {
    "s1-deals": "Deals",
    "s2-import": "New deal",
    "s3-workspace": "Placeholder deal",
}
STATUS_WORDS = {
    "clear": "Clear",
    "ambiguous": "Ambiguous",
    "missing": "Missing",
    "conflict": "Conflict",
}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.text: list[str] = []
        self.stack: list[str] = []
        self.status_texts: list[tuple[str, str]] = []
        self._status: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag not in {"meta", "link", "input", "br", "hr", "img"}:
            self.stack.append(tag)
        classes = (a.get("class") or "").split()
        for c in classes:
            if c.startswith("status--"):
                self._status.append(c.removeprefix("status--"))

    def handle_endtag(self, tag: str) -> None:
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._status and data.strip():
            self.status_texts.append((self._status.pop(), data.strip()))


def load(screen: str) -> tuple[str, Page]:
    html = (WEB / "screens" / screen / "index.html").read_text(encoding="utf-8")
    page = Page()
    page.feed(html)
    return html, page


@pytest.mark.parametrize("screen", SCREENS)
def test_page_basics(screen: str) -> None:
    html, page = load(screen)
    assert html.lstrip().lower().startswith("<!doctype html>")
    tags = [t for t, _ in page.tags]
    assert dict(next(a for t, a in page.tags if t == "html")).get("lang") == "en"
    assert tags.count("h1") == 1
    assert tags.count("main") == 1
    assert "<title>" in html
    assert any(a.get("name") == "viewport" for t, a in page.tags if t == "meta")


@pytest.mark.parametrize("screen", SCREENS)
def test_pages_load_fonts_tokens_components_and_their_own_css(screen: str) -> None:
    html, page = load(screen)
    hrefs = [a["href"] for t, a in page.tags if t == "link" and a.get("rel") == "stylesheet"]
    names = [str(h).rsplit("/", 1)[-1] for h in hrefs]
    assert names[:3] == ["fonts.css", "design-tokens.css", "components.css"]
    assert len(names) == 4, "exactly one screen CSS file per screen"
    base = WEB / "screens" / screen
    for href in hrefs:
        assert not str(href).startswith(("http:", "https:", "//"))
        assert (base / str(href)).resolve().is_file(), href


@pytest.mark.parametrize("screen", SCREENS)
def test_pages_are_offline_static_markup(screen: str) -> None:
    html, page = load(screen)
    tags = [t for t, _ in page.tags]
    assert "script" not in tags, "layout only: no JavaScript, no data binding"
    assert "style" not in tags
    assert all("style" not in a for _, a in page.tags), "no inline styles"
    assert "form" not in tags or all(
        a.get("action") in (None, "") for t, a in page.tags if t == "form"
    )
    assert not re.search(r"https?://", html)


@pytest.mark.parametrize("screen", SCREENS)
def test_placeholder_content_is_clearly_marked(screen: str) -> None:
    html, page = load(screen)
    banners = [
        a for t, a in page.tags if a.get("class") and "placeholder-banner" in str(a["class"])
    ]
    assert banners, "a visible banner must say the content is placeholder"
    assert "placeholder" in " ".join(page.text).lower()
    assert any("data-placeholder" in a for _, a in page.tags)


@pytest.mark.parametrize("screen", SCREENS)
def test_accessibility_basics(screen: str) -> None:
    html, page = load(screen)
    assert 'class="skip-link"' in html and 'href="#main"' in html
    ids = {a["id"] for _, a in page.tags if a.get("id")}
    assert "main" in ids
    labels_for = {a["for"] for t, a in page.tags if t == "label" and a.get("for")}
    for t, a in page.tags:
        if t in {"input", "select", "textarea"} and a.get("type") not in {"hidden"}:
            labelled = a.get("id") in labels_for or a.get("aria-label") or a.get("aria-labelledby")
            assert labelled, f"unlabelled {t}: {a}"
        if t == "img":
            assert a.get("alt") is not None
        if t == "button":
            assert a.get("type") in {"button", "submit"}


@pytest.mark.parametrize("screen", SCREENS)
def test_every_status_shows_a_symbol_and_a_word(screen: str) -> None:
    _, page = load(screen)
    if screen != "s2-import":  # the import screen has no statuses
        assert page.status_texts, "this screen shows at least one status"
    for status, text in page.status_texts:
        assert STATUS_WORDS[status] in text, f"status--{status} must contain its word"
    symbols = [a for t, a in page.tags if a.get("class") == "status__symbol"]
    assert len(symbols) == len(page.status_texts)
    assert all(a.get("aria-hidden") == "true" for a in symbols)


def test_the_header_links_connect_the_screens() -> None:
    for screen in SCREENS:
        _, page = load(screen)
        hrefs = {str(a["href"]) for t, a in page.tags if t == "a" and a.get("href")}
        base = WEB / "screens" / screen
        for href in hrefs:
            if href.startswith("#"):
                continue
            assert (base / href).resolve().exists(), f"{screen}: broken link {href}"
        assert any("s1-deals" in h or h.endswith("index.html") for h in hrefs)


def test_s1_has_deals_search_filters_and_new_deal() -> None:
    html, page = load("s1-deals")
    assert "New deal" in html and "Search deals or people" in html
    for tab in ("All", "Needs attention", "Awaiting confirmation", "Confirmed"):
        assert tab in html
    assert [t for t, _ in page.tags].count("progress") >= 3
    assert "stored on this device" in html


def test_s2_has_sources_preview_which_one_is_you_and_the_privacy_line() -> None:
    html, _ = load("s2-import")
    expected = [
        "WhatsApp export", "Paste text", "Simulator", "Clean chat", "Ambiguous chat",
        "Contradictory chat", "Which one is you?", "Supply or order", "Freelance job",
        "Analyse chat", "This chat stays on this device. Nothing is uploaded.",
    ]  # fmt: skip
    for text in expected:
        assert text in html, text
    assert "Step 1 of 2" in html


def test_s3_has_chat_score_terms_and_suggestion() -> None:
    html, page = load("s3-workspace")
    expected = [
        "Evidence strength", "Terms found", "Suggested next message", "Casual", "Polite",
        "Firm", "Use this", "Present", "Clear", "Acknowledged by both", "Send",
    ]  # fmt: skip
    for text in expected:
        assert text in html, text
    kinds = {s for s, _ in page.status_texts}
    assert kinds == set(STATUS_WORDS), "the workspace shows all four status kinds"


def test_components_css_exists_and_uses_status_symbol_tokens() -> None:
    css = (WEB / "components" / "components.css").read_text(encoding="utf-8")
    for status in STATUS_WORDS:
        assert f"var(--status-{status}-symbol)" in css
    assert "focus-visible" in css
