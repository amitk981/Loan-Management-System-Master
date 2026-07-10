# Independent Standards Review

Fixed point: `1e2d873112c1b14a43b81fa398f0013ba4bb02ae`

Diff command: `git diff 1e2d873...HEAD`

## Standards

- **Hard — architecture drift:** `sfpcl_credit/applications/services.py` adds eligibility rules,
  loan-limit calculation, configuration resolution, persistence, serialization, and auditing to a
  2,789-line generic application service; `applications/models.py` also places credit-assessment
  models in `applications`. The documented seams are `credit.modules.eligibility_assessment`,
  `credit.modules.loan_limit_calculator`, and `configurations.modules.configuration_resolver`
  (`docs/source/codebase-design.md` §§12.1-12.2, §36.1, §38.1).
- **Hard — snapshot immutability:** the service reloads the existing one-to-one assessment and
  overwrites snapshot fields on an explicit rerun. The standards reviewer read this against
  “Historical assessments do not change when policy changes” (`codebase-design.md` §12.2). The
  primary review disposition downgraded this to a watch because `data-model.md` defines one
  assessment per application, 006D explicitly requires successful rerun replacement with old/new
  audit, and passive policy changes do not alter the stored GET response.
- **Hard — React-owned workflow rule:** `ApplicationDetail.tsx` derives documentation/payment
  readiness locally. React pages must render backend readiness/`available_actions`, not decide it
  (`codebase-design.md` §§23.3-23.4, §28.3, §42.3).
- **Hard — wrong test seam:** `ApplicationDetail.test.tsx` bypasses HTTP through a production
  `initialData` prop and static rendering; loan-limit tests exist only in the large HTTP suite.
  Standards require frontend tests with mocked HTTP and pure calculation tests through the module
  interface (`codebase-design.md` §§26.1, 26.3-26.4).
- **Judgment call — duplication:** `serialize_loan_limit_assessment` and
  `_loan_limit_assessment_audit_snapshot` duplicate nearly the same projection, creating drift risk.

Corrective disposition: `005I4` owns the React/test seam; `006D2` owns deep modules, focused module
tests, configuration resolution, and snapshot projection. Explicit rerun replacement remains a
documented watch item.
