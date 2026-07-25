# Trusted-Browser Repair Diagnosis

## Authoritative Symptom

The prior trusted browser run launched Chromium, completed disbursement, completed and replayed the
direct repayment, and then received HTTP 409 from the public subsidiary-repayment endpoint at
`critical-uat-smoke.e2e.spec.ts:227`. Screenshot validation did not run because this application
assertion stopped the scenario.

## Ranked Hypotheses and Result

1. Missing current verified tri-party agreement — confirmed.
2. Duplicate repayment/idempotency reference — disproved by the fresh seeded database.
3. Non-serviceable account status after direct repayment — disproved by the authoritative request
   sequence and the serviceable `partially_repaid` state.
4. Invalid subsidiary payload field — disproved by the public-API regression after restoring the
   agreement precondition.

The Epic 009 synthetic fixture contained the target tri-party agreement with generated, verified,
and renderer-validated evidence, but its execution status remained `pending`. The canonical
loan-term selector therefore returned no current agreement, and subsidiary capture correctly
failed closed.

## Repair

The guarded critical-UAT seed now advances only that retained synthetic agreement to `executed` and
then verifies it through the canonical `current_loan_term_document_for_update` selector. A missing
or otherwise invalid retained agreement raises `CommandError` rather than silently fabricating
replacement evidence.

The seed regression runs the guarded seed twice, verifies the canonical agreement, authenticates
the seeded Credit Manager, and posts the same subsidiary-deduction payload through the public
repayment API. It asserts HTTP 200 and `pending_statement`.

## Evidence

- RED: `terminal-logs/tri-party-precondition-red.log`
- GREEN selector/idempotency: `terminal-logs/tri-party-precondition-green.log`
- GREEN public API: `terminal-logs/tri-party-public-api-green.log`
- GREEN focused backend pack: `terminal-logs/backend-focused-green.log`
- Seeded-database canonical selector probe: `terminal-logs/tri-party-seeded-probe-green.log`
- Original exact-command repair attempt: `terminal-logs/trusted-browser-repro-red.log`
- Post-fix exact-command attempt: `terminal-logs/trusted-browser-acceptance-1.log`
- Current browser infrastructure probe: `terminal-logs/browser-infrastructure-probe-current.log`

The two current-run browser attempts and current probe aborted Chrome before a page existed. They
did not exercise the repaired assertion. The prior orchestrator-owned log remains the source of
truth for the post-launch 409, and independent trusted validation must rerun the declared spec
twice and produce the two declared screenshots.
