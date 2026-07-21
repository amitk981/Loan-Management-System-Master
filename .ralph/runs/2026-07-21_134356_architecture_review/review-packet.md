# Review Packet: 2026-07-21_134356_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Scope

- Fixed point: successful architecture-review commit `5c0aba87`.
- Product commits reviewed: `00e537d3` (010K3), `9d4fa144` (010K2), `7574cd6b`
  (010L), and `283d9767` (010MA). Orchestration-only commits and retained run artifacts were
  excluded from the product critique.
- Trusted active roots: `ROOT-010-DPD-SNAPSHOT-OWNER` generation 2 via 010K3,
  `ROOT-010-REMINDER-DELIVERY-OWNER` generation 2 via 010K3, and
  `ROOT-010-MIS-AS-OF-OWNER` generation 1 via 010K3.
- Candidate changes are confined to the active findings ledger, one terminal corrective slice,
  two downstream dependency edges, and current-run review evidence/artifacts. Production code,
  migrations, source documents, protected files, state, progress, and mechanical handoff facts are
  unchanged.

## Standards Review

- Closed High: 010K3 adds the bidirectional database guard and public capitalisation-aware source
  needed by the DPD snapshot owner; the focused two-test closure set passes.
- Carried High: reminder serviceability still commits before the provider adapter side effect. A
  repayment in that gap produces one provider call.
- Carried High: MIS repeatable-read generation freezes a coherent current view, not historical
  transition truth. A post-cutoff issuance of an older-dated invoice changes the historical status.
- Escalated carried High: 010MA owns capture, SAP posting, and allocation in the client. An exact
  capture replay after a SAP failure returns `allocation: null` and never resumes the remaining
  financial steps.
- Grouped Medium: statement concurrent replay, borrower export projection, portal first-100
  truncation, cross-`TestCase.setUp` fixtures, and incomplete boundary matrices remain owner-seam
  debt.

The independent axis report is retained at
`.ralph/runs/2026-07-21_134356_architecture_review/evidence/standards-axis.md`.

## Spec Review

- 010K3 is partial against its final reminder execution-owner requirement because the locked check
  and provider invocation are not one retained decision.
- 010K3 is partial against immutable cutoff/source-race requirements because invoice status is not
  constrained by its transition timestamp.
- 010MA is partial against its stable idempotent repayment-attempt requirement because exact retry
  cannot continue after a committed partial attempt.
- 010K2 and 010L meet their core read surfaces but leave Medium borrower-safety, concurrent
  statement ownership, and pagination obligations incomplete.
- 010K3 satisfies the DPD cross-account integrity and capitalisation-consumption closure contract.

The independent axis report is retained at
`.ralph/runs/2026-07-21_134356_architecture_review/evidence/spec-axis.md`.

## Owner-Level Disposition

- `AR-010-DPD-001` is Closed High. Its root is removed after focused current-run closure evidence.
- `AR-010-REMINDER-001` remains Carried High at ordinary generation 2. It owns the terminal
  `CR-015` identity because this root has reached the configured cap.
- `AR-010-MIS-001` remains Carried High and advances independently from generation 1 to generation
  2 through the grouped `CR-015` mapping.
- `AR-010-SERVICING-SEAM-001` remains Carried under its stable root, escalated from Medium to High
  by the directly reproduced partial financial workflow. This is not a New finding.
- `AR-010-LEDGER-001` remains Carried Medium and unchanged; it was not charged to another root.

## Root-Cause Boundary Correction

`CR-015` is the one standing-policy terminal finalizer for exhausted root
`ROOT-010-REMINDER-DELIVERY-OWNER`. It groups all related Critical/High symptoms at the final
decision/side-effect owner: provider delivery, immutable MIS cutoff state, and resumable direct
repayment. It also bundles naturally related Medium statement/portal/test-seam debt so the review
does not create another leaf. `010MB` and the Epic 011 entry slice `011A` now depend on `CR-015`,
preventing consumers from advancing across the open Epic 010 boundary.

The generated slice declares `postgresql-five-race-acceptance`. Both required runtime validators
pass, and the complete queue lint passes with no dangling dependency or cycle.

## Focused Evidence

- DPD closure: 2 focused tests passed, exit 0.
- Reminder review probe: 1 intended assertion failed after one provider call, exit 1.
- MIS review probe: 1 intended assertion failed with historical status `issued` instead of `draft`,
  exit 1.
- Servicing replay review probe: 1 intended Vitest assertion failed with `allocation: null`, exit 1.
- Probe source, bound logs, and both independent axes are under
  `.ralph/runs/2026-07-21_134356_architecture_review/evidence/`.

These failures are review RED signals, not failed candidate product gates. No complete backend,
coverage, frontend, or browser suite was duplicated for this documentation-only review candidate.

## Convergence Metrics

- Findings closed: 1
- New Critical: 0
- New High: 0
- New Medium: 0
- New Low: 0
- Corrective slices added: 1

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-DPD-001 | ROOT-010-DPD-SNAPSHOT-OWNER | High | Closed | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/dpd-owner-reproducer.log | - | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/dpd-owner-closure.log |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | High | Carried | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/reminder-owner.log | CR-015 | - |
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | High | Carried | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/mis-owner.log | CR-015 | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | High | Carried | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/servicing-seam.log | CR-015 | - |

## Recommended Next Action

Run independent architecture-review validation. On acceptance, execute `CR-015` before 010MB or
Epic 011 work. If any of its grouped roots recurs after that terminal finalizer, fail closed instead
of admitting another terminal or numeric corrective.
