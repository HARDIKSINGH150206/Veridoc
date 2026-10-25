type: Added
area: 2
requirements: FR-EXT-001, FR-EXT-004, FR-AIS-002, FR-AIS-004
summary: Add the model adapter (issue #63): ModelAdapter protocol, FakeModelAdapter with recorded outputs including the model's two known real mistakes, a mapping from the local model's JSON to contract Terms (dates, money, quantities, message numbers, voice time ranges, malformed output marked for review, grounding and value-versus-quote checks), and the VERIDOC_MODEL_MODE=fake|local setting (local not built, issue #69).
