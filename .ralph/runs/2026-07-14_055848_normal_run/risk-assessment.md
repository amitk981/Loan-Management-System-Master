# Risk Assessment

Risk: **Medium**, matching the selected slice.

- Database: one additive migration creates `document_templates`; it changes or deletes no existing
  rows. Protected FKs, date/status/borrower checks, version uniqueness, and one-successor linkage
  constrain invalid history. PostgreSQL remains the authoritative concurrency gate.
- Authorization: catalogue reads and mutations use separate explicit permissions. A template-file
  reference additionally requires the existing file-download permission, but the catalogue response
  returns metadata only and does not grant or invoke a download.
- Consistency: create/successor, audit, and version-history writes share one transaction. PATCH locks
  the immutable predecessor; exact replay creates no duplicate business evidence. Approved effective
  overlap is rejected for the same document/borrower identity.
- Compliance: the implementation persists the source `draft`/`approved`/`retired` vocabulary and
  does not resolve disputed Annexure J/K/L lettering. It generates no borrower document and makes no
  readiness, approval, or routing decision.
- External effects: no deployment, real communication, file download, external service, dependency
  installation, commit, merge, or push was performed.

Residual risk: the five-request successor race is skipped under local SQLite and must pass the
slice-declared PostgreSQL acceptance run during independent validation. Approval-versus-active UI
vocabulary remains explicitly governed by A-095.
