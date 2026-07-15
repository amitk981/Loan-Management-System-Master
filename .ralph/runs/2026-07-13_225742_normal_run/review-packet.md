# Review Packet: 2026-07-13_225742_normal_run

## Result
Success

## Slice
007H3-frozen-case-provenance-and-read-scope-parity-closure

## Outcome

Approval-case validity is now frozen-only. The credit interface validates the locked appraisal and
complete loan-limit source at enrichment; later case reads validate only the immutable approval
snapshot. The reader projection narrows candidates, then the same frozen-validity and actor-scope
decision runs before detail/action/decision/register counts, filters, pagination, and serialization.

## Traceability

- The source docs say approval cases/actions/decisions/register rows are cycle-attributed immutable
  records (`data-model.md` §§15.3-15.6) and sanction approval writes remain atomic (§34). The code
  keeps all existing transaction boundaries, removes the live appraisal comparison, and introduces
  no hidden write. Verified by
  `test_live_appraisal_policy_change_preserves_pending_case_reads_and_action` and
  `test_return_correction_fresh_review_creates_immutable_second_cycle`.
- The source API says approval detail/actions and sanction/register reads use the §25.3-25.9 public
  boundaries with §8 pagination. The code validates/scopes every narrowed case before counts and
  pages. Verified by
  `test_malformed_frozen_terminal_case_fails_closed_at_every_read_boundary`.
- The codebase design says the Approval Case Engine is the deep module (§13.1/§27.1), tests cross
  public interfaces (§26), and views remain thin (§42). The single approval-owned validity/read
  decision is reused by case, action, decision, Exception Register, and Credit Sanction Register
  callers. Verified by all 106 approval-routing tests and the focused terminal parity regression.

## Files and design review

- Production changes are limited to `approval_case_engine.py` and
  `approval_case_selector.py`; there is no schema, permission catalogue, URL, serializer, or
  frontend production change.
- `API_CONTRACTS.md` and the Epic 007 digest record frozen-versus-live ownership and pre-count
  parity. 007I/007J carry concrete container regressions for old/new cycles and hidden register
  rows.
- No protected or source file was modified. `git diff --check` is clean.

## Validation

- RED: live appraisal policy mutation changed case detail from 200 to 404.
- GREEN: pending/live, malformed-frozen, terminal/live, and returned/new-cycle public probes pass.
- Approval routing: 106 tests pass (2 expected PostgreSQL skips).
- Full backend: 679 tests pass, 19 expected PostgreSQL skips, 93% coverage (floor 85%).
- Frontend: build/typecheck/lint green; 208 tests pass.

## Recommended Next Action
Run independent Ralph validation, commit/merge/push the passing slice, then execute 007I.
