# Ralph Handoff

## Last Run
2026-07-13_190107_normal_run

## Current Status

007H creates one immutable Credit Sanction Register row for each approved or rejected terminal
case inside the locked approval-action transaction. Approved rows link the §15.5 sanction decision;
rejected rows preserve terminal case/action facts with a null sanction link under A-088. Partial,
returned, conflict-blocked, and General Meeting-gated outcomes create no row. The register row
freezes the 15 source fields and references the exact terminal sanction workflow event plus an
attributable creation audit.

The projection uses only the terminal case's application/member, verified loan-limit snapshot,
reviewed appraisal, effective action authority, one-to-one 007F exception, frozen 007E conflict/
abstention facts, and frozen 007G General Meeting relation. It never selects latest evidence by
application. Queryset and instance mutations are blocked; the read adapter exposes no row mutation
route. CFO, Director, Company Secretary, and Internal Auditor receive the dedicated register grant.

The §25.8 sanction-decision GET returns 404 before approval and after rejection. The §25.9 register
GET supports bounded pagination plus exact decision and A-086 April-March `FYyyyy-yy` filtering.
OC-002/A-087 keeps Annexure K/template code absent. Independent review found and closed bulk
immutability, 255-character borrower-name, and abstainer-as-approver defects.

## Validation

Retained RED/GREEN logs cover approved/rejected generation, exact same-case related references,
filters/pagination/permissions/read-only routes, financial-year range validation, seeded reader
roles, and review repairs. Frontend build/typecheck/lint and all 208 tests pass. Backend check and
migration sync pass; the full 669-test suite passes with 19 expected PostgreSQL-only SQLite skips
and 93% coverage.

## Next Run

The four-slice architecture-review cadence is now due. After that review, run
`007I-sanction-workbench-ui`; its run-ahead section is sharpened for the separate case, sanction,
and register permission/read contracts. `007J-registers-and-approval-matrix-frontend-wiring` is
also sharpened for frozen nested references, FY filters, and the borrower/internal authority seam.
