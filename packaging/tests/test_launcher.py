"""Windows launcher checks for #15: NFR-PERF-001, NFR-PORT-001, NFR-SEC-004."""

import asyncio
import http.client
import importlib.util
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uvicorn import Config, Server

from apps.api.main import create_app
from apps.api.settings import Settings

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def isolate_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    for name in os.environ:
        if name.startswith("VERIDOC_"):
            monkeypatch.delenv(name)


@pytest.fixture
def launcher() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "veridoc_launcher", ROOT / "packaging/launcher.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def settings() -> Settings:
    return Settings(port=None)


def test_mount_keeps_api_and_bundled_assets_available(launcher: ModuleType) -> None:
    app = create_app(Settings())
    launcher.mount_ui(app, ROOT / "apps/web")
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        assert "Deals - VeriDoc" in client.get(launcher.UI_ENTRY).text
        assert client.get("/ui/assets/design-tokens.css").status_code == 200
        assert client.get("/ui/../.env").status_code == 404
        assert client.get("/ui/%2e%2e/%2e%2e/pyproject.toml").status_code == 404


def test_missing_ui_fails_before_startup(launcher: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        launcher.mount_ui(FastAPI(), tmp_path)


def test_dynamic_port_is_loopback_and_released(launcher: ModuleType, settings: Settings) -> None:
    with launcher.bind_listener(settings) as listener:
        host, port = listener.getsockname()
        assert host == settings.host
        assert port > 0
    assert listener.fileno() == -1


def test_configured_port_is_honoured(launcher: ModuleType, settings: Settings) -> None:
    with launcher.bind_listener(settings) as probe:
        port = probe.getsockname()[1]
    settings.port = port
    with launcher.bind_listener(settings) as listener:
        assert listener.getsockname()[1] == port


def test_busy_port_is_not_silently_replaced(launcher: ModuleType, settings: Settings) -> None:
    with launcher.bind_listener(settings) as occupied:
        occupied.listen()
        settings.port = occupied.getsockname()[1]
        with pytest.raises(OSError), launcher.bind_listener(settings):
            pytest.fail("A second launcher must not take an occupied port")


@pytest.mark.parametrize("port", [-1, 65536])
def test_invalid_port_fails_clearly(launcher: ModuleType, port: int) -> None:
    with pytest.raises(ValueError, match="port"), launcher.bind_listener(Settings(port=port)):
        pytest.fail("Invalid ports must be rejected")


@pytest.mark.parametrize("browser_fails", [False, True])
def test_browser_opens_after_real_startup_and_server_shuts_down(
    launcher: ModuleType, settings: Settings, browser_fails: bool
) -> None:
    opened: list[str] = []
    notices: list[str] = []
    app = create_app(settings)
    launcher.mount_ui(app, ROOT / "apps/web")

    async def exercise() -> None:
        with launcher.bind_listener(settings) as listener:
            port = listener.getsockname()[1]
            ready = asyncio.Event()

            def open_browser(url: str) -> bool:
                assert server.started
                opened.append(url)
                ready.set()
                if browser_fails:
                    raise OSError("private fixture content must not be printed")
                return True

            server = launcher.BrowserServer(
                Config(app, host=settings.host, port=port, access_log=False, log_config=None),
                f"http://{settings.host}:{port}{launcher.UI_ENTRY}",
                open_browser,
                notices.append,
            )
            task = asyncio.create_task(server.serve(sockets=[listener]))

            def check_http() -> None:
                connection = http.client.HTTPConnection(settings.host, port, timeout=5)
                try:
                    connection.request("GET", "/api/health")
                    response = connection.getresponse()
                    assert response.status == 200
                    assert b'"status":"ok"' in response.read()
                    connection.request("GET", launcher.UI_ENTRY)
                    response = connection.getresponse()
                    assert response.status == 200
                    assert b"Deals - VeriDoc" in response.read()
                finally:
                    connection.close()

            try:
                await asyncio.wait_for(ready.wait(), timeout=10)
                await asyncio.to_thread(check_http)
            finally:
                server.should_exit = True
                await asyncio.wait_for(task, timeout=10)
            assert len(opened) == 1
            assert str(port) in opened[0]
            assert all(not instance.is_serving() for instance in server.servers)
        assert listener.fileno() == -1

    asyncio.run(exercise())
    assert all("private fixture content" not in notice for notice in notices)
    if browser_fails:
        assert any("Open this address" in notice for notice in notices)


def test_failed_startup_does_not_open_browser(
    launcher: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[str] = []

    async def fail_startup(self: object, sockets: list[socket.socket] | None = None) -> None:
        raise RuntimeError("startup failed")

    monkeypatch.setattr("uvicorn.Server.startup", fail_startup)

    def open_browser(url: str) -> bool:
        opened.append(url)
        return True

    server = launcher.BrowserServer(Config(FastAPI()), "unused", open_browser, lambda message: None)
    with pytest.raises(RuntimeError, match="startup failed"):
        asyncio.run(server.startup())
    assert opened == []


def test_false_browser_result_prints_manual_address(
    launcher: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    notices: list[str] = []

    async def ready(self: object, sockets: list[socket.socket] | None = None) -> None:
        server.started = True

    monkeypatch.setattr("uvicorn.Server.startup", ready)
    server = launcher.BrowserServer(
        Config(FastAPI()), "local-ui", lambda url: False, notices.append
    )
    asyncio.run(server.startup())
    assert any("Open this address: local-ui" in notice for notice in notices)


def test_server_failure_releases_listener_and_disables_access_logging(
    launcher: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    listeners: list[socket.socket] = []

    def fail_run(self: Server, sockets: list[socket.socket]) -> None:
        assert self.config.access_log is False
        assert self.config.proxy_headers is False
        listeners.extend(sockets)
        raise RuntimeError("server failed")

    monkeypatch.setattr(launcher.BrowserServer, "run", fail_run)
    app = create_app(Settings())
    with pytest.raises(RuntimeError, match="server failed"):
        launcher.run(app, ROOT / "apps/web")
    assert len(listeners) == 1
    assert listeners[0].fileno() == -1


@pytest.mark.parametrize("failure", [RuntimeError("private value"), KeyboardInterrupt()])
def test_main_handles_failure_without_leaking_details(
    launcher: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    failure: BaseException,
) -> None:
    def fail_run(app: FastAPI, web_directory: Path) -> None:
        assert Path.cwd() == ROOT
        assert web_directory == ROOT / "apps/web"
        raise failure

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", sys.path.copy())
    monkeypatch.setattr(launcher, "run", fail_run)
    assert launcher.main() == (0 if isinstance(failure, KeyboardInterrupt) else 1)
    assert "private value" not in capsys.readouterr().out


@pytest.mark.skipif(sys.platform != "win32", reason="Windows entry point")
@pytest.mark.parametrize("installed", [False, True])
def test_batch_from_another_directory_with_spaces_preserves_failure(
    tmp_path: Path, installed: bool
) -> None:
    checkout = tmp_path / "checkout with spaces"
    package = checkout / "packaging"
    package.mkdir(parents=True)
    batch = package / "START.bat"
    batch.write_bytes((ROOT / "packaging/START.bat").read_bytes())
    if installed:
        # A real interpreter shim exercises the batch invocation without installing dependencies.
        interpreter = checkout / ".venv/Scripts/python.exe"
        interpreter.parent.mkdir(parents=True)
        shutil.copy2(sys.executable, interpreter)
        # A copied venv redirector needs its original pyvenv.cfg to locate the base interpreter.
        (checkout / ".venv/pyvenv.cfg").write_bytes((ROOT / ".venv/pyvenv.cfg").read_bytes())
        (package / "launcher.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
    result = subprocess.run(
        ["cmd", "/d", "/c", str(batch)], cwd=tmp_path, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == (7 if installed else 1), result.stderr
    if not installed:
        assert "uv sync" in result.stdout
