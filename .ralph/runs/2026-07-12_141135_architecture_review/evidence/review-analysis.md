# Architecture Review Evidence

## Reproducible boundary

```text
fixed point: b6d86cd4d777dd83167ac5d7e6c859659d88dbfc
commits: 654a92b, 45c267d, 8dc46e8, 5cbbc5d
diff: git diff b6d86cd...HEAD
```

## Concrete continuity defect

Executed with the required Ralph backend interpreter through `manage.py shell`:

```text
years = 2020-21, 2022-23, 2023-24, 2025-26, 2026-27, 2027-28
reported_continuity = 5
actual_longest_uninterrupted_run = 3
```

The helper counts later matching offsets after gaps, so BR-004/BR-007 can pass without four
continuous financial years. Corrective owner: 006Z4.

## Evidence cross-checks

- 006X5's result table claims exhaustive action/write coverage, while its executable matrix contains
  primarily permission denials and one sanction state denial; required role/object/maker-checker/
  provenance/history/payload/stale variants are absent.
- 006Y5 uses ordinary sequential `TestCase` requests for duplicates; no PostgreSQL runtime capability,
  concurrent transaction case, or duplicate-approval race exists.
- Member approval projection calls an evaluation without object scope; the write performs object
  access first. Witness Update projection omits the verifier check enforced by identity correction.
- 006Y5/006Y6 run packets contain no trusted browser contract/screenshots despite their slice evidence
  requirements. 006Y6 explicitly cites absence of a runtime capability as its reason for omission.
- Active-member public tests cover one individual direct route but omit institution, BR-006 service,
  relaxation, as-of/future, and row-classification cases.

## Independent critics

Separate Standards and Spec critics reviewed the same fixed diff with different source sets. Their
findings were retained as separate axes in REVIEW_FINDINGS; the primary reviewer then reproduced the
continuity defect and checked run-packet evidence before creating corrective slices.
