# Ralph Handoff

## Last Run

2026-07-14_193053_normal_run

## Current Status

008G2 is complete. A material pending stamp/notary/signature editor becomes the current maker and
the previous maker remains in immutable evidence; exact replay remains zero-write. New positive or
adverse stamp/notary outcomes and mismatch resolutions have database-enforced non-null distinct
maker/checker ids. Only migrated null-maker history receives the explicit legacy marker and cannot
be changed or supply new downstream truth.

HTTP adapters now check action authority before strict parsing and call lower request contracts;
business modules no longer import the HTTP serializer adapter. §26.6 returns the exact §6.3 action
shape with durable workflow identity, unresolved mismatch overwrite returns
`SIGNATURE_MISMATCH_UNRESOLVED`, and verified tri-party execution freezes/guards consumed signature
ids, names, makers, and signing times. The positive path crosses genuine public DOCX/PDF generation.

The security-package/PoA owner remains in `legal_documents`; 008F2 is still required to move it to
`security_instruments`, consume canonical terminal sanction truth, and close terminal activation.
008H remains correctly dependent on 008F2.

## Validation

Evidence is in `.ralph/runs/2026-07-14_193053_normal_run/evidence/`: five retained RED/GREEN cycles,
public generation tracer, dependency/action/error proof, all 45 Stage-4 tests on SQLite and
PostgreSQL, four twice-run tri-party races, 810 backend tests at 93% coverage, and all configured
frontend gates (293 tests).

## Next Run

Run 008F2, then 008H. Do not extend SH-4/CDSL on the current legal-documents-owned security seam.
Reuse 008G2 current-maker, legacy-marker, consumed-evidence, lower request-contract, and §6.3 action
semantics. A-101 still blocks the real M05-to-full-Term-Sheet path; no checklist, package,
repayment, file, or disbursement-readiness claim changed.
