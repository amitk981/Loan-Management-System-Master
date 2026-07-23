# Execution Plan

Selected slice: `011O-auditor-read-only-views`

## Boundary

Implement one focused Internal Auditor read-only surface for Epic 011. Reuse the existing
default/recovery, closure, compliance/KYC, archive, and grievance public read services; add only the
smallest missing aggregate read projection. Do not add audit observations, exports, evidence-review
authority, operational workflows, new visual language, migrations, dependencies, or Epic 012 work.

## Source-backed contract

- Internal Auditor uses the existing `audit_readonly` object scope and read permissions.
- Auditor GET/list/detail/query responses expose masked summaries, immutable workflow/audit
  references, and authorised evidence metadata, with no mutating `available_actions`.
- Restricted downloads continue through the existing permission, object-scope, reason, audit, and
  signed-download path.
- Every Epic 011 mutation remains forbidden, including compliance evidence review.
- Other broad-read roles do not inherit auditor scope; existing staff and borrower filters remain
  unchanged.
- The slice citation `docs/source/test-plan.md` §§37.2-37.5 does not exist in that file. The
  applicable source test contracts are §§13.17-13.20, §14.11, §§15.3-15.5, §18.2, and the slice's
  explicit acceptance matrix; no business rule is inferred from the bad section reference.

## Permission matrix to prove

| Surface | Auditor GET/list/detail | Auditor mutation | Evidence/download |
|---|---|---|---|
| Default, assessment, extension, note, recovery | Allowed with active `audit_readonly`; masked and action-free | 403 | Metadata only unless the existing classified download contract authorises access |
| Closure, NOC, security return, archive | Allowed with active `audit_readonly`; immutable history included | 403 | Existing classified/signed download contract only |
| Controls, tasks, evidence, calculations, KYC reviews | Allowed read-only; no review action | 403, including evidence review | Existing category and object-scope rules remain authoritative |
| Grievances | Allowed read-only with protected fields masked/safe | 403 | Existing supporting-evidence rules only |
| Borrower and non-auditor broad readers | Existing object filters unchanged | Existing authority unchanged | Existing classification unchanged |

## TDD sequence

1. Inventory the current Epic 011 URL/service/test surfaces and identify only missing auditor reads
   or action leakage.
2. RED: add one public-interface backend behavior test for the focused auditor aggregate/read
   projection, including active scope, masked/action-free output, immutable references, and
   representative Epic 011 families. Save the failing output.
3. GREEN: implement the minimum read projection/permission changes to satisfy that behavior and save
   focused passing output.
4. RED→GREEN one behavior at a time for the mutation method matrix, inactive/missing auditor scope,
   evidence-review denial, and reverse-consumer object-scope regression.
5. Read `docs/working/FRONTEND_DESIGN_RULES.md`, then RED→GREEN focused component/route tests for
   populated, empty, error, and unauthorised states and for the absence of mutation controls.
6. Implement the focused route/view and API client using existing cards, filters, status badges,
   tables, timeline, evidence-link, and state patterns.
7. Implement the declared Playwright spec and exact populated/empty/unauthorised screenshots; run
   it locally when Chromium is available and retain honest output.

## Focused validation and evidence

- Backend: use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every command; run only the new
  focused module plus directly impacted Epic 011 permission/read suites, `manage.py check`, and
  `makemigrations --check`.
- Frontend: run the focused Vitest file, then frontend tests, typecheck, lint, and build as required.
- Browser: run the exact declared Playwright spec against the localhost server if launch succeeds;
  never fabricate screenshots.
- Save red/green and gate logs under
  `.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/`.
- Finish `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review result
  exactly to `Ready for independent validation`.
- Do not edit protected paths, source documents, slice status, state/progress, changed-files, or
  mechanical handoff facts. Do not run git add/commit/push.
