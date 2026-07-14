# Ralph Handoff

## Last Run

2026-07-14_081204_normal_run

## Current Status

008A2 is complete. A database-backed identity row serializes every template create/successor before
effective-range checks, so concurrent overlapping first approved versions retain one winner and
one evidence set. The documents-owned template-source boundary now requires singular immutable
global upload provenance, matching sensitivity/metadata, and dedicated reference authority;
template read/manage and file download do not imply reference or expose storage actions.

Catalogue reads are selector-owned and writes receive transport-neutral request metadata. The
public borrower-template resolver maps only `individual_farmer`; `fpc`, `producer_institution`, and
unknown values fail configuration-required until governance confirms the source FPO mapping.

## Validation

Evidence is in `.ralph/runs/2026-07-14_081204_normal_run/evidence/`. Frontend build, typecheck,
lint, and all 287 tests pass. Django check/migration sync and all 710 backend tests pass with 21
expected skips at 93% coverage. The focused 39-test documents/catalogue suite passes, and both
PostgreSQL template races pass twice.

## Next Run

Run sharpened 008B. Generation must consume the public template-source reference decision and
borrower-variant resolver, require the dedicated reference permission alongside generation/object
scope, and implement its own replay identity without duplicating the catalogue lock.
