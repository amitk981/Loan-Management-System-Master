# Export Masking and Download Evidence

- `frontend-export-red.log` records the pre-implementation failures for missing request, status,
  denial, and download behavior.
- `frontend-export-green.log` records 18 focused passing tests.
- `reportApi.test.ts` proves the canonical POST body, stable idempotency header, preserved job id,
  actor-scoped status path, same-origin audited download capability, and rejection of failed or
  foreign download paths.
- `ReportsMIS.test.tsx` proves queued, running, completed-without-capability, ready, failed,
  validation, permission-denial, masking notice, audited download, and retry-key reuse behavior.
- `RegistersHub.test.tsx` proves export permission visibility, backend job identity, expired
  capability gating, and final owned mock removal.
- The trusted browser spec proves the request/status/download network path and retains the two
  named screenshots when Chrome is available to trusted validation.

