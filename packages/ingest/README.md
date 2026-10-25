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

## Demo recap with an echo code (#29)

`demo_recap.build_demo_recap` builds the recap of one agreement version from confirmed terms (`AgreedTerm`) only, hashes its content without the code line (`recap_hash`, INTEGRITY_SPEC section 7) and derives the echo code from that hash. The hashed content includes `deal_id` and `version_n`, so a code cannot be reused for another version or deal. `POST /api/agreement/samples/{sample_id}/recap` (demo mode only) takes `{"terms": [AgreedTerm, ...]}`, checks that the primary user confirmed them and that their sources are messages of the sample, and returns the `Recap`. The wording is a stand-in until the playbook templates exist (#64). A body that fails validation is answered with a fixed message that never repeats chat content.
