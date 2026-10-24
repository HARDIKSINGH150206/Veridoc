type: Added
area: 3
requirements: NFR-MNT-001, NFR-SEC-004
summary: apps/api/main.py now loads every module in apps/api/routers/ automatically (ADR-022), reports a broken module by name, skips placeholders, takes settings from the settings module and serves GET /api/health.
