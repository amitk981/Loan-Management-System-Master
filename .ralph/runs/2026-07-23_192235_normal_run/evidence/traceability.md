# Evidence Traceability

| Behavior | Evidence |
|---|---|
| Grievance required fields, own create/list/detail, foreign nondisclosure | `portal-grievances-red.log`, `portal-grievances-green.log`, `portal-communications-focused-green.log` |
| Direct-user notification list/read and foreign denial | `portal-notifications-red.log`, `portal-notifications-green.log`, `backend-portal-communications-regressions-final.log` |
| Own NOC notice/closure projection, foreign isolation, signed audited download | `portal-notices-closure-red.log`, `portal-notices-closure-green.log`, `backend-portal-communications-regressions-final.log` |
| MP19-MP24 loading/empty/error/submit/detail/resolution/read/download states | `frontend-portal-communications-focused-final.log` |
| Type safety, lint, production bundle | `frontend-typecheck-final.log`, `frontend-lint-final.log`, `frontend-build-final.log` |
| Django/migrations/diff/protected files/line budget | `final-static-gates.log` |
| Trusted-browser infrastructure failure without fabricated screenshot | `browser-infrastructure-reprobe.log`, `member-portal-communications-e2e-run-1.log`, `member-portal-communications-e2e-run-1-retry.log` |
