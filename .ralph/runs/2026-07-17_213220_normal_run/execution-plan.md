# Execution Plan

Selected slice: 009E5-source-bank-rationale-redaction-closure

1. Add a focused shared-module table test for safe ordinary audit text and unsafe blanks, length,
   controls, formatted digit sequences, field-encryption prefixes/tokens, legacy markers, and
   lookup hashes. Run it first and retain the RED output.
2. Implement one deep `shared.audit_text` interface that returns trimmed reviewable text or raises
   one generic safe validation error, including optional caller-owned protected values.
3. Add a public source-bank activation/replacement regression table proving unsafe text produces
   the same generic denial, zero governance/version/audit writes, and no rejected-text echo. Run
   focused GREEN tests and retain the output.
4. Run the retained source-bank rationale/history/current-resolution tests, the impacted shared
   security tests, Django check, and migration-sync check. Do not run the complete backend suite.
5. Save self-contained evidence, changed-files, risk assessment, review packet, and final summary;
   update the Epic 009 digest, Ralph progress/state/handoff, mark only 009E5 Complete, and recheck
   the next two Not Started corrective slices for concrete requirements.

Expected product files:
- `sfpcl_credit/shared/audit_text.py`
- `sfpcl_credit/configurations/modules/source_bank_governance.py`
- focused tests under `sfpcl_credit/tests/`

No frontend, API shape, dependency, or database migration change is expected.
