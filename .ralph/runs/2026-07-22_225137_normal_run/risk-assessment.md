# Risk Assessment

Risk level: High

- Selected slice: 011I-security-return-and-cdsl-unpledge-tracking
- Mode: normal_run
- Manual review required: independent Ralph validation is required before commit.

## Risk Controls

- Applicability, package identity, and item identity are derived from the financially closed loan and existing security owners; caller-declared applicability is rejected.
- The closure row is locked for every write. One aggregate per closure, unique request keys, and explicit versions protect duplicate and stale transitions.
- Pending items may advance, while returned/released/completed/rejected outcomes are terminal. The aggregate completes only when every applicable item is terminal-success and a verified restricted acknowledgement exists.
- Physical recipient/time/acknowledgement and CDSL PSN/URF/DP/outcome/completion evidence are validated before writes. Evidence must be a verified restricted/confidential LoanDocument for the same application.
- BO account values are never copied or revealed; responses reconstruct masked last-four projections from the CDSL owner.
- Aggregate, item, request, denial, and CDSL-result evidence is audited; public model mutation/deletion is blocked outside the owner module.

## Residual Risk

- This is a schema/routing/high-control change, so the orchestrator's independent High-risk complete-suite coverage lane remains mandatory. The agent deliberately ran focused and reverse-consumer suites only.
- The adapter records governed manual DP outcomes; it does not perform or claim a real depository request, matching the slice non-goal.
- No frontend was changed; staff/portal aggregate UI remains explicitly outside 011I.

## Assessment

No unresolved implementation blocker or invented business rule remains. One migration was added, within the configured limit. Final local and PostgreSQL evidence is green.
