Added the demo-only sample messages endpoint for Issue #14 (FR-IMP-007,
FR-IMP-009), with source fixtures from #12/#13. Validates against the shared
Message model, built against draft PR #40 at de8bc7b. Returns 404 when demo mode
is off or the sample is unknown; 503 when contracts or fixture data are missing
or invalid. No network, import persistence, analysis, or vault writes.
