# Standards Axis

Boundary: `git diff 33f5e5df...c7c81e92`, covering CR-015, 010MB, and 010N product
changes while excluding mechanical Ralph bookkeeping.

- High: `InterestManagement.tsx` loads one page of 100 accounts and submits those ids as the
  complete monthly-accrual population. `docs/working/API_CONTRACTS.md` says omitted ids mean the
  complete bounded scoped set and explicit ids are selected batches. This violates the backend-owned
  financial-decision rule in `FRONTEND_DESIGN_RULES.md` and the owner-seam direction in source
  `codebase-design.md` §42.3.
- High: CR-015's `_invoice_status_at_cutoff` checks nonexistent `InterestInvoice.created_at`; the
  model retains `generated_at`. Its synthetic private-helper regression omits the real field and
  masks post-cutoff invoice admission, contrary to the finalizer's immutable-source and public-test
  contract.
- High: the global-search coordinator reads sensitive security-instrument owners without their
  canonical authority. A CFO with member read but no blank-cheque authority can resolve a member by
  exact cheque number, contrary to source auth §§21–22 and the slice's nondisclosure requirement.
- Medium, grouped under the High interest root: client permission arrays control mutation visibility,
  and the owned Playwright contract replaces interest/DPD/reminder reads rather than proving the
  canonical domain seams. Backend denial still prevents direct privilege escalation.
- Medium, grouped under the High search root: application scope is evaluated after the 100-row cap,
  independently authorised groups depend on member-read-derived ids, and submitted sensitive values
  remain duplicated in client state.

The terminal finalizer's retained `fixture.setUp()` call is a hard binding-contract breach and is
carried under `ROOT-010-SERVICING-OWNER-SEAM` rather than counted as a new root.
