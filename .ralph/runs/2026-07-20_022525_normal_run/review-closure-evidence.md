# Review Closure Evidence

## Finding Evidence
| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py::StatementEvidenceOwnerScopeClosureTests::test_direct_capture_rejects_nonexistent_statement_line_evidence | evidence/terminal-logs/statement-owner-red.log | evidence/terminal-logs/statement-owner-green.log |

## Acceptance Evidence
| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-STATEMENT-1 | sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py::StatementEvidenceOwnerScopeClosureTests::test_statement_line_is_the_only_database_relationship_owner | evidence/terminal-logs/acceptance-matrix-green.log |
| AC-STATEMENT-2 | sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py::StatementEvidenceOwnerScopeClosureTests::test_import_time_auto_match_respects_permission_and_loan_object_scope | evidence/terminal-logs/acceptance-matrix-green.log |
| AC-STATEMENT-3 | sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py::StatementEvidenceOwnerScopeClosureTests::test_subsidiary_auto_match_requires_borrower_and_application_facts | evidence/terminal-logs/subsidiary-matrix-green.log |
| AC-STATEMENT-4 | sfpcl_credit/tests/test_statement_evidence_owner_migration.py::StatementEvidenceOwnerMigrationTests::test_coherent_and_orphan_legacy_links_migrate_without_inventing_lines | evidence/terminal-logs/statement-migration-green.log |
| AC-STATEMENT-5 | sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py::StatementEvidenceOwnerScopeClosureTests::test_statement_list_hides_out_of_scope_matches_counts_and_private_facts | evidence/terminal-logs/acceptance-matrix-green.log |
