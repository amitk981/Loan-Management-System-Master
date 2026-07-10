# Risk Assessment

Risk level: High

- Selected slice: 005I5-application-ownership-and-nominee-authority-hardening
- Mode: normal_run
- Standing approval: applicable; no `[revoked]` entry exists for this slice.
- Manual review required: yes, because the change affects object presentation, nominee legal-age
  authority, blocked mutation integrity, and portal/staff contracts.

## Main risks and controls

- Ownership misrepresentation: controlled by returning `assigned_owner: null` for both staff list
  and detail and proving staff-created and portal-created paths. No role/status/stage fallback exists.
- Divergent legal-age decisions: controlled by one public backend module used by intake, submit,
  completeness/reference, and eligibility. Existing messages and age threshold are unchanged.
- Partial mutation on validation failure: controlled by substantive staff PATCH and portal
  create/PATCH tests that compare serialized detail and success audit/workflow counts.
- Sensitive nominee disclosure: controlled by metadata-only serializers plus staff/portal render
  assertions excluding PAN, Aadhaar, hashes, tokens, and reveal controls.
- Frontend regression: controlled by lint, typecheck, 107 unit tests, build, and three compiled
  Playwright browser specs. Local browser execution was sandbox-blocked because the web server could
  not bind a port; this is recorded for orchestrator execution and does not weaken mandatory gates.

## Change size

- 21 non-run-artifact files listed in `changed-files.txt`; no dependency or migration added.
- Tracked diff before final artifact updates: 358 additions / 141 deletions; comfortably below
  Ralph's 2,000-line and 30-file limits when run evidence is excluded as configured.
- Protected paths and `docs/source/` are unchanged.
