WhatsApp parser, media handling, voice import wiring (calls the speech interface owned by Area 2), recap builder and Blind Handshake logic. Owner: Area 1. Tests go in packages/ingest/tests/.

## Demo sample endpoint (#14)

With `VERIDOC_DEMO_MODE=true`, `GET /api/ingest/samples/{sample_id}/messages`
returns an array of shared Message objects. Bundled sample IDs are `clean`,
`ambiguous`, and `contradictory`. The endpoint is hidden (404) when demo mode is
off. Unknown names return 404. Invalid fixture data returns a generic 503 without
exposing content or paths.

Every fixture is validated with the shared Message model (contracts v0.2.0); there is
no duplicate local schema. No real import, participant selection, persistence, or analysis is
implemented by this endpoint. Run `uv run pytest packages/ingest/tests`.

Shared documentation request: review the demo endpoint under THREAT_MODEL T16/T17
and document this HTTP interface when contracts are agreed. Only synthetic
bundled data is exposed; callers cannot supply filesystem paths or request
arbitrary files. The app remains loopback-only and launcher access logs are off.

`GET /api/ingest/samples` lists the bundled samples and `GET /api/ingest/samples/{sample_id}` returns one with its playbook id, participants and messages (demo mode only, same 404 and 503 rules).
