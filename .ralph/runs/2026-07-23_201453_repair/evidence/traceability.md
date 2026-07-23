# Repair Evidence Traceability

| Repair behavior | Evidence |
|---|---|
| Original validator reached the closure row but could not find lowercase `issued` | Prior run `evidence/terminal-logs/trusted-browser-acceptance-1.log` |
| Exact repaired Playwright spec parses and collects one test | `terminal-logs/member-portal-communications-collection.log` |
| MP19-MP24 focused component behavior remains green | `terminal-logs/frontend-portal-communications-focused.log` |
| Type safety, lint, and production bundle remain green | `terminal-logs/frontend-typecheck.log`, `terminal-logs/frontend-lint.log`, `terminal-logs/frontend-build.log` |
| Candidate has no whitespace errors | `terminal-logs/repair-diff-check.log` |
| Agent-side Chrome infrastructure closes before page creation; no screenshot claimed | `terminal-logs/member-portal-communications-e2e-run-1.log`, `terminal-logs/browser-infrastructure-reprobe.log` |

The source-backed UI contract remains unchanged: MP20 shows borrower closure/NOC/security status
(`docs/source/screen-spec-member-portal.md` MP20), MP23 exposes notification read state (MP23), and
portal grievances use the model-bounded category vocabulary. Independent trusted validation owns
the two passing browser runs and screenshot manifests.
