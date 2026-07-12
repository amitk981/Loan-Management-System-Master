# Execution Plan

Selected slice: 006Z8-portal-limit-provenance-module-and-interaction-closure

Mode: repair

1. Preserve the quarantined implementation and reproduce the trusted-browser failure from the
   saved external logs with the smallest agent-runnable interaction seam available in the sandbox.
2. Inspect only the portal authentication/navigation fixture and existing routed portal tests,
   then rank and falsify causes of the repeatedly detached `New Application` control.
3. Add a focused regression assertion before the fix where the existing test seam can express the
   external failure; save red output under `evidence/terminal-logs/`.
4. Make the smallest change to the declared Playwright contract needed to enter the real routed
   MP05 screen deterministically, without changing production behavior or the slice's assertions.
5. Run the focused regression green, Playwright collection, and all configured frontend/backend
   gates that are available in the sandbox. Record the expected Chromium sandbox limitation
   honestly; independent Ralph validation remains authoritative for the two browser runs.
6. Refresh repair evidence, changed-files, risk assessment, review packet, final summary, state,
   progress, handoff, and the selected slice status without modifying protected files or git state.
