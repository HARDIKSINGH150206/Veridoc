Thin FastAPI route modules. ingest.py and agreement.py (Area 1), analysis.py (Area 2), vault.py and export.py (Area 3). main.py (Area 3) loads them automatically. Routes only; no business logic.

## How routers are loaded (ADR-022)

`apps/api/main.py` imports every public module in this folder (names not starting with `_`, in alphabetical order) and mounts its `router` under `/api`. To add routes:

1. Create or edit your area's module here and define a module-level `router = APIRouter(prefix="/<name>", tags=["<name>"])`.
2. Add routes to it. Do not edit `main.py`.
3. A module with no `router` attribute is a placeholder and is skipped. A module that fails to import, or whose `router` is not an `APIRouter`, stops startup with an error that names the module.
4. Routers stay thin: validate input and output with contract models, call a package, return the result. No business logic here.
5. Settings come from `apps/api/settings.py` (available as `request.app.state.settings`), never from `os.environ` or constants.

`GET /api/health` is defined in `main.py` and shows status, safe mode, demo mode and the number of loaded routers.
