# Execution Plan

Selected slice: 011J-archive-record-and-retention
Mode: same-worktree repair
Failed validation domain: trusted PostgreSQL acceptance

1. Preserve the existing 011J candidate and inspect only the failed PostgreSQL acceptance artifacts, the declared acceptance class, and the minimal archive concurrency path needed to reproduce the exact validator failure.
2. Run the declared `ArchiveRecordPostgreSQLAcceptanceTests` command against the configured PostgreSQL environment as the deterministic repair feedback loop; retain its red output in this repair run when reproducible.
3. Rank and test bounded hypotheses for the validator mismatch. Change only the demonstrated PostgreSQL acceptance domain, adding or correcting regression coverage before product code if implementation behavior is at fault.
4. Rerun the exact named validator until it reports exactly one passing test on both independent runs and records PostgreSQL environment evidence. Save focused output under this run's `evidence/terminal-logs/`.
5. Run proportionate backend checks for any touched files, verify no protected paths changed, then complete the repair risk assessment and review packet with traceability and the exact required result.
