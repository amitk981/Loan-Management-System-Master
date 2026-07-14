# Execution Plan

Selected slice: 008I2-security-poa-owner-and-read-contract-closure

1. Inspect the retained `security_instruments`/`legal_documents` PoA models, modules, routes,
   migrations, permission catalogue, object-scope helpers, and existing public/PostgreSQL tests.
   Preserve database tables, model labels, UUIDs, protected relations, route shapes, replay,
   terminal evidence, checklist projections, and public generation behavior.
2. RED: add focused public-interface regressions for exact ₹500 activation (including missing,
   null, ₹1, ₹499.99, and ₹500.01 zero-write failures), the documented scoped read-role matrix,
   read-only mutation denial, and AST/migration ownership invariants. Save the failing output under
   `evidence/terminal-logs/`.
3. GREEN, one behavior at a time: move the complete PoA policy implementation to
   `security_instruments.modules.power_of_attorney`, leave only a policy-free compatibility import
   if an existing external caller requires it, enforce the PoA-specific exact stamp value inside
   the atomic activation boundary, and separate masked package reads from Compliance/CS mutation
   authority while preserving authority-first nondisclosure.
4. Run the focused SQLite regressions after each vertical red/green cycle, then run the existing
   PoA/security package/module-boundary suites. Save green output and compact public API examples,
   module dependency proof, and retained migration/table proof in the run evidence folder.
5. Run the declared PostgreSQL exact/changed activation and downgrade races twice with the Ralph
   backend interpreter/settings, capturing terminal winner and loser evidence. Then run configured
   backend check, migration sync, coverage suite, and frontend lint/typecheck/tests/build gates.
6. Review the diff for scope, protected paths, retained contracts, and line/file limits. Sharpen
   the next one or two Not Started slices only from already-opened Epic 008 material. Write
   `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update the
   executed slice, state, progress, handoff, API contract ledger if changed, and durable digest.
