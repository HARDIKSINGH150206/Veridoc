type: Added
area: 2
requirements: FR-EXT-001, FR-EXT-002, FR-AIS-001
summary: Add the demo analysis for the walking skeleton (issue #30): analyze_demo maps a FakeModelAdapter recording to unconfirmed Terms with source links for each bundled sample, and GET /api/analysis/samples/{id}/terms serves them in demo mode (501 for VERIDOC_MODEL_MODE=local). Recordings are hand-written, not real model output. Depends on the model adapter (PR #70).
