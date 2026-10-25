WhatsApp parser, media handling, voice import wiring (calls the speech interface owned by Area 2), recap builder and Blind Handshake logic. Owner: Area 1. Tests go in packages/ingest/tests/.

## Demo sample endpoint (#14)

With `VERIDOC_DEMO_MODE=true`, `GET /api/ingest/samples/{sample_id}/messages`
returns an array of shared Message objects. Bundled sample IDs are `clean`,
`ambiguous`, and `contradictory`. The endpoint is hidden (404) when demo mode is
off. Unknown names return 404. Missing draft contracts or invalid fixture data
return a generic 503 without exposing content or paths.

Requires contracts PR #40 (validated against draft de8bc7b); there is no duplicate
local schema. No real import, participant selection, persistence, or analysis is
implemented by this endpoint. Run `uv run pytest packages/ingest/tests`.
Contract-dependent tests skip explicitly until the Message model is installed
in the shared package; they must pass against the agreed models before merging.

Shared documentation request: review the demo endpoint under THREAT_MODEL T16/T17
and document this HTTP interface when contracts are agreed. Only synthetic
bundled data is exposed; callers cannot supply filesystem paths or request
arbitrary files. The app remains loopback-only and launcher access logs are off.
