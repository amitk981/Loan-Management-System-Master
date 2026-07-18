# Risk Assessment

Risk level: High

- Selected slice: `009K-disbursement-and-cfc-frontend-wiring`
- Mode: `normal_run`
- Recommendation: do not mark the slice complete; retain/requeue it to close S36 and obtain the
  declared browser evidence.

## Material risks

1. **High — S36 is not walkable in the UI.** The implemented workspace exposes assigned SAP
   confirmation (S37), readiness, initiation, CFC decision, transfer success, and advice (S38-S41).
   The existing S36 create endpoint requires a terminally sanctioned application and an active
   Senior Manager Finance assignee, but there is no bounded candidate/assignee projection for a
   Credit Manager. The implementation deliberately does not invent a raw UUID-entry workflow.
2. **High — trusted browser acceptance is unproven.** The sandbox denied the Vite listener with
   `EPERM`, and the in-app browser returned no available browser runtime. Consequently the required
   screenshots of blockers, initiation, CFC authorisation, and success were not captured. No
   screenshots were fabricated; see `evidence/visual-evidence.md`.
3. **Medium — financial workflow aggregation is security-sensitive.** The new endpoint masks bank,
   SAP, and external reference values, keeps protected identifiers only in server-owned fixed action
   payloads, uses canonical object-scope/readiness/current-disbursement decisions, and has focused
   permission tests. The orchestrator's authoritative full backend coverage gate remains required.
4. **Low — the existing frontend production bundle remains above Vite's 500 kB warning threshold.**
   The build passes and this slice does not add a package or a new styling system.

## Mitigations and evidence

- Stable idempotency keys are generated once per selected row/action and forwarded by the shared
  authenticated transport.
- The browser renders server-owned action descriptors and backend errors; it does not infer role,
  readiness, or payment authority.
- Focused red/green evidence and final gate logs are saved under `evidence/terminal-logs/`.
- No protected file or `docs/source/**` edit was made, and `git diff --check` passed.
