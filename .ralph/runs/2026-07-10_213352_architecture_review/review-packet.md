# Review Packet: 2026-07-10_213352_architecture_review

## Result

Success — five corrective slices required before the Epic 006 tracer.

## Fixed Point and Reviewed Set

- Fixed point: `46442fe7892d3ad7aa9f4251a9f5f01442ff4a9a`
- Diff: `git diff 46442fe...HEAD`
- Commits: `cd3aca6` 006E3, `b022c83` 006F3, `b1b8889` 006G, `b7cf63f` 006H.
- Spec sources: four slice files, Epic 006/digest, functional §9.8/M04-FR-001-011, API §3/§22-25,
  auth §19.2/§25.3/§34.4, data-model §14-§15/§30/§34, and appraisal test plan.
- Standards sources: AGENTS/Decision Policy/Frontend Design Rules plus codebase-design §12-§13,
  §22-§26, §31-§32, §35-§37; API §6-§8; data-model §30/§34.

## Standards

1. **Critical — hard: required PostgreSQL acceptance never executed.** 006F3's own committed packet
   says failed acceptance/do not merge and four tests found, zero executed; it was marked Complete
   and merged. 006G's fifth PostgreSQL race also executed zero before success was claimed.
2. **High — hard: frontend recreates workflow/action state.** Local role/permission/status logic
   replaces backend `available_actions`, then React hard-codes two submitted statuses absent from
   the response. Revalidation is gated by the wrong permission/state.
3. **High — hard: protected prototype composition was redesigned.** The staged 1,186-line workbench
   became a new condensed form and the checklist/calculator layouts changed, with no screenshots.
4. **High — test quality: static rendering does not test actions.** The view tests never mount the
   container, run effects, click controls, mock the HTTP interface, or verify mutation refresh.
5. **Medium — hard: malformed JSON escapes the standard envelope.** The sanction adapter does not
   catch `ValidationError` from malformed or non-object JSON, unlike the established adapters.
6. **Medium — hard: authenticated transport is duplicated.** The new credit client adds a bespoke
   fetch path while omitting shared refresh/request-ID/envelope responsibilities.
7. **Medium — judgment: approval-case seam is reversed.** Credit imports a concrete approvals model
   although the documented dependency is approvals -> credit and the approval engine should hide
   case persistence/read/enrichment.

## Spec

1. **Critical — missing database outcome proof.** The slice-required five competing-transaction
   tests have never run on PostgreSQL.
2. **High — loaded drafts cannot PATCH.** The full response object becomes the form and is sent to a
   strict writable endpoint, including IDs, snapshots, history, status, reviewer, and TAT fields.
3. **High — legacy rows can be permanently stranded.** Migration 0005 downgrades all states while
   repair is draft-only; it also omits a known returned reason after resubmit.
4. **Medium — sanction case UUID disappears after reload.** No read returns the pending case and the
   loader explicitly clears it.
5. **Medium — revalidation uses the wrong UI authority/state.** The button is gated by draft plus
   submit-review permission although the backend requires update+risk permissions and
   legacy-unverified state.

Summary: Standards found 1 Critical, 3 High, and 3 Medium issues; Spec found 1 Critical, 2 High, and
2 Medium issues. The worst issue in both axes is the explicitly failed PostgreSQL acceptance.

## Corrective Architecture

- 006E4: state-aware legacy remediation and latest-known history backfill; A-061 prevents an old
  review from approving newly pinned facts.
- 006F4: execute all five PostgreSQL races twice with zero skips; unavailable execution is failure.
- ADR-0005/006G2: one approvals-owned deep module for case create/read/enrichment, complete canonical
  state response, reload-safe case summary, and malformed-body envelope.
- 006H2: writable draft projection, server actions/state, shared transport, and real container
  interaction tests.
- 006H3: restore the approved prototype composition with non-deferrable screenshots/visual tests.
- 006X now depends on 006H3. 007B must enrich the same unique case through ADR-0005's interface.

The codebase-design skill materially shaped ADR-0005: approval complexity is concentrated behind a
small approvals-owned interface, preserving dependency direction, locality, and an interface-level
transaction test surface instead of adding another concrete cross-app call.

## Test Quality and Functional IDs

006E3 and 006G have substantive functional assertions around authority, provenance, immutable
history, strict payloads, state, redaction, and rollback. The precise gaps are non-draft migration
repair, real PostgreSQL execution, real frontend actions, and visual fidelity. Full requirement
mapping is in `evidence/functional-id-coverage.md`; Epic 006 remains incomplete.

## Validation

- Django check and migration sync: pass.
- Backend: 372 passed, 5 PostgreSQL-only skipped; 93% coverage (85% floor).
- Frontend: lint/typecheck pass; 126 tests pass; production build pass.
- Final diff/protected/state/artifact checks are recorded in the run evidence.

## Recommended Next Action

Run 006E4, then 006F4. Continue through 006G2, 006H2, and 006H3 before 006X. Do not describe Epic
006 as PostgreSQL- or visually accepted until those corrections pass.
