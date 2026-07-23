# Risk Assessment

Risk level: High

- Selected slice: 011M2-member-portal-kyc-correction-request
- Mode: normal_run
- Manual review required: yes; independent validation owns the authoritative High-risk lane and
  browser acceptance.

## Risk controls

- **Protected identity/data integrity:** portal submissions create a pending request and cannot edit
  `Member`/`KycProfile`. PAN/Aadhaar remain tokenised and borrower projections/history stay masked.
  Approval is blocked until every linked restricted document passes the existing 004H governed KYC
  verification endpoint; protected identity apply delegates to `MemberRegistry`.
- **Scope/authorization:** portal member identity comes only from the active `PortalAccount`.
  History is filtered by that exact account. Forged member claims are `403`, audited, and write-free.
  Staff queue/review requires `members.member.update` plus member object scope; protected identity
  apply additionally requires `members.member.identity_change.approve`.
- **Maker-checker/reverification:** the portal requester cannot approve the identity change. The
  existing KYC verifier maker-checker rule remains active. Approval writes governed masked history,
  then resets member/profile KYC to pending and links an open 011M review where present.
- **Evidence/privacy:** correction evidence is PDF/JPG/PNG, restricted, provenance-bound to portal
  account/member, and self-attested for PAN/Aadhaar. Portal responses omit reviewer identity,
  internal notes, storage keys, and full protected values.
- **Concurrency/state:** staff actions lock the correction; only submitted→under_review and
  under_review→approved/rejected are accepted. Existing member version checks protect apply.
- **Schema:** one additive migration; Django check and migration sync passed.
- **Frontend:** MP04 reuses existing portal cards, alerts, badges, inputs, buttons, spacing, colours,
  and responsive grid. No mock/runtime policy calculation was added.

## Residual validation risk

The exact Playwright spec was attempted twice after both localhost servers became ready, but Chrome
closed during launch before a page existed. No screenshot was fabricated. Independent trusted
validation must run the declared spec twice and retain `portal-kyc-correction-decision.png`.
