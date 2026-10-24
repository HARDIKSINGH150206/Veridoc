"""Tests for apps/api/main.py: router auto-discovery (ADR-022). Written before the code."""

import importlib
import sys
import textwrap
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from apps.api import main as api_main
from apps.api.main import RouterLoadError, create_app, discover_routers
from apps.api.settings import Settings

ROUTER_TEMPLATE = """
from fastapi import APIRouter, FastAPI

router = APIRouter()


@router.get("/{path}")
def {path}() -> dict[str, str]:
    return {{"name": "{path}"}}
"""


@pytest.fixture
def routers_pkg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """An importable package of routers that tests can add files to."""
    pkg = tmp_path / "fake_routers"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))
    yield pkg
    for name in [n for n in sys.modules if n == "fake_routers" or n.startswith("fake_routers.")]:
        del sys.modules[name]


def add_router(pkg: Path, name: str) -> None:
    (pkg / f"{name}.py").write_text(textwrap.dedent(ROUTER_TEMPLATE.format(path=name)))
    importlib.invalidate_caches()


def paths(app: FastAPI) -> set[str]:
    """All URL paths of the app, read from its OpenAPI description."""
    return set(app.openapi()["paths"])


def test_real_placeholder_routers_still_load_and_the_app_starts() -> None:
    app = create_app(Settings())
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200


def test_placeholder_modules_without_a_router_are_skipped(routers_pkg: Path) -> None:
    (routers_pkg / "empty.py").write_text("# Placeholder only. No code yet.\n")
    assert discover_routers("fake_routers") == []


def test_a_new_router_file_is_picked_up_without_editing_main(routers_pkg: Path) -> None:
    add_router(routers_pkg, "alpha")
    first = create_app(Settings(), routers_package="fake_routers")
    assert "/api/alpha" in paths(first)
    add_router(routers_pkg, "beta")
    second = create_app(Settings(), routers_package="fake_routers")
    assert {"/api/alpha", "/api/beta"} <= paths(second)
    with TestClient(second) as client:
        assert client.get("/api/beta").json() == {"name": "beta"}


def test_discovery_order_is_alphabetical_and_skips_underscore_modules(routers_pkg: Path) -> None:
    for name in ("zeta", "alpha", "_private"):
        add_router(routers_pkg, name)
    assert [name for name, _ in discover_routers("fake_routers")] == ["alpha", "zeta"]


def test_a_broken_router_module_is_reported_by_name(routers_pkg: Path) -> None:
    (routers_pkg / "broken.py").write_text("raise RuntimeError('boom')\n")
    with pytest.raises(RouterLoadError, match="fake_routers.broken"):
        create_app(Settings(), routers_package="fake_routers")


def test_a_router_attribute_of_the_wrong_type_is_reported(routers_pkg: Path) -> None:
    (routers_pkg / "wrong.py").write_text("router = 'not a router'\n")
    with pytest.raises(RouterLoadError, match="fake_routers.wrong"):
        discover_routers("fake_routers")


def test_main_does_not_import_any_router_module_by_name() -> None:
    source = Path(api_main.__file__).read_text(encoding="utf-8")
    for name in ("ingest", "agreement", "analysis", "vault", "export"):
        assert f"routers.{name}" not in source
        assert f"import {name}" not in source


def test_settings_are_stored_on_the_app_and_drive_health(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(safe_mode=True, demo_mode=True)
    app = create_app(settings)
    assert app.state.settings is settings
    with TestClient(app) as client:
        body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["safe_mode"] is True
    assert body["demo_mode"] is True
    assert body["router_count"] >= 0


def test_the_app_listens_only_on_the_loopback_interface() -> None:
    assert Settings().host == "127.0.0.1"


def test_a_router_object_is_an_api_router(routers_pkg: Path) -> None:
    add_router(routers_pkg, "gamma")
    [(name, router)] = discover_routers("fake_routers")
    assert name == "gamma" and isinstance(router, APIRouter)
