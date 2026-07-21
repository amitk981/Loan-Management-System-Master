# Risk Assessment

- Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`
- Mode: repair
- Risk level: High
- Repair domain: generic communication-worker provider-acceptance crash recovery

## Material risks

- **External side-effect duplication:** rolling back accepted provider identity after the provider has
  accepted a message permits a later worker to send the same communication again.
- **Transaction boundary:** removing an encompassing atomic block must not remove the narrow locks
  used for job claims, immutable provider evidence, reminder serviceability, or final completion.
- **Final-attempt truth:** accepted provider evidence must coexist truthfully with a failed/exhausted
  local job and its operator exception when post-acceptance finalisation crashes.
- **Regression breadth:** the repair affects the generic worker used by reminders and ordinary
  communications, although it changes only the transaction wrapper around existing explicit atomic
  phases.

## Controls and evidence

- Existing public-seam tests went RED before the repair for both non-final and final accepted-crash
  recovery; logs are `communication-nonfinal-accepted-probe.log` and
  `communication-final-accepted-red.log`.
- The exact failed test and the non-final companion both pass after the one-line boundary change.
- All 36 communication-worker runtime tests pass (6 PostgreSQL-only cases skipped by the local
  SQLite-focused run), covering claim, retry, provider failure, crash, exception, and resolution
  paths.
- Django system check and migration consistency pass; no schema, frontend, API, or policy change was
  made.
- The orchestrator must still run the authoritative complete-suite coverage and trusted PostgreSQL
  gates before committing. No local complete-suite result is claimed.

## Residual risk

Low after independent validation. The narrow atomic phases remain intact, and the outer transaction
was the direct cause of losing database evidence for an irreversible external effect. The retained
provider evidence now becomes durable before later payload/finalisation work can fail.
