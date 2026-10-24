# Changelog fragments

Each pull request adds one file here instead of editing `CHANGELOG.md`. Two pull requests then never touch the same file, so the changelog never causes a merge conflict. The release lead (Hardik, Area 4) combines the fragments into `CHANGELOG.md` at the end of each phase and deletes them.

## File name

The branch name with `/` replaced by `-`, plus `.md`. Branch `feat/ingest-android-parser` gives `changes/feat-ingest-android-parser.md`.

## File content

```
type: Added | Changed | Fixed | Removed | Security | Docs
area: 1 | 2 | 3 | 4 | shared
requirements: FR-IMP-001, FR-IMP-002
summary: One plain sentence that a user or teammate would understand.
```

Rules:
1. One fragment per pull request. A fragment may have several `summary:` lines.
2. Do not include secrets, chat content or personal data.
3. Do not edit another pull request's fragment.
4. This `README.md` stays; the combine step ignores it.
