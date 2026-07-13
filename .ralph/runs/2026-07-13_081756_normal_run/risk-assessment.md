# Risk Assessment

Risk level: High (standing owner approval; no veto recorded).

- The slice changes Critical approval configuration permissions, concurrency evidence, and the
  approval-case schema. A defect could expose governance reasons or route future cases incorrectly.
- Activation remains inside `decide_proposal`, one atomic transaction, and the existing persistent
  configuration lock. Range, lifecycle, and authority logic was not moved into views or tests.
- Four real PostgreSQL races prove one winner for rule/committee create/supersede. Every losing
  proposal remains pending with unchanged maker/reason/version/null decision facts and no loser
  effective/history/audit writes.
- New case snapshot fields are nullable/backward-compatible for existing 006G shells, protected by
  foreign keys and a positive version constraint, and migration/model sync passes.
- Proposal detail now denies unrelated authenticated users while preserving maker, eligible
  checker, and configured reader access. The public authority code is source-standard.
- Full backend and frontend gates pass. No protected/source/frontend files or external systems were
  changed, and no real personal or financial data was used.
