# Active Review Findings

This is the bounded, active architecture-review ledger. Reviews prepend new entries here and keep
only unresolved findings or the most recent closure evidence. The complete historical ledger
through 2026-07-18 is retained unchanged at
`docs/working/archive/REVIEW_FINDINGS-through-2026-07-18.md` and in Git history.

## Review admission and convergence

- Critical/High correctness, security, financial/data-integrity, or binding source-contract
  findings create immediate corrective slices.
- Medium findings are grouped into the owning slice or epic closure. Low findings remain recorded
  unless they naturally combine with higher-severity work.
- Related symptoms are grouped by root owner rather than creating one corrective slice per symptom.
- Every `review-packet.md` reports non-negative integer counts for findings closed, new findings by
  severity, and corrective slices added. Validation checks the reported additions against the
  candidate queue diff.
- Two consecutive reviews with no new Critical/High findings expand routine cadence from four to
  eight completed slices. Any new Critical/High resets cadence to four. Epic boundaries always
  trigger a review.

## Open findings from 2026-07-18_204305_architecture_review

Reviewed range: `fb380227...e3d965ad`. Full evidence and detailed code/source citations are in the
historical ledger linked above.

### 009H9B — final-attempt recovery and exception queue

- **High:** an expired running job at its final allowed attempt can be returned to retry and then
  violate the database attempt cap instead of becoming terminal.
- **High:** exhausted provider/job/entity/error/retry facts need one reachable, singular operator
  exception and resolution ledger.
- Closure requires exact-cap recovery, repeated-scan idempotency, fenced stale-worker behavior,
  operator scope, and PostgreSQL winner/loser evidence.

### 009H9C — channel interface and immutable provider evidence

- **High:** generic SMS/phone/courier jobs currently cross the Email adapter; SMS requires its own
  adapter and sensitive-content matrix, while unsupported channels must fail closed.
- **Medium:** the public communications facade, API replay envelope, immutable attempt/provider
  evidence, and thin periodic-task boundary remain partial.
- Closure requires production-callable interface tests, channel/template/recipient coherence,
  stable replay, immutable provider facts, concurrency evidence, and contract-document alignment.

### 009I2 — member disbursement-status contract

- **High:** MP14 must use an explicit selected application and server-owned workflow truth rather
  than client ordering/ranking.
- **High:** documentation, SAP, initiation, CFC, transfer, and advice stages must expose their own
  retained timestamps or honest nulls; timestamps may not be fabricated from later events.
- **Medium:** restore existing portal composition and produce declared real-Django visual evidence.

## Closed since the latest review

- `009H9A` completed the Critical queued-job migration provenance closure. Its implementation and
  independent validation evidence live in `.ralph/runs/2026-07-18_210357_normal_run/`.

Older findings whose corrective slices are Complete remain searchable in the historical ledger;
they are not repeated here. A future review may restore an archived item to this active file only
when current code or evidence reproduces it.
