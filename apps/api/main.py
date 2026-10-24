"""The FastAPI application. It loads every module in apps/api/routers/ automatically (ADR-022).

To add routes, create or edit a module in apps/api/routers/ that defines a module-level
`router = APIRouter(...)`. Nobody edits this file to add a route. Settings come only from
apps/api/settings.py.
"""

import importlib
import logging
import pkgutil
from types import ModuleType

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict

from .settings import Settings

ROUTERS_PACKAGE = "apps.api.routers"
ROUTER_ATTRIBUTE = "router"
API_PREFIX = "/api"

log = logging.getLogger("veridoc.api")


class RouterLoadError(RuntimeError):
    """A router module could not be loaded. The message names the module."""


class HealthResponse(BaseModel):
    """Answer of GET /api/health. Contains no user data."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: str
    safe_mode: bool
    demo_mode: bool
    router_count: int


def discover_routers(package_name: str = ROUTERS_PACKAGE) -> list[tuple[str, APIRouter]]:
    """Import every public module of a package and return its `router` objects, sorted by name.

    A module without a `router` attribute is a placeholder and is skipped. A module that fails
    to import, or whose `router` is not an APIRouter, raises RouterLoadError naming the module.
    """
    package = importlib.import_module(package_name)
    found: list[tuple[str, APIRouter]] = []
    for info in sorted(pkgutil.iter_modules(package.__path__), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        full_name = f"{package_name}.{info.name}"
        try:
            module: ModuleType = importlib.import_module(full_name)
        except Exception as error:  # noqa: BLE001 - re-raised with the module name
            raise RouterLoadError(f"could not load router module {full_name}: {error}") from error
        if not hasattr(module, ROUTER_ATTRIBUTE):
            log.info("router_placeholder_skipped module=%s", full_name)
            continue
        router = getattr(module, ROUTER_ATTRIBUTE)
        if not isinstance(router, APIRouter):
            raise RouterLoadError(f"{full_name}.{ROUTER_ATTRIBUTE} is not a fastapi.APIRouter")
        found.append((info.name, router))
    return found


def create_app(settings: Settings | None = None, routers_package: str = ROUTERS_PACKAGE) -> FastAPI:
    """Build the application: store settings, load all routers, add the health route."""
    settings = settings or Settings()
    logging.getLogger("veridoc").setLevel(settings.log_level.upper())
    app = FastAPI(title="VeriDoc", docs_url=None, redoc_url=None)
    app.state.settings = settings

    routers = discover_routers(routers_package)
    for name, router in routers:
        app.include_router(router, prefix=API_PREFIX)
        log.info("router_loaded name=%s", name)

    @app.get(f"{API_PREFIX}/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            safe_mode=settings.safe_mode,
            demo_mode=settings.demo_mode,
            router_count=len(routers),
        )

    return app


app = create_app()
