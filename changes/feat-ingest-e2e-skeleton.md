Added an import-to-confirmed-fake-receipt contract-flow harness in packaging/tests
for Issue #16 (NFR-MNT-002). Uses the real demo ingest endpoint and test-only
analysis/record adapters, with explicit confirmation and no vault writes. Draft
contracts #40 required. This does not complete the four-area UI walking skeleton
or offline verification; those still depend on #30, #31, #32 and agreed contracts.
