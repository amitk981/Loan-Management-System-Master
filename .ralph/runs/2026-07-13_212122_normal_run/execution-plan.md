# Execution Plan

Selected slice: `007G2-general-meeting-current-evidence-and-document-scope-closure`

## Scope and seams

- Keep the public §25.11 POST endpoint and canonical approval-case list/detail/action interfaces.
- Deepen the documents module with one reference-authorization interface that owns document
  existence, upload provenance, application attribution, category, sensitivity, and workflow-purpose
  checks. The approvals module will consume that interface and will not query `DocumentFile`.
- Make the approvals module choose one General Meeting projection: the current unsuperseded record
  for an evidence-required pending cycle, or the case-frozen record for returned/terminal history.
- Preserve 007F2 exception reason/register facts and existing case reader scope without recomputing
  exception or conflict truth.

## TDD tracer bullets

1. RED then GREEN: through §25.11 plus canonical list/detail/action endpoints, prove pending,
   rejected, and approved current evidence is projected during a pending cycle with an explicit
   `current_pending` source; prove return/final approval freezes the applicable row with
   `cycle_frozen` source and later supersession cannot rewrite historical reads.
2. RED then GREEN: upload valid legal documents through the public document endpoint, then record
   them through §25.11. Add same-permission cross-application, missing/unproven metadata,
   disallowed category/sensitivity, unrelated-file, and unscoped-actor rows for each evidence field;
   require one nondisclosing validation contract and zero meeting/audit/workflow/case/exception/
   download-audit writes.
3. Run the lifecycle against the existing public above-limit/007F2 case path (or extend its public
   tracer) and assert meeting supersession does not change `reason_for_approval`, `exception_reason`,
   Exception Register identity, or ordinary/assigned visibility.

## Documentation and closure

- Update `docs/working/API_CONTRACTS.md`, A-085, the Epic 007 digest, and 007I run-ahead semantics.
- Run scoped tests after each red/green cycle, then backend check, migration sync, full coverage,
  and unchanged frontend build/typecheck/lint/test gates.
- Save red/green and gate logs under the run evidence folder, complete changed-files/risk/review/final
  artifacts, mark only 007G2 complete, update state/progress/handoff, and review the work against the
  slice and repository standards. Do not commit, add, push, or edit protected paths.
- Re-check and sharpen the next two Not Started slices (`007H2`, `007I`) only with requirements from
  source sections already opened and this delivered contract.
