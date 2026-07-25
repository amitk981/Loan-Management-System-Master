# Deployment Performance Smoke

The local-server deployment smoke completed successfully and bounded every collection
read to `page=1&page_size=1`.

The probes were:

1. liveness;
2. readiness;
3. login plus current-user authentication;
4. dashboard;
5. member directory, one row;
6. loan applications, one row;
7. approval cases, one row;
8. documentation-readiness report, one row;
9. default cases, one row;
10. compliance tasks, one row;
11. audit logs, one row.

The application/approval, documentation/security/disbursement,
servicing/default/closure/compliance, and report/export/audit module groups are each
represented by at least one critical workflow read. The complete command returned in
0.87 seconds in the isolated local evidence run, including token hashing and all twelve
HTTP requests. No individual list request is
unbounded, and the integration test proves representative business-model counts are
unchanged.

Evidence:

- `terminal-logs/smoke-check-local-transcript.log`
- `terminal-logs/smoke-local-server-final.log`
- `terminal-logs/backend-focused-final.log`

This is a bounded functional smoke, not a substitute for the separately completed
012F2 load/performance readiness evidence.
