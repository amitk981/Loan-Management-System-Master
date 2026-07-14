# Review Range and Diagnostics

## Pinned range

- Fixed point: `7d0106a627bde89408b5bb95bb880c30bb8ad012`
- Diff: `git diff 7d0106a6...87f2e93b`
- Commits:
  - `a9af7867` — 007T register null/action order closure
  - `a1e6c5e9` — 008B2 legal-document boundary closure
  - `fdc57ece` — 008B3 renderer/output closure
  - `87f2e93b` — 008C checklist applicability

## Reproducible diagnostic facts

- `approval_actions.approve_case` and `record_action` accept
  `sanction_completion_hook=None`; the hook is invoked only when non-null after decision creation.
  The HTTP adapter uses the coordinator, but direct callers can create a final decision without it.
- `document_checklist._synchronise_items` computes `completion_status=pending/not_applicable` for
  every existing item. It does not preserve later `complete`/verification facts.
- `document_checklist._signature_mismatch` reads `CancelledCheque.signature_mismatch_flag` without
  filtering or evaluating `verification_status`; default false pending rows become source matches.
- `legal_documents` imports the members model directly although codebase-design §36.2 omits that app
  from its dependency set, and checklist audit writers receive no request metadata.
- generation replay returns an existing `LoanDocument` before current renderer validation. The model
  stores no renderer contract/version provenance, while the checklist selector accepts generated +
  non-null template/file metadata. The 008C link test manually creates such a row without bytes.
- authorized absent application ids become module `ValidationError` and HTTP 400 in generation/list,
  not the standard 404 contract.

## Queue outcome

- Added `008B4-renderer-provenance-and-replay-contract-closure`.
- Added `008C2-checklist-lifecycle-authority-and-side-effect-closure`, dependent on 008B4 and 008C.
- Changed 008D to depend on 008C2 and sharpened its provenance/completion seam requirements.
- No slice was `Blocked`; no stale prerequisite status required changing.
