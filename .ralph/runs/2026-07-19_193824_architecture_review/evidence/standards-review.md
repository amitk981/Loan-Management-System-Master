# Standards Review

Fixed point: `e748f8ca085a9ad2e174c6295bddbdd6d3f9cc3e`

Commit: `4f8febd3 chore(009L7-epic-009-read-boundary-convergence-closure): complete Ralph AFK run`

## Findings

- **Hard — retained High recurrence:** `post_transfer_evidence.py:51-81` selects active accounts
  from a coarse set of related-row existence checks, while the transfer owner's
  `completed_success_is_coherent` verifies file bytes/provenance, exact register/advice/posting,
  audit/workflow, actor, and activation evidence. `loan_account_360.py:161-216` now trusts the
  selector and exposes the row without that owner decision. This violates 009L7 requirements 2-3,
  `API_CONTRACTS.md`'s owner-valid-before-count contract, and codebase-design §§16/42.
- **Hard — retained High authorization/scope risk:** `loan_account_read.py:65-77` admits Senior
  Finance from any assigned request and CFC from raw task/status rows. `loan_account_360.py:91-104`
  skips the latest-assignee restriction for an actor who also has the initiation grant and removed
  the exact scalar scope resolver from public detail/list. This is not the exact current object
  scope required by auth-permissions §§19.3/34.7.
- **Hard — retained Medium private seam:** `identity/epic009_e2e_fixture.py:14-26,43` still imports a
  `TestCase`, calls `setUp`, and invokes private test helpers. The new regression inspects only the
  management-command source, so the wrapper hides rather than removes the §26 violation.
- **Hard — retained Medium matrix gap:** the six new one-row HTTP tests have real assertions, but do
  not provide five-branch 1/21/101, adjacent-invalid, scalar-component, action/mutation,
  query-ceiling, and independent error coverage required by 009L7 requirement 4.
- **Judgment — retained Low duplication:** JSON equality/key-count selector helpers remain copied
  across lifecycle, SAP, and disbursement owners, weakening locality under §42.

No Critical finding was identified. The same High owner-boundary root recurred, so the review must
fail closed without another leaf corrective.
