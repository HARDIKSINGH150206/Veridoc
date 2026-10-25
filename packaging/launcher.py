"""Start the local API and bundled layout preview (#15).

Run as a script, not as ``python -m packaging``: that name belongs to an installed dependency.
Bundle-relative asset names below follow the repository layout; runtime host, port and logging
configuration come from the API's existing Settings object.
"""

import os
import socket
import sys
import webbrowser
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, cast

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server

if TYPE_CHECKING:
    from apps.api.settings import Settings

UI_MOUNT = "/ui"
UI_DOCUMENT = Path("screens") / "s1-deals" / "index.html"
UI_ENTRY = f"{UI_MOUNT}/{UI_DOCUMENT.as_posix()}"


def mount_ui(app: FastAPI, web_directory: Path) -> None:
    """Serve only bundled web assets, never the repository or vault directory."""
    if not (web_directory / UI_DOCUMENT).is_file():
        raise FileNotFoundError("Bundled UI is missing. Restore the complete checkout.")
    app.mount(UI_MOUNT, StaticFiles(directory=web_directory, html=True), name="launcher-ui")


@contextmanager
def bind_listener(settings: "Settings") -> Iterator[socket.socket]:
    """Keep the chosen socket open through startup, avoiding a free-port race."""
    port = settings.port if settings.port is not None else 0
    if not 0 <= port <= 65535:
        raise ValueError("Configured port must be between 0 and 65535.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        if sys.platform == "win32":
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        listener.bind((settings.host, port))
        yield listener


class BrowserServer(Server):
    """Open the browser only after Uvicorn has completed application and socket startup."""

    def __init__(
        self,
        config: Config,
        url: str,
        open_browser: Callable[[str], bool],
        report: Callable[[str], None],
    ) -> None:
        super().__init__(config)
        self.url = url
        self.open_browser = open_browser
        self.report = report

    async def startup(self, sockets: list[socket.socket] | None = None) -> None:
        await super().startup(sockets=sockets)
        if not self.started or self.should_exit:
            return
        self.report(f"VeriDoc layout preview: {self.url} (Ctrl+C to stop)")
        try:
            opened = self.open_browser(self.url)
        except Exception:
            # Browser errors may include local paths; show a safe fallback without details.
            opened = False
        if not opened:
            self.report(f"Browser could not open automatically. Open this address: {self.url}")


def run(
    app: FastAPI,
    web_directory: Path,
    open_browser: Callable[[str], bool] = webbrowser.open,
    report: Callable[[str], None] = print,
) -> None:
    """Run in the foreground; Uvicorn handles Ctrl+C and shutdown of active connections."""
    settings = cast("Settings", app.state.settings)
    mount_ui(app, web_directory)
    with bind_listener(settings) as listener:
        port = listener.getsockname()[1]
        config = Config(
            app,
            host=settings.host,
            port=port,
            log_level=settings.log_level.lower(),
            access_log=False,
            proxy_headers=False,
        )
        server = BrowserServer(
            config, f"http://{settings.host}:{port}{UI_ENTRY}", open_browser, report
        )
        server.run(sockets=[listener])


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    # Locate imports and the API's .env independently of the caller's working directory.
    sys.path.insert(0, str(repo_root))
    os.chdir(repo_root)
    try:
        from apps.api.main import create_app

        run(create_app(), repo_root / "apps" / "web")
    except KeyboardInterrupt:
        return 0
    except Exception:
        # Do not print exceptions that could contain environment values or user identifiers.
        print(
            "Could not start VeriDoc. Check dependency setup, bundled UI files and VERIDOC_PORT; "
            "the configured port may already be in use."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
