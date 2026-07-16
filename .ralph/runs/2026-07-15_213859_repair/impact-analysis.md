# Impact Analysis: CR-008

## Directly Affected Backend Module

- `sfpcl_credit/documents/models.py`: `DocumentTemplate.Meta.constraints` passes unordered sets to
  `approval_status__in` and `borrower_type__in`. Grep found the two affected definitions at the
  named `doc_template_approval_status` and `doc_template_borrower_type` constraints.
- `sfpcl_credit/documents/migrations/0002_documenttemplate.py`: historical state contains the same
  unordered collections. It is already-applied history and must remain byte-for-byte untouched.
- `sfpcl_credit/documents/migrations/`: the terminal documents migration state needs a new forward
  remove/add constraint migration so Django compares deterministic state on every hash seed.
- `sfpcl_credit/tests/`: add a documents migration-state regression that asserts both named
  constraints retain exact ordered collections and no unordered set/frozenset can re-enter their
  migration-facing `__in` values. Existing `test_document_templates_api.py` remains the targeted
  runtime/database-enforcement regression suite.

No endpoint, serializer, selector, or document-template module interface changes. The public
document-template GET/POST/PATCH behavior and all status/borrower validation remain unchanged.

## Other Backend Consumers and Blast Radius

- `legal_documents.modules.document_generation` selects approved `DocumentTemplate` rows and is an
  indirect consumer; generation selection behavior must remain unchanged.
- `documents.modules.document_templates` and `documents.selectors` consume the class-level allowed
  value catalogues and create/query template rows. Those catalogues are not being changed; the
  existing document-template API suite covers their validation and database writes.
- Legal checklist, stamp/notary, signature, PoA, tri-party, final-documentation, and portal tests
  create `DocumentTemplate` rows. They consume the same database constraints indirectly, but no
  code or interface in those modules changes. The full backend suite is the regression check for
  every such indirect consumer.
- CI and Ralph migration gates consume Django's terminal project state. A representative hash-seed
  matrix of the exact `makemigrations --check --dry-run` command is the added integration
  regression evidence for that consumer.

The schema operation briefly removes and recreates two check constraints when deployed, but it
does not alter columns, rows, indexes, allowed values, constraint names, or application APIs. The
blast radius is therefore migration-state/schema enforcement only.

## Frontend Impact

Grep and routing inspection show no frontend screen, component, or route consumes Django migration
serialization. No frontend file or behavior will change. `FRONTEND_DESIGN_RULES.md` remains fully
compliant because this CR introduces no UI, styling, copy, state, or route changes. Configured
frontend lint/typecheck/test/build gates will still be run.

## Regression Tests to Add or Run

- Documents module: add one focused regression covering exact ordered values for both named model
  constraints and the terminal documents migration state; run existing document-template API tests
  to preserve validation and database enforcement.
- Legal-document and process consumers: no new behavior is introduced at their interfaces, so no
  speculative per-consumer tests are added; the existing tests in each affected consumer module run
  unchanged as part of the full backend coverage gate.
- Migration/CI consumer: run the exact migration check under multiple fixed `PYTHONHASHSEED` values
  and require `No changes detected` for every seed.

This test allocation is intentionally local to the only changed module while the full suite guards
all indirect consumers, avoiding implementation-coupled duplicate tests in unrelated modules.
