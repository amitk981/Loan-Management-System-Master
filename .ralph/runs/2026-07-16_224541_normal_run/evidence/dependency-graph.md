# SAP Dependency Graph

Executable import assertions in the focused suite confirm:

```text
finance ───────► sap_workflow
loans ─────────► sap_workflow
disbursements ─► sap_workflow
sap_workflow ──X finance
```

The canonical models, current-evidence decision, Annexure storage, send/completion policy, and
Manual/Fake/Future adapter contract remain in `sap_workflow`. No schema, migration, real SAP/email
transport, or parallel Finance selector was introduced.

Evidence: the dependency assertion is included in
`terminal-logs/22-focused-sap-tests-final-green.txt`; repository inspection found no executable
`sap_workflow` import of `finance` outside the historical state-only migration vocabulary.
