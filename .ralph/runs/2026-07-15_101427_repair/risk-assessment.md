# Risk Assessment

Risk level: High

- Selected slice: 008K4-current-evidence-and-security-read-closure
- Mode: repair
- Manual review required: independent orchestrator revalidation before commit under standing
  approval.

The repair changes only migration routing plus Ralph artifacts. The underlying slice affects
security-instrument privacy, immutable bank/checklist authority, and concurrent legal-document
generation. The migration now targets the actual `legal_documents.ChecklistAction` state/table,
keeps one migration file, applies on fresh SQLite and PostgreSQL databases, reverses through Django's
standard `AddField` path, and reports no model drift. Full regression, 92% coverage, twice-run
PostgreSQL acceptance, affected race repeats, diff, queue, and protected-path checks are green.
