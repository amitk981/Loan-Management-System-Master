# Ralph Handoff

## Last Run
2026-07-05_091741_architecture_review

## Current Status
Architecture review completed for the four slices merged since review commit `559b1b7`:
- `002K2-demo-tracer-permission-isolation`
- `003A-audit-log-foundation`
- `003B-workflow-event-foundation`
- `003C-document-metadata-and-storage-adapter`

## What Completed
Review findings were appended newest-first in `docs/working/REVIEW_FINDINGS.md`.

Passes:
- `002K2` closed the demo tracer permission leak. `demo.tracer@sfpcl.example` now uses
  local/dev-only role `local_demo_tracer_user` with exactly `tracer.lifecycle.run`, while
  non-demo `sales_team_user` stays permission-neutral after guarded demo seeding.
- `003A` exposes `GET /api/v1/audit-logs/` over the existing `identity.AuditLog` model with
  standard pagination, filters, `actor: null` for system rows, and `audit.audit_log.read`.
- `003B` moved canonical workflow-event ownership to `sfpcl_credit.workflows` without
  recreating the physical `workflow_events` table, preserved tracer `workflow_event_id`
  responses, and added protected `GET /api/v1/workflow-events/`.
- `003C` added generic `document_files` metadata, local file storage, checksum capture,
  `POST /api/v1/document-files/`, `documents.file.upload` permission gating, and upload audit.

Finding:
- Medium architecture drift: protected backend views now repeat the same session-bound Bearer
  parser in `admin_views`, `identity/views`, `tracer/views.py`, `audit_views`, `workflows/event_views`,
  and `documents/views`. No response-contract bug was found, but the duplication should be closed
  before another protected document endpoint is added.

Working docs updated:
- `docs/slices/003D-secure-document-download-with-audit.md` now requires extracting/reusing a
  shared bearer-session auth helper before implementing document download, and regression tests
  proving existing `401` envelopes remain unchanged.
- `docs/slices/003E-versioned-configuration-shell.md` now explicitly traces functional-spec
  M01-FR-001, M01-FR-002, and M01-FR-015, and defers M01-FR-003 through M01-FR-014 unless their
  neutral storage fields are implemented without policy-rule invention.
- `docs/working/digests/epic-003-audit-documents-config.md` includes distilled extracts for
  document download permission/audit and loan-policy configuration functional IDs.

## Evidence
See `.ralph/runs/2026-07-05_091741_architecture_review/`:
- `evidence/terminal-logs/review-window-git-log.log`
- `evidence/terminal-logs/review-window-diff-stat.log`
- `evidence/terminal-logs/review-window-files.log`
- `evidence/terminal-logs/git-diff-check.log`
- gate logs saved under `evidence/terminal-logs/` after this review run.

## Current Blocker
None.

## Next Recommended Action
Run `003D-secure-document-download-with-audit`. It should reuse 003C `DocumentFile` and
the local storage boundary, require `documents.file.download`, write download/access audit,
avoid loan-document/checklist UI, and first remove the repeated protected-view bearer-auth
parser by introducing one shared backend helper.
