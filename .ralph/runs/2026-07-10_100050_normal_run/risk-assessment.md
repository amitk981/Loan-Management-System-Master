# Risk Assessment

Risk level: High

- Selected slice: `005I3-application-nominee-selection-contract`.
- High risk is warranted because the change adds a database FK and tightens submit,
  completeness/reference, portal, and eligibility decisions. Standing owner approval applies and
  the veto list contains no matching revocation.
- Migration risk is bounded by a nullable, non-destructive protected FK; legacy applications remain
  valid rows and receive pending/manual-evidence behavior until a nominee is selected.
- Authorization risk is bounded by reusing staff application permissions/object access and active
  portal-account own-member scope. No new permission or parallel linking endpoint was added.
- Privacy risk is bounded by metadata-only application summaries. PAN/Aadhaar values, protected
  tokens, hashes, and reveal controls are absent from application responses and screens; audit
  metadata contains only the nominee UUID.
- Integrity risk is bounded by shared same-member/adult/evidence validation at create/update,
  revalidation at submit/reference, protected deletion behavior, and deterministic eligibility from
  `LoanApplication.nominee` only.
- Invalid paths assert no application/audit/workflow success evidence. The initial staff contract
  has captured backend RED/GREEN logs; the later invalid-path cases have GREEN evidence but no
  separate preserved RED log, an honest TDD process-evidence caveat. Frontend error-state
  RED/GREEN evidence is present.
- Visual verification uses self-contained HTML plus React static-render assertions. PNG capture was
  unavailable because the in-app browser runtime exposed no browser instance; this limitation is
  recorded in `evidence/visual-evidence.md`.
- No dependency, deployment, external communication, real personal data, protected-path, or
  `docs/source/` changes were made.
