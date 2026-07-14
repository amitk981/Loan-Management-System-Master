# Review Packet: 2026-07-14_102642_normal_run

## Result

Ready for independent Ralph validation.

## Slice

`008B2-legal-document-generation-boundary-closure`

## Standards review

The isolated review found: (1) malformed payload validation preceded authority; (2) dependency
proof was ownership-only; (3) shallow `can_generate`/`can_read` helpers were unused and did not
check active status; and (4) Ralph artifacts were incomplete. The first three were fixed with
authority-first ordering, a guarded import/transport probe, and helper removal. This packet and the
remaining run artifacts close the fourth. No route, envelope, selector, migration, or loan-account
integrity violation remained.

## Spec review

The isolated review found the same authority-order defect plus partial zero-read/zero-write denial
and dependency evidence. Tests now cover malformed missing-generate, missing-reference, inactive,
and out-of-scope calls across template/frozen/file/storage/model/audit/workflow surfaces. The
foundation package is imported in isolation while application/approval/legal imports are blocked;
the legal module exposes no request parameter or imported view/HTTP module. Generated `__pycache__`
files are ignored runtime artifacts and are absent from `git status`/changed files.

## Source-to-code-to-test traceability

- Codebase-design §§14.1/36.2 say legal generation belongs in `legal_documents` and foundation
  `documents` must not depend on application/approval owners. Code moves the model/module/views and
  selector accordingly; `LegalDocumentDependencyDirectionTests` and the guarded import probe verify it.
- API §§3/26.4-26.5 require backend authority and unchanged v1 contracts. Module entry points enforce
  active actor, generate/read permission, template reference, and application scope; API/direct
  parity and denial tests verify the same exact contracts.
- Data-model §§16.3/34 require nullable relational integrity. The state-only migration preserves the
  retained table/row and adds the nullable-only transition; migration retention, fresh migration,
  and database rejection tests verify it.
- Slice requirement 6 requires exact replay and one evidence set. Focused replay tests plus two
  final PostgreSQL five-request races verify one loan document/file/audit/workflow result.

## Gates

- Backend: Django check and migration sync pass; 732 tests pass with 22 expected skips; coverage 93%.
- PostgreSQL: five-request replay race passes twice after review fixes.
- Frontend (unchanged): build, typecheck, lint, and 293 tests pass.
- Fresh migration and `git diff --check` pass.

## Recommended next action

Run independent Ralph validation and, if green, let the orchestrator commit/merge. Next slice: 008B3.
