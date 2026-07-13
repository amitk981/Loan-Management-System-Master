# Risk Assessment

Risk level: High

- Selected slice: 007A5-approval-governance-complete-loser-ledger
- Mode: normal_run
- Standing approval: confirmed; no veto exists.
- Risks: Critical configuration proposal payload disclosure, concurrent activation correctness, and
  accidental mutation of open approval-case routing snapshots.
- Mitigations: the existing participant/eligible-checker/read permission remains authoritative;
  activation remains exclusively behind `decide_proposal` and the configuration lock; four direct
  PostgreSQL races compare complete winner/loser ledgers and public loser reads; full gates pass.
- Database impact: none (migrations 0005 and 0006 are consumed, no new migration).
- Dependency impact: none.
- Residual risk: 007B must populate production case snapshots; this slice proves configuration
  governance cannot mutate a fully populated fixture but does not implement enrichment.
