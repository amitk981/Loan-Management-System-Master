# Legacy prerequisite provenance repair

Forward and reverse behavior is verified by
`AppraisalHistoryHardeningMigrationTests` in
`evidence/terminal-logs/06-hardening-migration-green.txt`.

| Fixture before migration | Provenance after migration | Copied JSON |
|---|---|---|
| Both exact same-application success audits before preparation; no later audit; source times before preparation | `verified` | Preserved exactly |
| Eligibility audit missing | `legacy_unverified` | Preserved exactly |
| Both audits missing | `legacy_unverified` | Preserved exactly |
| Later eligibility success audit | `legacy_unverified` | Preserved exactly |
| Source timestamp after preparation | `legacy_unverified` | Preserved exactly |
| Assessment IDs belong to another application | `legacy_unverified` | Preserved exactly |
| Already `legacy_unverified` | `legacy_unverified` | Preserved exactly |

One complete existing latest reviewed decision is backfilled with
`history_provenance = legacy_latest_only`. No earlier cycle is invented. Reverse migration drops
the derived history table but deliberately retains conservative `legacy_unverified` labels, because
restoring false historical verification would recreate the defect.
