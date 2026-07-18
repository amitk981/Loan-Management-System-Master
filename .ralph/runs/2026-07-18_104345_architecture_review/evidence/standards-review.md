# Standards Review

## Findings

1. **High — dispatcher/job duplication:** the advice-specific dispatcher duplicates the existing
   communications template/render/send path, does not expose the source §40.1 interface, calls the
   provider synchronously, has no bounded queued/failed/retrying lifecycle, and retains no source-
   shaped integration event. Corrective owner: 009H5.
2. **High — two-way app dependency:** communications persists FKs to a disbursement intent while
   disbursements imports communications models/modules. This conflicts with codebase-design §§8/
   36. Corrective owners: 009H4 persistence, 009H5 runtime composition.
3. **Medium — misplaced/bypassable migration policy:** `shared` contains legal/disbursement-specific
   allowlist policy, and the literal AST heuristic misses ordinary indirection. Corrective owner:
   009G5.
4. **Medium — proof at private/shallow seams:** crash tests patch private helpers and the second
   never reaches the real pre-commit point; receipt schema evidence compares names rather than full
   definitions. Corrective owner: 009H4.

Sources: `docs/source/codebase-design.md` §§6-8, 20, 22, 26, 35-36, 40, 42;
`docs/source/integrations.md` §§10, 19.3, 21; `docs/source/data-model.md` §34.

Worst severity: High. Two High and two Medium findings.
