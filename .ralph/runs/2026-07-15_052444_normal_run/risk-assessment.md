# Risk Assessment

Risk level: High.

- Selected slice: 008K3-final-checklist-evidence-closure
- Mode: normal_run
- Manual review required: no; standing High-risk approval applies and no veto is recorded.

This slice changes final legal-document completion and approval authority plus cross-owner evidence
reconciliation. A defect could approve stale, synthetic, cross-application, or status-only evidence,
misattribute a multi-role actor, or retain the wrong concurrent request as the legal winner.

The change fails closed under checklist and source-row locks. It checks exact current documents,
signer sets, security-package parties, canonical terminal WorkflowEvents, completion action/history
cardinality, item verifier/time/remarks, current approval case, retained evidence body and digest,
and stage role. Blank-cheque output remains `******`; no encrypted values or reveal callbacks cross
the coordinator. Errors create no approval action/audit/version/workflow identity.

The adverse matrix covers missing/status-only and extra completion evidence, synthetic cheque
history, changed verifier/remarks, stale cycle, forged workflow, wrong PoA amount, extra signer,
replay, roles, permissions, and unrelated objects. PostgreSQL races run twice and query every loser
request across success ledgers. No schema, dependency, external call, readiness, disbursement,
loan-account, protected file, source document, or frontend product code changed.
