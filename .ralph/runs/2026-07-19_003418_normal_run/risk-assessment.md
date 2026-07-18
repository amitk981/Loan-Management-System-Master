# Risk Assessment

Risk level: High (declared by slice; standing owner approval applies)

- Selected slice: `009I2-portal-disbursement-stage-and-visual-closure`
- Mode: `normal_run`
- Database/migration impact: none; Django reports no model changes.

## Material risks and controls

- Financial-stage integrity: the borrower timeline now composes six owner decisions. Completion
  truth is kept separate from timestamps, so an owner can prove completion while honestly retaining
  a null time. Account/application/member/SAP-code identity checks and ordered fallbacks prevent
  mixed evidence from implying a later stage.
- Reused SAP identity: an active member-level SAP code can originate on an earlier application.
  Currentness is bounded by member/status and the current loan account's exact SAP code binding;
  regression evidence covers this BR-048 path.
- Advice/data disclosure: advice becomes available only after current finalized provider acceptance.
  Queued, legacy-partial, changed-ledger, stale, expired, replayed, and cross-scope paths remain
  unavailable or nondisclosing. Capability/audit vocabulary uses `artifact_id`; full account,
  reference, SAP, actor, checksum, and evidence values remain excluded.
- Read-side mutation: a captured-query regression proves the status GET issues no SQL write verb and
  does not add audit rows.
- Frontend selection/fidelity: the portal container owns application selection, MP14 makes one status
  request for that id, and opposite list-order tests preserve the clicked identity. Existing portal
  cards, fact grid, timeline, advice composition, and `AlertBanner` are reused without new styling.
- Browser acceptance: the Playwright contract collects all three declared scenarios and uses real
  Django authentication/list/selection with an exact status-route scenario seam. Chromium and the
  required twice-run screenshots are intentionally left to the orchestrator's external gate; no
  screenshots were fabricated in the coding sandbox.

## Residual risk

- The legal-readiness owner does not retain a trustworthy composite completion instant, so the
  documentation stage is correctly complete with `completed_at: null` until that owner introduces a
  governed composite event. This is an explicit honest-null behavior, not inferred time.
- The production chunk-size warning remains pre-existing and non-blocking; no bundle architecture
  change belongs to this slice.
