# Risk Assessment

Risk level: High

The slice moves money-state truth: it records the bank reference, funds balances, and activates a
loan account. Owner standing approval applies and no revocation is recorded. Controls are exact
009F2 approval/evidence reconciliation under row locks, active governed actor scope, Critical
permission, maker/checker restrictions, normalized database-unique UTR, one transfer per account,
aggregate constraints, atomic funding/history/audit/workflow writes, and nondisclosing failures.

Residual risk is limited to integration semantics outside this slice: the transfer is a manual
bank-confirmation record and does not call RBL. Advice, Loan Register, checklist, repayment,
schedule, interest, communication, and borrower-visible truth remain deliberately absent. Twice-run
five-caller PostgreSQL races and stale/replay tests support the concurrency boundary. No dependency,
frontend, protected-file, source-document, or external-system change was made.
