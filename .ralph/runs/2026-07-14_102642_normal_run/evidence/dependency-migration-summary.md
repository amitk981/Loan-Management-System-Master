# Dependency and migration evidence

- `legal_documents.modules.document_generation` owns orchestration and imports the public
  application/approval fact boundaries plus foundation document services.
- `legal_documents.selectors` owns exact application filtering, eager loading, deterministic
  ordering, count, bounded page normalization, and slicing.
- `legal_documents.models.LoanDocument` is the sole runtime model owner and retains
  `db_table = "loan_documents"`.
- `documents` has no application, approval, or legal-document business import.
- The legal module/model/selector have no view or HTTP request import.
- The single migration transfers Django state from `documents` to `legal_documents` without a
  create/copy/drop operation, then adds `loan_document_account_requires_epic_009`.
- A migration-executor test creates a pre-transfer row and reads the same primary/application/
  template/file identities after transfer.
- Fresh migration creates exactly one `loan_documents` table and its SQL includes
  `CHECK ("loan_account_id" IS NULL)`.

Evidence: `green-dependency-model-ownership.txt`, `green-retained-row-migration.txt`,
`green-loan-account-database-constraint.txt`, and `fresh-migration.txt` in `terminal-logs/`.
