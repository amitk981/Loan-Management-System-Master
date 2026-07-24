# 012DA Requirement Preservation Matrix

The original 012DA contract is preserved across the dependency-ordered
`012DAA -> 012DAB -> 012DAC` chain.

| Original 012DA contract | Successor owner | Preservation |
|---|---|---|
| Prerequisite `012D2` | 012DAA | The first successor depends on `012D2`; later successors depend on their immediate predecessor. |
| Runtime capability `localhost-e2e-server` | 012DAA, 012DAB, 012DAC | Every successor declares the capability and an exact trusted-browser section. |
| Trusted spec `e2e/reports-exports-audit-explorer.e2e.spec.ts` | 012DAA, 012DAB, 012DAC | The same spec is extended progressively and terminal 012DAC repeats its complete contract. |
| Screenshot `report-results.png`, two passing runs | 012DAA; repeated by 012DAC terminal evidence | Preserved by exact name and run count. |
| Screenshots `export-job-status.png` and `masked-export.png`, two passing runs | 012DAB; repeated by 012DAC terminal evidence | Preserved by exact names and run count. |
| Screenshots `audit-explorer.png` and `audit-observation-recorded.png`, two passing runs | 012DAC | Preserved by exact names and run count. |
| Wire S69 report reads to 012A with filters, sorting, pagination, roles, and parameters | 012DAA requirements 1-3 | Preserved with backend round-trip and reconciliation. |
| Wire RegistersHub and ReportsMIS export actions to 012B/012C | 012DAB requirement 1 | Preserved for start, job identity, polling/status, and ready-only audited download. |
| Masked sensitive columns and unauthorized export rejection | 012DAB requirements 2-4 | Preserved with backend-authoritative permission boundaries and no restricted-value leakage. |
| Wire S74 to 012D filters and pagination; keep it read-only and suppress restricted fields | 012DAC requirements 1-2 | Preserved with deterministic pagination, no audit-log writes, and no edit affordance. |
| Scoped sampled-result observation form/list/detail using 012D2 | 012DAC requirement 3 | Preserved as a separate immutable auditor-only resource, never an editable audit row. |
| Loading, empty, error, unauthorized, validation, and success states throughout | 012DAA requirement 4; 012DAB requirement 2; 012DAC requirement 4 | Every owned surface retains truthful state coverage. |
| Export states queued/running/failed/ready | 012DAB requirements 1-2 | Preserved using existing status patterns. |
| Remove report/register mock data and inline fixtures | 012DAA partial read removal; 012DAB final ownership; 012DAC terminal assertion | Final mock-removal ownership remains exact for `ReportsMIS.tsx` and `RegistersHub.tsx`; terminal completion covers all original screens. |
| Report filter round-trip and seeded-fixture result test | 012DAA tests | Preserved, with sorting/pagination and state cases added only to make the seam independently green. |
| Unauthorized export and permitted masked export test | 012DAB tests | Preserved, including status and audited-download assertions. |
| Audit explorer no-mutation/restricted-field test | 012DAC tests | Preserved exactly. |
| M14-FR-012 scoped Internal Auditor observation and negative authorization/edit tests | 012DAC tests | Preserved exactly, including foreign evidence, lifecycle fields, and no-leakage rejection. |
| Out-of-scope new reports, 012E dashboard hardening, and 012F security regression | All successors | Repeated and preserved; sibling successor work is also explicitly excluded at each seam. |
| RED/GREEN request/filter/status/download evidence | 012DAA request/filter/status; 012DAB export request/status/download; 012DAC audit request/filter/observation | Preserved across the chain. |
| Reconciliation, masking, denial, audited download, read-only explorer, and observation evidence | 012DAA reconciliation; 012DAB masking/denial/download; 012DAC explorer/observation | Preserved across the capability owners. |
| Focused 012A-012D2 regressions and full gates | 012DAA: 012A; 012DAB: 012B/012C; 012DAC: 012D/012D2 | Every successor requires its focused backend regressions and full configured gates. |
| Medium risk | 012DAA, 012DAB, 012DAC | Every successor retains Medium risk. |
| End-to-end S69/S74/export acceptance, no mocks, gates, and all screenshots | 012DAA/012DAB capability criteria; 012DAC terminal criteria | Terminal completion explicitly requires the complete original acceptance contract. |
| Original done-checklist duties | All successors | Each independently retains planning, tests, implementation, contract, permission/audit as applicable, visuals, gates, risk, unresolved-decision, and post-gate commit duties. |

## Diff Budget

| Successor | Predicted changed lines | Margin below 2,000 |
|---|---:|---:|
| 012DAA | 1,050 | 950 |
| 012DAB | 1,250 | 750 |
| 012DAC | 1,350 | 650 |

The 3,475-line failed candidate is split at natural page/capability seams. Shared report and browser
seams are extended serially, so no successor needs to rebuild the entire rejected candidate.

## Dependency Rewrite

- 012DAA inherits original prerequisite `012D2`.
- 012DAB depends on 012DAA.
- 012DAC depends on 012DAB.
- Existing downstream slice 012G now depends on terminal successor 012DAC.
