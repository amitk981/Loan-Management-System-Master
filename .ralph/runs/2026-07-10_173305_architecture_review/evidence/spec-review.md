# Spec

- **High — historically wrong:** 006E says appraisal consumes the stored 006B/006D facts, but the
  model stores only their UUIDs and caller-authored summaries. A same-UUID rerun replaces those
  facts, so the appraisal cannot prove the acreage, limits, policy, eligibility, or exception it
  used. ADR-0003/006E2 freeze the canonical projections.
- **High — missing/partial:** functional §9.8/M04-FR-009 requires
  `repayment_capacity_notes`; no API/model field exists. M04-FR-008's amount, tenure, interest/rate
  basis, and security facts do exist. 006E2 adds the exact missing field without inventing a
  repayment formula.
- **High — missing but owned:** M04-FR-001/002 require an appraisal task after application-number
  generation assigned to Deputy Manager–Finance. 006E only records the eventual preparer. A-053
  and sharpened 012EA explicitly own idempotent create/assign/close/reopen/backfill behavior.
- **High — unowned before review:** M04-FR-011 requires Credit Manager rejection and a Rejection
  Note; 006F only planned reviewed/returned and 006G sanction. New 006F2 owns a terminal rejected
  decision and one unsent 005H note.
- **Medium/watch:** M04-FR-003 allows receipt/completeness confirmation while §14.4 says receipt.
  The model has no completeness-confirmed timestamp, so A-054 keeps `application.created_at` as the
  explicit receipt proxy pending governance.
- **Low/watch:** the 005I5 public nominee seam owns same-member validation, but one resolver
  prefilters by member before calling it. Outcomes are safe and tests cover both paths; later
  locality cleanup should remove the duplicated decision if the module is extended.

No material scope creep was confirmed. Worst Spec issue: mutable IDs are presented as historical
appraisal snapshots. Four actionable findings; two watches.
