# Review Packet: 2026-07-13_042414_normal_run

## Result
Ready for independent validation

## Slice
007A-approval-matrix-configuration

## Standards Review

The independent reviewer found configuration lifecycle logic outside the approvals module seam and
an identity-to-approvals model dependency. Both were corrected: lifecycle logic now lives under
`approvals.modules`, views translate HTTP only, and committee seeding is an approvals command.
Ralph artifacts/state are completed below. No unresolved documented-standard violation remains.

## Spec Review

The independent reviewer found historical resolution excluded superseded rules, missing race proof,
partial permission negatives, and incomplete invalid-input zero-write evidence. Historical lookup now
uses effective dates irrespective of current status; tests cover both resources' 401/403 behavior,
non-finite complete zero-write state, and PostgreSQL competing create/supersede one-winner behavior.
The committee is seeded by `seed_approval_configuration` after deterministic demo users exist.

## Traceability

- Source data-model §15.1-§15.2 says effective-dated committee/rule facts; the models and migration
  persist those fields, verified by `SeededApprovalMatrixTests` and demo seed tests.
- Functional M05-FR-003-006 and auth §16.2 say up to ₹5L is CFO + one Director, above is CFO + two,
  and exceeds-limit requires the Exception Register; migration data and resolver boundary tests prove it.
- API §25.1 and auth §12.6 say matrix GET/POST/PATCH with read/manage permissions; API tests verify
  standard envelopes, 401/403, immutable supersession, overlap conflict, audit, and zero-write denial.

## Recommended Next Action

Run independent standard gates and PostgreSQL five-race acceptance, then commit/merge through Ralph.
