# Risk Assessment

Risk level: High

- Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`
- Mode: `normal_run`
- Independent validation required: yes

## Material Risks and Controls

| Risk | Exposure | Control and evidence |
|---|---|---|
| Duplicate or stale reminder delivery | A provider effect could occur after repayment, source/scope change, cancellation, timeout, or a competing claim. | The final server owner locks the job and serviceability inputs through the provider effect. The exact five-test PostgreSQL class exercises repayment-after-check, source/scope change, competing workers, exact retry, and timeout followed by repayment, twice against PostgreSQL. |
| Partial direct-repayment completion | Capture could be presented as complete without SAP posting and allocation, or replay could duplicate financial effects. | The browser now invokes one backend transaction which composes the existing idempotent capture, posting, and allocation owners and returns the retained complete projection. Focused replay regression is retained. |
| Historical MIS drift | Events recorded after quarter cutoff could rewrite an already generated as-of view. | Invoice status is projected from cutoff-valid retained timestamps, with a permanent post-cutoff issuance regression and exact replay coverage. Existing source owners remain unchanged. |
| Duplicate statement artifact | Equal-key concurrent generation could race at `get_or_create`. | The losing path validates and returns the retained artifact. Borrower CSV projection is explicitly allow-listed and retains safe metadata for an empty statement. |
| Portal omission or mutable payment instructions | The UI could silently truncate after 100 records or read instructions from mutable runtime settings. | The transport follows canonical pagination; a 101-row regression crosses the first page. Instructions now come from an immutable, approved, effective-dated database version with one-active-version enforcement. |
| Migration/data rollout | A new instruction table is empty until an approved version is seeded. | The portal truthfully returns no direct-repayment instruction/action until an active effective version exists. Migration consistency and Django checks pass; no implicit fallback to settings remains. |

## Residual Risks

- Reminder provider latency now extends a database transaction and row-lock lifetime. This is an
  intentional correctness tradeoff for a provider without an idempotent prepare/commit protocol;
  operations should monitor lock duration and provider timeout rates.
- The composite repayment command relies on a single database transaction plus the existing
  idempotency records rather than a new durable per-step command journal. A database rollback
  converges internal state, but a future non-transactional SAP adapter would require an outbox or
  durable step state before adoption.
- Pagination traversal is permanently exercised at the schedule boundary; repayments and invoices
  share the same transport helper and backend envelope but do not each have a separate 101-row test.
- The orchestrator still owns the authoritative complete backend coverage run. This agent followed
  the run contract and did not duplicate that full-suite gate.

## Gate Evidence

- PostgreSQL acceptance passes: `postgresql-acceptance-authoritative-pass-1.log` and
  `postgresql-acceptance-authoritative-pass-2.log` (five tests each, both exit 0).
- Focused backend: 37 tests, exit 0.
- Focused frontend: 19 tests, exit 0.
- Django check, migration dry-run, frontend typecheck, lint, and build: exit 0.

