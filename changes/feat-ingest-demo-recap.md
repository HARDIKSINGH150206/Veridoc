type: Added
area: 1
requirements: FR-RCP-001, FR-RCP-002, FR-ECH-001, FR-ECH-002
summary: Add the demo recap with an echo code for the walking skeleton (issue #29): build_demo_recap hashes the recap content without the code line, derives the code with packages/integrity, and POST /api/agreement/samples/{id}/recap (demo mode only) accepts only terms confirmed by the primary user. Wording is a stand-in until the templates (#64).
