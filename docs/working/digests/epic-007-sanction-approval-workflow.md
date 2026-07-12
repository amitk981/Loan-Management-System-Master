# Epic 007 Digest: Sanction Approval Workflow And Registers

Sources distilled while finishing 006G and sharpening 006H/006X:

- `docs/source/implementation-roadmap.md` §12.1-§12.5
- `docs/source/api-contracts.md` §25.1-§25.4
- `docs/source/data-model.md` §15.1-§15.4 and §30/§34
- `docs/source/auth-permissions.md` §12.6, §15.8-§15.9, §20.1, §34.5

## 007A Approval-Matrix Boundary

- Rules are effective-dated and describe decision type, inclusive amount bounds, optional
  condition code, required role list/director count, joint-approval flag, register requirement,
  and active/inactive status.
- Source sanction rules: up to and including INR 500,000 requires CFO + one Director; above INR
  500,000 requires CFO + two Directors; an exceeds-limit condition requires CFO + two Directors
  and exception handling. Configuration must persist these facts rather than hard-code them in
  the case engine.
- Admin/config management requires `approvals.matrix.manage`; reads require
  `approvals.matrix.read`. Effective ranges and amount ranges must not overlap for the same
  decision/condition route, and updates must preserve historical case snapshots.
- Architecture review sharpening: expose one resolver projection consumed unchanged by API and
  downstream routing, and prove overlapping effective rule creation/supersession with a PostgreSQL
  one-winner race while preserving already-referenced historical rule snapshots.

## 007B Existing 006G Case Enrichment

- 006G already creates the unique pending application/appraisal case shell at source §24.5. 007B
  must resolve the effective 007A rule and enrich that row with recommended amount, matrix-rule
  linkage, required-approver snapshot, related-entity facts, and exception condition/reason.
- ADR-0005 and corrective 006G2 make the approval-case module the only create/read/enrichment seam;
  007B must use that interface and must not import or mutate the case model from credit code.
- Do not expose a second generic create path that can duplicate the 006G case. Any source §25.2
  adapter must return/enrich the existing row idempotently or reject incompatible state.
- Approver selection, conflict exclusion, actions, sanction decisions, and register entries remain
  their later dedicated slices. Required approver facts are immutable snapshots once assigned.
