# Risk Assessment

Risk level: Medium

- Selected slice: `008D-stamp-duty-and-notarisation-tracking`
- Mode: `normal_run`
- Manual review required: No; the owner's standing Ralph approval applies and no veto exists.
- Data/schema: One additive migration creates protected one-to-one stamp/notary records and two
  nullable checklist projection fields. No destructive migration or legacy-row rewrite.
- Legal/compliance: Incorrect adequacy/completion could affect readiness. Mitigations are explicit
  Company Secretary authority, strict outcome requirements, same-application evidence provenance,
  audit/version/workflow evidence, and no checklist completion/readiness side effect.
- Concurrency: Changed submissions race on a legal record. Mitigated by `FOR UPDATE OF` the owning
  loan-document row, one-to-one constraints, atomic owner/checklist/evidence writes, and a genuine
  five-worker PostgreSQL race passing twice after final review fixes.
- Access/disclosure: Evidence and legal metadata are sensitive. The legal-document owner enforces
  action permission, role, sanctioned Stage 4 scope, and current renderer provenance; the documents
  owner enforces exact legal upload provenance and sensitivity. Responses grant no download.
- Money/business rule: Amount is persisted as supplied; no ₹500 or ad-valorem rule is calculated.
  The unresolved rate policy remains configurable rather than invented.
- External effects: None. No deployment, communication, payment, download, or external service call.
