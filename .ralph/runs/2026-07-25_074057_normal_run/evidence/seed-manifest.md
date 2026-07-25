# Critical UAT Seed Manifest

## Isolation and guards

- Commands run only when `ENABLE_DEMO_SURFACES`, `SFPCL_DEBUG=true`, and
  `SFPCL_ALLOW_E2E_SEED=true` are all effective.
- Playwright deletes and migrates the isolated `SFPCL_DB_PATH` before each run.
- Production-settings regression explicitly requires `seed_critical_uat_e2e_fixture` to refuse.
- Fixtures contain synthetic names, identifiers, accounts, references, and documents only.

## Deterministic command order

1. `seed_role_catalogue`
2. `seed_e2e_users`
3. `seed_portal_e2e_fixture`
4. `seed_epic_009_e2e_fixture`
5. `seed_epic_009_e2e_fixture --make-ready`
6. `seed_epic_009_e2e_fixture --prepare-transfer`
7. `seed_critical_uat_e2e_fixture`

The critical command is idempotent and adds exactly:

- two guarded actors (`e2e.uat.cfo@…`, `e2e.uat.accounts@…`);
- one ₹400,000 repayment schedule due 2026-06-30 on `LN-REAL-OWNER-001`;
- two quarterly statutory tasks with current accepted synthetic evidence;
- the CFO read permission needed to inspect the canonical approval matrix.

It does not create a test-only API or change production settings. The readiness and transfer
commands establish deterministic starting preconditions before the browser journey; no management
command or database transition runs after the test starts. Business transitions are executed
through existing authenticated UI/API actions. SAP, bank, communications, and storage remain the
existing manual/fake/local adapters; no live provider is called.

## Focused determinism evidence

- Backend: 3 tests passed, including double-run seed idempotency and production refusal.
- Frontend fixture selection and command order: 5 tests passed.
- Local Playwright attempt: one test selected, zero skipped; system Chrome closed during launch
  before a page existed. No screenshots were fabricated. Per the slice contract, the orchestrator's
  trusted two-run browser validation is authoritative for counts, runtimes, screenshots, and traces.
