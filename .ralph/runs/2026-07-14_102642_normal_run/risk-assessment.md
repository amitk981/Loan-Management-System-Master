# Risk Assessment

Risk level: High (owner standing approval; no veto recorded).

## Material risks and controls

- **Authority bypass:** direct task/module callers previously bypassed generate/read permission and
  application scope. The public module now enforces active actor, exact permissions, template-
  reference authority, and canonical application scope before validation/business reads. Direct and
  HTTP denial matrices assert zero bytes/rows/audit/workflow evidence.
- **Dependency reversal:** moving the model/module could leave two writable owners or make the
  foundation package import business apps. Runtime ownership and an isolated import probe prove one
  `legal_documents` owner and a business-owner-free `documents` package.
- **Migration/data loss:** the single migration changes Django state without creating/copying/
  dropping `loan_documents`. A migration-executor test retains an actual pre-transfer row and fresh
  migration produces exactly one table.
- **False loan reference:** the source requires a nullable FK but Epic 009's aggregate is absent.
  A database check accepts only `NULL`; A-102 assigns the protected FK replacement to 009C.
- **Replay/race regression:** application locking, replay identity, stored output cleanup, and one
  evidence set are retained. The five-request PostgreSQL race passed twice after final review fixes.

## Residual risk

Rendered DOCX/PDF content and the real M05 missing-term blocker remain explicitly owned by 008B3.
This slice does not claim legal output readability or a complete M05-to-M06 path.

Manual review required: normal High-risk audit review only; all standing controls and gates pass.
