# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- PASS: first manual-recovery trusted browser run passed 2/2 tests.
- PASS: second manual-recovery trusted browser run passed 2/2 tests.
- PASS: all four declared browser screenshots exist and are non-empty.

Machine-readable reports:
- `evidence/terminal-logs/trusted-browser-manual-recovery-1.json`
- `evidence/terminal-logs/trusted-browser-manual-recovery-2.json`

The earlier `trusted-browser-acceptance-1.log` and `trusted-browser-acceptance-2.log` files retain
the pre-recovery failures for diagnosis history.

Declared specs:
- e2e/member-portal-documentation-actions.e2e.spec.ts
- e2e/member-portal-deficiency-response.e2e.spec.ts
Declared screenshots:
- portal-documentation-upload-modal.png
- portal-documentation-complete-upload-denied.png
- portal-deficiency-mobile-response.png
- portal-deficiency-resubmitted.png
