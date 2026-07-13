# Execution Plan

Selected slice: 004E-witness-shareholder-validation

1. Preserve the nested HTTP endpoint as the only public interface. Keep validation, protected
   identity persistence, verification derivation, and audit creation behind one applications-module
   seam; reuse the local database and existing object-access/audit adapters without adding ports.
2. Add one public API test for the qualifying shareholder/KYC create path and run it to RED. Add the
   minimum model, migration, route, view, service behavior, and narrow catalogue permissions to turn
   it GREEN; save both outputs under `evidence/terminal-logs/`.
3. Add remaining behaviors incrementally: application-isolated list; non-shareholder and KYC/name
   rejection; missing records and malformed/forged payloads; permission and object-access denial;
   read-only roles; protected persistence, masked output, verification metadata, and audit hygiene.
   Run each focused test after introduction and retain concise red/green evidence.
4. Update the working API contract and assumption ledger. Generate the migration, inspect it, and
   run focused backend tests plus Django check and migration-sync checks.
5. Run every configured backend/frontend quality gate with the mandated backend interpreter. Save
   terminal logs and self-contained API response evidence.
6. Review the diff for slice boundaries and protected paths; write changed-files, risk assessment,
   review packet, and final summary; update slice status, Ralph state/progress, handoff, and sharpen
   the next one or two eligible Not Started slices using only already-opened source material.

Risk controls: no frontend or application-state change; no plaintext identity values in response,
audit, or schema; verification is derived exclusively from persisted member/KYC/shareholding facts;
all reads/writes require both a witness-specific permission and application object access.
