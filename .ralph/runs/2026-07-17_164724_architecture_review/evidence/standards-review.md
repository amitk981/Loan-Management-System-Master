# Standards Review

Independent pass over `git diff f35e0fc7...dbccea9c` using codebase-design §§6.5, 16.3-16.4,
22, 26-28, 36-38, 42; API §§3, 6-8, 31, 45; data-model §§19.3-19.4, 29-30, 34; and auth
§§18, 30-31.

- High: successful transfer omits atomic register/pending-communication/post-disbursement completion
  truth required by data-model §34 and the workflow-owned advice trigger.
- High: advice provider acceptance happens before database persistence, while adapter idempotency is
  stored only in a newly constructed instance and includes a random communication id.
- High: Critical source-bank changes retain only a reason hash and mislabel request/provisioner as
  approval, leaving no reviewable CFG-001 rationale.
- Medium: general audit evidence duplicates the full borrower email already held in the protected
  communication row.

Retained tests otherwise contain substantive state/audit assertions and repeated PostgreSQL races;
their blind spots are provider-acceptance rollback, post-success source completion, recoverable
configuration rationale, and minimized advice evidence.
