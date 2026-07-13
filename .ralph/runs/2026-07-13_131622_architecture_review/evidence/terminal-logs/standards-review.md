# Independent Standards Review

The independent Standards pass found no material new issue in 006Z15 or 007A6. Their tests now
cross real member action boundaries and exact governed PostgreSQL race interfaces respectively.

Material findings after source/deferral adjudication:

1. High: `approval_case_engine.can_read_approval_case` permits only snapshotted approvers, denying
   source-required Credit Manager, Company Secretary, and Auditor sanction-package reads. 007C3
   owns persisted read-only scope separate from action permission.
2. High: return closes a one-to-one case, while sanction handoff rejects any existing case. Source
   data cardinality and codebase-design §13.1 require immutable new cycles. 007D3 owns correction,
   fresh review, and resubmission.
3. Medium judgment: collection filtering materializes the broad approval-case ledger in Python
   before pagination. 007C3 owns a scope-narrowed selector.

The reviewer also raised missing register/conflict behavior. Those are explicit 007H/007E
deferrals, not 007D defects. The submitted case `version` is the documented optimistic-concurrency
addition required by 007C2 sharpening.

