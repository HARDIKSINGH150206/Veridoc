type: Added
area: 1
requirements: FR-IMP-007, FR-IMP-009
summary: Add the demo-only sample messages endpoint (issue #14) that validates bundled fixtures with the shared Message model (contracts v0.2.0). 404 when demo mode is off or the sample is unknown, a generic 503 for invalid fixture data. No network, persistence, analysis or vault writes.
