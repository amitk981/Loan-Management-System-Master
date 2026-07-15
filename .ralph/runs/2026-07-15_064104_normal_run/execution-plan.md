# Execution Plan

Selected slice: 008L-member-portal-documentation-actions

1. Confirm the source/API/model requirements and existing owner seams for portal scope, checklist
   projection, immutable document upload provenance, borrower-safe generated-document descriptors,
   and masked security status. Record any source-silent implementation assumption before product
   edits.
2. Add failing backend API/service tests first for the self-scoped GET and multipart upload routes:
   own/cross-member/session matrices, sanctioned versus blocked states, canonical applicability,
   stable ordered actions, upload/re-upload validation and immutable provenance/history/audit, safe
   downloads, sensitive-field scans, and proof that uploads cannot mutate internal legal/security/
   checklist/readiness truth. Save the red run in `evidence/terminal-logs/`.
3. Implement the narrow portal documentation module, request contract, routes, and—only if the
   existing immutable provenance cannot represent current action history—one protected relation and
   migration. Reuse the document storage and existing legal/security borrower-safe selectors; do
   not grant internal permissions or call internal mutation/reveal/custody seams.
4. Run the focused backend tests to green and save output. Update the API contract with exact request,
   response, nondisclosure, validation, audit, and sensitive-field rules.
5. Add failing frontend service/component interaction tests for MP07 and MP13 covering loading,
   empty/blocked, 401/403/server/validation, server-owned actions, exact multipart upload, progress,
   success, one canonical refetch, and the no-fixture/no-sensitive-DOM regressions.
6. Wire both existing portal screens to the canonical API while preserving their current markup and
   design patterns. Remove inline business arrays, expose only advertised upload/re-upload and safe
   download actions, and never optimistically promote internal status.
7. Run focused frontend tests, typecheck, and lint during implementation; save green evidence and
   reviewable API response examples. Attempt the locally available frontend visual/browser feedback
   without fabricating screenshots if Chromium is unavailable.
8. Run all Ralph quality gates with the mandated backend interpreter, review the resulting diff
   against the slice/source and design rules, then save changed-files, risk assessment, review
   packet, final summary, progress/handoff/state/slice status, and sharpen the next one or two
   Not Started slices using only source material already opened.
