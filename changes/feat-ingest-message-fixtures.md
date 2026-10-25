Added parsed synthetic Message fixtures and source-preservation/contract tests
for Issue #13 (FR-IMP-001, FR-IMP-007). Depends on sample fixtures from #12.
Built against draft contracts PR #40 at de8bc7b; contract checks explicitly skip
when the shared Message model is absent. Revalidate after contract agreement.
