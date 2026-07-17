# Risk Assessment

Risk level: High (approved by the standing-approval/veto policy).

- Selected slice: `009E-payment-initiation-by-senior-manager-finance`
- Mode: `normal_run`
- Financial/state risk: initiation is a critical money workflow boundary. Mitigations are exact
  positive amount equality with immutable loan terms, sanctioned/unfunded account locks, bounded
  database statuses, a positive-money constraint, and explicit absence of balance/status/transfer
  mutations.
- Authority risk: the owner re-locks an active persisted Senior Manager Finance actor, verifies the
  canonical Critical grant, and relies on 009D3's newest-SAP-assignee scope. The future checker is a
  distinct CFC role queue; role or permission alone does not create loan scope before initiation.
- Readiness/evidence risk: all 23 checks must be present, ordered, and passing. The frozen digest
  contains only code/status and excludes `evaluated_at`; exact SAP request/code, borrower-bank
  decision, and governed source-bank ids are locked and retained separately.
- Duplicate/concurrency risk: raw idempotency keys are hashed; exact replay re-evaluates current
  evidence and writes nothing; changed replay and second active initiation conflict. A conditional
  unique constraint and twice-run fresh PostgreSQL five-caller tests retain one complete winner.
- Privacy risk: borrower/source links are protected FKs. Public output, audit/workflow/task, and
  evidence examples contain safe ids/digests only; tests assert encrypted values and account hashes
  do not leak. The source selector returns no plaintext.
- Integration risk: MVP remains a manual RBL-portal record. No bank API, UTR, authorisation,
  transfer, communication, funding, activation, register update, or checklist signature occurs.
- Schema risk: one additive migration creates the disbursement aggregate and constraints. Existing
  nullable-join locks were narrowed to `of=("self",)` for PostgreSQL without changing selected rows.
- Residual operational risk: a verified active SFPCL-owned RBL `bank_accounts` row must be governed
  and provisioned out of band; missing or duplicate active rows intentionally block readiness.
  Authoritative complete-suite coverage and frontend gates remain the orchestrator's independent
  acceptance step, as required by the run prompt.

No protected file, source document, dependency, external service, or real financial/personal data
was changed or used.
