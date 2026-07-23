# Execution Plan

Selected slice: `011M3-global-search-compliance-results`

## Boundary

Extend the existing 010N registered provider seam with safe projections from the canonical
011K–011M compliance owners. Do not add a search table, change sensitive-query handling, expose
restricted evidence/KYC/legal content, or edit future slices.

## Behaviours, in TDD order

1. An authorised caller can find a compliance control/task, money-lending review, Section 186
   tracker, NBFC test, and KYC/re-KYC review through the public global-search API, with deterministic
   ordering, source-backed S02 fields, and only route-valid actions.
2. Compliance permissions and object ownership filter every record type; guessed identifiers and
   restricted evidence, legal-opinion, KYC, comment, and hidden-count content do not leak.
3. An unavailable or invalid compliance provider fails closed as a safe omitted/errored group and
   cannot turn into broad access or fabricated success.
4. The existing frontend renders the seventh Compliance Records group, including its safe card and
   authorised action, without new styling or local sensitive state/indexing.
5. The trusted browser spec proves the complete seven-group S02 contract and writes
   `global-search-compliance-results.png` on two runs.

## Implementation seams

- Add a compliance-owned search facade that uses canonical model/query ownership and returns only
  shared `build_result_card` projections.
- Register it from the compliance app lifecycle without importing compliance models into the
  aggregate search process.
- Preserve the 010N continuation, pagination, rate-limit, group ordering, and frontend patterns.

## Focused validation and evidence

- Save each backend RED/GREEN command under `evidence/terminal-logs/`.
- Run focused compliance/global-search backend tests with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run focused frontend tests, then frontend typecheck, lint, and build.
- Run the declared Playwright spec twice with the run evidence directory.
- Save source-to-card/permission and leak-negative matrices, risk assessment, review packet, and
  final summary. The orchestrator owns the authoritative full backend gate and all Git operations.
