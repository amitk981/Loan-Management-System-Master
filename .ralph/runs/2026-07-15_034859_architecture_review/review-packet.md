# Review Packet: 2026-07-15_034859_architecture_review

## Result

Success

## Slice and Range

Architecture review of `git diff 85f142c2...447e965b`, covering completed slices 008I2, 008I3,
008I4, 008J, and 008K. No production code changed.

## Standards

The isolated Standards pass found one Critical, one High, and two Medium issues. Versioned
ciphertext embeds plaintext last-four values; Senior Manager Finance/CFC reads are wider than the
source state/object matrix; blank-cheque PATCH is full replacement; and promised two-direction
dependency/forged-access/duplicate-hash proof remains incomplete. The apparently missing
Idempotency-Key and CFO-checklist-signature findings were rejected after applying the more specific
§45 and SOP/008K contracts; A-118 records the idempotency interpretation.

## Spec

The isolated Spec pass found one Critical, two High, and one Medium issue. Synthetic application-
labelled cheque version JSON completes a checklist without a current cheque row; status-only bulk-
completed items pass Company Secretary approval without durable completion actions; the promised
public terminal matrix is mostly bypassed; and race assertions prove aggregate counts rather than
exact winner/loser identities.

## Executable Reproduction

The retained review harness adds three expected-failing assertions and changes no production/test
discovery path:

- `123456` produces ciphertext containing `:6:3456:`.
- no `BlankDatedCheque` row plus a synthetic version projection returns successful completion.
- complete item statuses with no completion actions return successful Company Secretary approval.

All inherited tests inside the harness remain green. The red log is defect evidence, not a quality-
gate failure.

## Traceability and Architecture Outcome

- Data-model §§17.4-17.5/29 require protected values in encrypted columns; 008J requires the fixed
  ordinary cheque mask without recoverable fragments.
- Auth §19.2 gates finance readers by documentation approval/disbursement readiness, not Stage 4.
- API §5.1 requires partial PATCH; §§27.3-27.7 and 008K require durable public action evidence.
- 008K's sharpened cheque contract requires exact current source-owner ids and decision truth.
- M06-FR-007-012/016-017 remain partial until corrections; M06-FR-013-015 remain A-101 constrained.
  No epic completed.

## Corrective Queue

1. `008K2-sensitive-security-contract-closure` — opaque ciphertext migration, partial PATCH,
   source-scoped readers, central redaction and complete executable boundary/hash proof.
2. `008K3-final-checklist-evidence-closure` — exact source-owned terminal evidence, one action per
   item, public completion matrix, authorising-role attribution, and exact race identities.
3. 008L now waits for K3; 008L/008M are sharpened against the corrected projections.

No Blocked slice is stale. No ADR was required because existing source documents decide the
boundaries. The complete queue parses and drains.

## Validation

- Review regression evidence: 3 expected failures, demonstrating the filed defects.
- Frontend: lint and typecheck pass; 293/293 tests pass; production build passes.
- Backend: Django check and migration sync pass; 855/855 tests pass with 39 expected SQLite skips.
- Coverage: 92%, exceeding the 85% floor.
- Queue drain, state JSON, `git diff --check`, no-production/no-source, and protected-path checks pass.

## Recommended Next Action

Run 008K2, then 008K3. Do not start 008L first.
