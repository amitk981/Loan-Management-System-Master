# Codebase Design — SFPCL Member Credit Administration & Loan Disbursement Platform

## 1. Document Control

| Field | Value |
|---|---|
| Document name | `codebase-design.md` |
| Product / system | SFPCL Member Credit Administration & Loan Disbursement Platform |
| Client | Sahyadri Farmers Producer Company Limited |
| Backend | Python + Django + Django REST Framework |
| Frontend | React |
| Database | PostgreSQL |
| Authentication | JWT |
| Supporting services | Redis, Celery, Celery Beat, object storage / DMS, email gateway, SMS gateway, SAP adapter, bank adapter, CDSL tracking adapter and future CKYC / bureau / e-sign adapters |
| Codebase design influence | Matt Pocock `skills/engineering/codebase-design` vocabulary: module, interface, implementation, seam, adapter, depth, leverage and locality |
| Source basis | Current analysis set: SOP review, client brief, user flows, functional specification, information architecture, screen specification, content specification, component specification, design system, domain model, data model, technical architecture, API contracts, auth-permissions, integrations, security/privacy, deployment/ops, test plan and implementation roadmap |
| Intended audience | Engineering leads, backend engineers, frontend engineers, QA automation, DevOps, product owners, implementation leads and technical reviewers |
| Status | Draft for implementation planning |

---

## 2. Purpose

This document defines the proposed codebase design for the SFPCL Member Credit Administration & Loan Disbursement Platform.

It turns the business, data, workflow, security, integration, testing and deployment analysis into an implementation-oriented codebase structure for a Django + React + PostgreSQL system.

The goal is not merely to list folders. The goal is to define where each important **module** lives, what **interface** it exposes, where each **seam** belongs, which **adapter** satisfies each seam, and how the codebase stays maintainable as SOP complexity grows.

This document answers:

1. How should the backend codebase be organised?
2. How should the frontend codebase be organised?
3. Which modules should be deep and which should stay thin?
4. Where should seams be placed?
5. Which external systems need adapters?
6. Which logic must be kept out of views, serializers and React pages?
7. How should workflow state transitions be implemented?
8. How should permissions be enforced?
9. How should financial and legal operations be kept idempotent and auditable?
10. How should tests be written through module interfaces?
11. How should code be structured so future SAP, bank, CKYC, bureau, e-sign and CDSL integrations can be added without rewriting core workflows?

---

## 3. Codebase Design Vocabulary

This codebase should consistently use the following vocabulary in design reviews, ADRs, comments and architecture documentation.

## 3.1 Module

A **module** is anything with an interface and an implementation.

A module may be:

- A function.
- A class.
- A Django app.
- A Python package.
- A React feature slice.
- A domain workflow.
- An integration adapter.
- A tier-spanning vertical slice.

The word **module** should be used for codebase design discussions instead of vague labels like “component”, “service” or “utility”, except where a framework has a precise meaning, such as “React component”.

## 3.2 Interface

An **interface** is everything a caller must know to use a module correctly.

It includes:

- Function or method names.
- Parameters.
- Return values.
- Types.
- Required ordering.
- Valid states.
- Error modes.
- Invariants.
- Permissions required.
- Idempotency behaviour.
- Transaction behaviour.
- Performance expectations.
- Side effects.
- Audit behaviour.

For example, the interface for disbursement initiation is not merely:

```python
initiate_disbursement(loan_account_id, amount)
```

The real interface also says:

- The loan account must be in `ready_for_disbursement`.
- Documentation checklist must be approved.
- SAP customer code must exist.
- Security package must be complete.
- Amount must not exceed sanctioned amount.
- Caller must have `finance.disbursement.initiate`.
- Operation must be idempotent.
- Audit log must be written.
- It returns a disbursement record and available next actions.

## 3.3 Implementation

An **implementation** is what sits inside a module.

For example, the implementation of the Loan Limit module may include:

- Shareholding lookup.
- Share valuation lookup.
- Scale of finance lookup.
- Land area aggregation.
- Policy version snapshotting.
- Exception flagging.
- Audit event creation.
- Decimal rounding rules.

Callers should not need to know those internal details.

## 3.4 Seam

A **seam** is where a module’s interface lives: the place where behaviour can be changed or replaced without editing callers.

Good seams in this platform include:

- External provider integrations such as SAP, bank, SMS, email, object storage, CDSL, CKYC and bureau.
- Workflow modules such as Approval Case Engine, Disbursement Readiness and Repayment Allocation.
- Policy calculators such as Loan Limit Calculator and NBFC Principal Business Test.
- Document generation modules.
- Report export modules.

Poor seams include:

- A repository wrapper around every Django model when there is only one database implementation.
- A separate interface for every one-line helper.
- A “manager” class that simply passes parameters through to another class.
- A React hook that mirrors every endpoint without hiding behaviour.

## 3.5 Adapter

An **adapter** is a concrete implementation at a seam.

Examples:

| Seam | Production Adapter | Test Adapter |
|---|---|---|
| Email sending | SMTP/email provider adapter | In-memory email adapter |
| SMS sending | SMS gateway adapter | In-memory SMS adapter |
| Object storage | S3/DMS adapter | Local/in-memory file adapter |
| SAP | Manual SAP adapter or SAP API adapter | Fake SAP adapter |
| Bank | Manual bank adapter or RBL API adapter | Fake bank adapter |
| CDSL | Manual tracking adapter or future CDSL adapter | Fake CDSL adapter |
| CKYC | CKYC provider adapter | Fake CKYC adapter |
| Credit bureau | Bureau provider adapter | Fake bureau adapter |
| E-sign | E-sign provider adapter | Fake e-sign adapter |

A seam is justified when at least two adapters exist or are meaningfully needed, typically production and test, or manual and API.

## 3.6 Depth

A module is **deep** when a small interface hides a large amount of useful behaviour.

The codebase should intentionally build deep modules for complex SOP logic:

- Loan Limit Calculator.
- Eligibility Assessment.
- Approval Case Engine.
- Documentation Checklist.
- Security Package.
- Disbursement Readiness.
- Repayment Allocation.
- Interest Engine.
- Default and Recovery Workflow.
- Closure Workflow.
- Compliance Calculators.

A module is **shallow** when callers must still understand nearly all the complexity or when the module simply forwards parameters to another module.

## 3.7 Leverage

**Leverage** is what callers get from a deep module.

A good Loan Limit module lets many callers ask:

```python
assessment = loan_limit_module.calculate_for_application(application_id)
```

without duplicating the rules for:

- Share valuation.
- Share count.
- Percentage/cap.
- Scale of finance.
- Acreage.
- Final lower-of-two amount.
- Exception flags.
- Policy version snapshots.

## 3.8 Locality

**Locality** is what maintainers get from a deep module.

When the client later resolves the 30% vs 10% vs ₹200/share ambiguity, the change should be local to:

- Loan policy configuration.
- Loan Limit module.
- Calculator tests.

It should not require editing:

- Application serializers.
- Approval views.
- Report exporters.
- React pages.
- Disbursement readiness code.
- MIS report logic.

---

# 4. Codebase Design Goals

## 4.1 Business Goals

The codebase must support the full SOP lifecycle:

1. Initial Loan Request.
2. Credit Assessment Process.
3. Credit Scrutiny and Approval Process.
4. Documentation and Stamping.
5. Loan Disbursement.
6. Monitoring and Repayment.
7. Default and Recovery.
8. Closure, NOC and Archival.
9. Compliance and Audit.

## 4.2 Engineering Goals

| Goal | Design Implication |
|---|---|
| Keep workflow rules centralised | Use domain modules, not scattered checks in views/pages. |
| Keep state transitions safe | Use state-transition modules with explicit allowed transitions. |
| Keep permissions enforceable | Use backend permission modules, not frontend-only checks. |
| Keep financial actions idempotent | Use idempotency keys and transaction-safe modules. |
| Keep integrations replaceable | Use adapter seams for true external systems. |
| Keep tests stable | Test behaviour through module interfaces, not internal helpers. |
| Keep reports consistent | Generate registers from system-of-record tables. |
| Keep sensitive data protected | Centralise masking, reveal and document access rules. |
| Keep historical accuracy | Snapshot policy, approvals, calculations and generated documents. |
| Keep frontend simple | React pages should orchestrate UI, not business rules. |

---

# 5. Repository Strategy

## 5.1 Recommended Repository Structure

A single monorepo is recommended for MVP because backend, frontend, API contracts, domain model, document templates and deployment configuration will change together.

```text
sfpcl-credit-platform/
  README.md
  CONTEXT.md
  ADR/
  docs/
    client-brief.md
    user-flows.md
    functional-spec.md
    information-architecture.md
    screen-spec.md
    content-spec.md
    component-spec.md
    design-system.md
    domain-model.md
    data-model.md
    technical-architecture.md
    api-contracts.md
    auth-permissions.md
    integrations.md
    security-privacy.md
    deployment-ops.md
    test-plan.md
    implementation-roadmap.md
    codebase-design.md

  backend/
    manage.py
    pyproject.toml
    config/
    apps/
    tests/
    scripts/

  frontend/
    package.json
    tsconfig.json
    vite.config.ts
    src/
    tests/

  infra/
    docker/
    compose/
    k8s/
    terraform/
    nginx/

  openapi/
    openapi.yaml

  templates/
    documents/
    emails/
    sms/

  tools/
    seed_data/
    migration/
    qa/
```

## 5.2 Why Monorepo

| Reason | Benefit |
|---|---|
| API and UI evolve together | Easier contract alignment |
| Shared documentation | One source for specs and ADRs |
| Shared release version | Easier UAT and deployment |
| Easier local development | Compose stack with backend/frontend/db/redis |
| Easier vertical slicing | One issue can include backend, frontend and tests |
| Easier CI orchestration | Full regression on cross-cutting changes |

## 5.3 When to Split Repositories Later

Splitting may be considered only when:

- Separate teams own backend and frontend release cycles.
- Multiple external clients consume the API.
- Deployment governance requires separate repos.
- A borrower portal or mobile app becomes a separate product.
- Integrations become independently deployable modules.

For MVP, splitting early would add coordination cost without enough benefit.

---

# 6. Backend Codebase Design

## 6.1 Backend Top-Level Structure

```text
backend/
  config/
    settings/
      base.py
      local.py
      dev.py
      qa.py
      uat.py
      staging.py
      production.py
    urls.py
    celery.py
    asgi.py
    wsgi.py

  apps/
    accounts/
    rbac/
    audit/
    documents/
    configurations/
    members/
    kyc/
    applications/
    credit/
    approvals/
    legal_documents/
    security_instruments/
    sap_workflow/
    loans/
    disbursements/
    repayments/
    interest/
    monitoring/
    defaults/
    recovery/
    closure/
    compliance/
    communications/
    reports/
    integrations/
    operations/

  shared/
    errors.py
    money.py
    dates.py
    ids.py
    enums.py
    permissions.py
    transactions.py
    idempotency.py
    masking.py
    pagination.py
    serializers.py
    typing.py

  tests/
    factories/
    fixtures/
    integration/
    e2e_helpers/

  scripts/
    seed_reference_data.py
    migrate_legacy_data.py
    reconcile_balances.py
```

## 6.2 Django App Design Rule

Each Django app should represent a coherent business area, but the important design unit is still the **module** inside the app.

A Django app may contain many modules:

```text
apps/credit/
  models.py
  selectors.py
  interfaces.py
  modules/
    eligibility_assessment.py
    active_member_status.py
    loan_limit_calculator.py
    appraisal_review.py
  api/
    serializers.py
    views.py
    urls.py
  tasks.py
  tests/
```

## 6.3 Views Must Be Thin

DRF views should not implement SOP logic.

Views should do:

1. Authenticate request.
2. Parse request with serializer.
3. Call a module interface.
4. Return response.
5. Let the module enforce workflow, permission, idempotency and audit where appropriate.

Views should not:

- Calculate loan limits.
- Decide approvers.
- Transition workflow states directly.
- Check document completeness manually.
- Allocate repayments.
- Generate audit logs by hand for every rule.
- Implement external provider logic.

### Good Pattern

```python
class LoanLimitAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        serializer = LoanLimitAssessmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = loan_limit_module.calculate_for_application(
            actor=request.user,
            application_id=application_id,
            request_data=serializer.validated_data,
        )

        return Response(LoanLimitAssessmentResponseSerializer(result).data)
```

### Bad Pattern

```python
class LoanLimitAssessmentView(APIView):
    def post(self, request, application_id):
        # Bad: view contains policy lookup, share calculation,
        # land calculation, exception flagging and audit.
        ...
```

## 6.4 Serializer Rule

Serializers should validate shape and simple field rules.

Serializers should not own deep business rules.

Good serializer responsibilities:

- Required fields.
- Type conversion.
- Format validation.
- Basic enum validation.
- Nested payload shape.

Bad serializer responsibilities:

- Approval matrix logic.
- Eligibility decisions.
- Recovery approval gate.
- Disbursement readiness.
- Repayment allocation.
- Interest capitalisation.

## 6.5 Model Rule

Django models should enforce persistence constraints and simple invariants.

Models should not become huge workflow engines.

Good model responsibilities:

- Fields.
- Relationships.
- Constraints.
- Status enums.
- Simple properties.
- Database indexes.

Deep workflow logic should live in modules with explicit interfaces.

---

# 7. Backend Module File Pattern

For complex apps, use this module organisation:

```text
apps/<app_name>/
  models.py
  enums.py
  selectors.py
  modules/
    <deep_module>.py
  api/
    serializers.py
    views.py
    urls.py
  tasks.py
  admin.py
  tests/
    test_<deep_module>.py
    test_api_<resource>.py
```

## 7.1 `models.py`

Owns persistence structure.

## 7.2 `selectors.py`

Owns read queries and queryset shaping.

Use selectors for:

- Lists.
- Search.
- Filtered queries.
- Prefetch/annotate optimisation.
- Permission-scoped querysets.

Selectors should not mutate state.

## 7.3 `modules/`

Owns deep business behaviour.

Examples:

```text
apps/approvals/modules/approval_case_engine.py
apps/disbursements/modules/disbursement_readiness.py
apps/repayments/modules/repayment_allocator.py
apps/interest/modules/interest_engine.py
```

## 7.4 `api/`

Owns HTTP layer:

- Serializers.
- Views.
- URLs.
- OpenAPI annotations.

## 7.5 `tasks.py`

Owns Celery task entry points.

Tasks should call module interfaces, not duplicate logic.

## 7.6 `tests/`

Test module behaviour through the module interface. Do not test private helper methods unless the helper itself is a public module.

---

# 8. Backend App Map

## 8.1 Foundation Apps

| App | Purpose |
|---|---|
| `accounts` | Users, sessions, login, password reset, user status |
| `rbac` | Roles, permissions, teams, authority types, object access |
| `audit` | Audit logs, workflow events, immutable evidence |
| `documents` | Document files, storage adapter, signed URLs, sensitivity |
| `configurations` | Versioned business configuration |
| `communications` | Email, SMS, letters, templates and delivery logs |
| `integrations` | Provider registry, integration events, jobs and adapters |
| `operations` | Health checks, scheduled job runs, operational dashboards |

## 8.2 Business Apps

| App | Purpose |
|---|---|
| `members` | Member master, profiles, nominees, witnesses, shareholding, land, crop |
| `kyc` | KYC profile, KYC documents, CKYC consent and re-KYC |
| `applications` | Loan application, reference number, completeness and deficiencies |
| `credit` | Eligibility, active status, loan limit, appraisal and risk |
| `approvals` | Approval matrix, approval cases, sanction and exceptions |
| `legal_documents` | Document templates, generated loan docs, signatures, stamps, notary, checklist |
| `security_instruments` | PoA, SH-4, CDSL, blank cheque, cancelled cheque and custody |
| `sap_workflow` | SAP customer profile request and customer code |
| `loans` | Loan account, loan ledger and loan account 360 |
| `disbursements` | Readiness, initiation, CFC authorisation and transfer success |
| `repayments` | Direct repayment, subsidiary deduction, allocation and reconciliation |
| `interest` | Interest invoice, accrual and capitalisation |
| `monitoring` | DPD, reminders and quarterly MIS |
| `defaults` | Default cases, grace period, assessment and extension |
| `recovery` | Non-payment notes, recovery decisions and recovery actions |
| `closure` | Closure readiness, NOC, security return and archive |
| `compliance` | Section 186, NBFC, KYC/re-KYC, stamp duty, money-lending, grievance |
| `reports` | Registers, exports and report jobs |

---

# 9. Foundation Modules

## 9.1 Permission Module

### Module Name

`rbac.modules.permission_engine`

### Interface

```python
class PermissionEngine:
    def require_permission(self, actor, permission_code: str) -> None: ...
    def has_permission(self, actor, permission_code: str) -> bool: ...
    def available_actions_for(self, actor, entity) -> list[AvailableAction]: ...
```

### What the Implementation Hides

- Role lookup.
- Team membership.
- Permission grants.
- User status.
- Permission versioning.
- Superuser/admin restrictions.
- Denial reasons.
- Available-action construction.

### Invariants

- Inactive/suspended/terminated users fail.
- Missing permission fails.
- Permission checks must be backend-enforced.
- Frontend permission helpers are not authoritative.

### Tests Through Interface

- Field Officer cannot approve sanction.
- Credit Manager cannot authorise disbursement.
- CFC cannot edit appraisal.
- Director cannot view unassigned approval case.
- Auditor has read-only access.

### Anti-Patterns

- Checking `if user.role == "cfo"` directly in views.
- Duplicating permission logic in React pages.
- Letting admin users approve loans by default.

---

## 9.2 Object Access Module

### Module Name

`rbac.modules.object_access`

### Interface

```python
class ObjectAccess:
    def require_application_access(self, actor, application) -> None: ...
    def require_loan_access(self, actor, loan_account) -> None: ...
    def require_document_access(self, actor, document_file, action: str) -> None: ...
    def scoped_applications_queryset(self, actor): ...
    def scoped_loan_accounts_queryset(self, actor): ...
```

### What the Implementation Hides

- Role scope rules.
- Team assignment rules.
- Approval assignment rules.
- Auditor read-only access.
- Sensitive document category logic.
- Future borrower self-access.

### Invariants

- List endpoints must filter by access scope.
- Detail endpoints must enforce object access.
- Document access requires both object access and sensitivity access.

---

## 9.3 Audit Module

### Module Name

`audit.modules.audit_recorder`

### Interface

```python
class AuditRecorder:
    def record(
        self,
        *,
        actor,
        action_code: str,
        entity,
        outcome: str = "success",
        old_value: dict | None = None,
        new_value: dict | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        ...
```

### What the Implementation Hides

- Request ID.
- IP address.
- User agent.
- Role/team snapshot.
- Sensitive value redaction.
- Audit table write.
- Workflow event write where required.

### Invariants

- Audit logs are append-only.
- Raw PAN, Aadhaar, bank account and cheque values are never stored in audit logs.
- Critical actions always record actor, action, entity, timestamp and outcome.

---

## 9.4 Sensitive Data Module

### Module Name

`documents.modules.sensitive_data_access` or `shared.masking`

### Interface

```python
class SensitiveDataModule:
    def mask_value(self, field_name: str, value: str) -> str: ...
    def reveal_field(self, *, actor, entity, field_name: str, reason: str) -> RevealedValue: ...
    def can_reveal(self, actor, entity, field_name: str) -> bool: ...
```

### What the Implementation Hides

- Field classification.
- Permission checks.
- Object access.
- Re-authentication requirements.
- Reveal timeout.
- Sensitive access audit.
- Rate limits.

### Invariants

- PAN/Aadhaar/bank/cheque/BO account are masked by default.
- Reveal requires explicit permission and reason.
- Reveal is audit logged.

---

## 9.5 Document Storage Module

### Module Name

`documents.modules.document_storage`

### Interface

```python
class DocumentStorage:
    def upload(self, *, actor, file, metadata: DocumentMetadata) -> DocumentFile: ...
    def get_download_url(self, *, actor, document_file_id, reason: str | None = None) -> DownloadGrant: ...
    def archive(self, *, actor, document_file_id, archive_reason: str) -> DocumentFile: ...
```

### What the Implementation Hides

- Storage provider adapter.
- File checksum.
- MIME validation.
- Virus scan hook.
- Sensitivity classification.
- Signed URL generation.
- Download audit.
- Retention metadata.

### Adapter Seams

| Seam | Adapter |
|---|---|
| Object storage | S3/DMS/local test adapter |
| Virus scanning | Disabled/manual/AV provider adapter |

---

# 10. Member and KYC Modules

## 10.1 Member Registry Module

### Module Name

`members.modules.member_registry`

### Interface

```python
class MemberRegistry:
    def create_member(self, *, actor, payload: CreateMemberPayload) -> Member: ...
    def update_member(self, *, actor, member_id, payload: UpdateMemberPayload) -> Member: ...
    def get_member_summary(self, *, actor, member_id) -> MemberSummary: ...
```

### Implementation Hides

- Individual vs FPC profile creation.
- PAN/Aadhaar encryption and hashing.
- Duplicate detection.
- Field-level masking.
- Audit events.

### Tests

- Create individual farmer.
- Create FPC borrower.
- Duplicate PAN rejected.
- Sensitive data masked.

## 10.2 Active Member Module

### Module Name

`members.modules.active_member_status`

### Interface

```python
class ActiveMemberStatusModule:
    def calculate(self, *, member_id, as_of_date) -> ActiveMemberStatusResult: ...
    def verify(self, *, actor, member_id, result_id, decision, reason) -> ActiveMemberStatusVerification: ...
```

### Implementation Hides

- Individual member 4-year supply condition.
- Individual relaxation condition.
- FPC 4-year supply condition.
- FPC relaxation condition.
- Service/employment route.
- Supply through Producer Institution.
- Status explanation.

### Invariants

- Eligibility must use a dated result.
- Overrides require reason and permission.
- Active status snapshot must be stored with application.

### Tests

- Individual supplied four financial years.
- Individual supplied one year under relaxation.
- Individual with three-year service route.
- Inactive member.
- FPC supplied four years.
- FPC supplied one year under relaxation.

## 10.3 KYC Module

### Module Name

`kyc.modules.kyc_profile`

### Interface

```python
class KycProfileModule:
    def create_or_update_profile(self, *, actor, party, payload) -> KycProfile: ...
    def verify_document(self, *, actor, document_id, decision, reason) -> KycDocumentVerification: ...
    def calculate_rekyc_due_date(self, *, party_id) -> date: ...
```

### Implementation Hides

- Party types: borrower, nominee, witness, authorised signatory.
- KYC document categories.
- CKYC consent requirement.
- Re-KYC two-year cycle.
- Beneficial ownership for FPCs.
- Sensitive file restrictions.

---

# 11. Loan Origination Modules

## 11.1 Loan Application Module

### Module Name

`applications.modules.loan_application_lifecycle`

### Interface

```python
class LoanApplicationLifecycle:
    def create_draft(self, *, actor, payload) -> LoanApplication: ...
    def submit(self, *, actor, application_id) -> LoanApplication: ...
    def return_with_deficiencies(self, *, actor, application_id, deficiencies) -> LoanApplication: ...
    def resolve_deficiency(self, *, actor, deficiency_id, payload) -> Deficiency: ...
    def cancel(self, *, actor, application_id, reason) -> LoanApplication: ...
```

### Implementation Hides

- Reference number generation.
- Required field validation.
- Required application documents.
- Nominee validation.
- Status transitions.
- Deficiency records.
- Notifications.
- Audit logs.

### Invariants

- Reference numbers are unique.
- Application cannot move to appraisal while incomplete.
- Disbursed applications cannot be cancelled.
- Deficiency resolution history remains.

## 11.2 Reference Number Module

### Module Name

`applications.modules.reference_number_generator`

### Interface

```python
class ReferenceNumberGenerator:
    def next_application_reference(self) -> str: ...
```

### Implementation Hides

- Sequence locking.
- Prefix configuration.
- Concurrency control.
- Historical import offsets.

### Invariants

- No duplicate `LO00000001` style references.
- Reference generation is transaction-safe.

---

# 12. Credit Assessment Modules

## 12.1 Eligibility Assessment Module

### Module Name

`credit.modules.eligibility_assessment`

### Interface

```python
class EligibilityAssessmentModule:
    def run(self, *, actor, application_id) -> EligibilityAssessmentResult: ...
    def override(self, *, actor, assessment_id, decision, reason) -> EligibilityAssessmentResult: ...
```

### Implementation Hides

- Active member check.
- Existing default check.
- Required documents.
- Land documents.
- KYC.
- Bank statement.
- Crop plan.
- Agreement to terms.
- Purpose category.
- Borrower/member status.
- Explanation generation.

### Invariants

- Ineligible applications cannot proceed unless approved exception route exists.
- Override is critical and audited.
- Assessment snapshot is tied to application version.

## 12.2 Loan Limit Module

### Module Name

`credit.modules.loan_limit_calculator`

### Interface

```python
class LoanLimitCalculator:
    def calculate_for_application(self, *, actor, application_id) -> LoanLimitAssessment: ...
```

### Interface Must Return

```python
@dataclass(frozen=True)
class LoanLimitAssessmentResult:
    application_id: UUID
    shareholding_based_limit: Decimal
    land_based_limit: Decimal
    final_eligible_amount: Decimal
    requested_amount: Decimal
    exceeds_limit: bool
    policy_version_id: UUID
    share_valuation_version_id: UUID
    scale_of_finance_version_id: UUID
    calculation_explanation: list[str]
    open_policy_warnings: list[str]
```

### Implementation Hides

- Number of shares.
- Share valuation.
- 30% vs 10% vs ₹200/share policy configuration.
- Board-approved policy versions.
- Land area under cultivation.
- Current cap ₹20,000 per acre.
- Lower-of-two rule.
- Exception flag.
- Rounding.
- Snapshot persistence.

### Invariants

- Final eligible amount is lower of shareholding and land-based limits.
- Calculation must snapshot policy versions.
- Historical assessments do not change when policy changes.
- Open policy ambiguity must be visible until resolved.

### Tests

- Share limit lower.
- Land limit lower.
- Requested amount below/equal/above limit.
- Zero shares.
- Missing share valuation.
- Policy version changed after assessment.

## 12.3 Appraisal Module

### Module Name

`credit.modules.appraisal_workflow`

### Interface

```python
class AppraisalWorkflow:
    def create_or_update(self, *, actor, application_id, payload) -> AppraisalNote: ...
    def submit_for_review(self, *, actor, appraisal_id) -> AppraisalNote: ...
    def review(self, *, actor, appraisal_id, decision, comments) -> AppraisalNote: ...
    def submit_to_sanction(self, *, actor, application_id) -> ApprovalCase: ...
```

### Implementation Hides

- Deputy Manager maker role.
- Credit Manager checker role.
- Risk assessment.
- Repayment capacity.
- Recommendation summary.
- TAT tracking.
- Approval case creation trigger.

### Invariants

- Credit Manager review required before sanction.
- Maker-checker separation enforced where configured.
- Appraisal cannot be edited after sanction submission without new version.

---

# 13. Approval Modules

## 13.1 Approval Case Engine

### Module Name

`approvals.modules.approval_case_engine`

### Interface

```python
class ApprovalCaseEngine:
    def create_for_application(self, *, actor, application_id) -> ApprovalCase: ...
    def record_action(self, *, actor, case_id, action: ApprovalActionInput) -> ApprovalCase: ...
    def get_required_approvers(self, *, application_id) -> RequiredApprovers: ...
```

### Implementation Hides

- Approval matrix threshold.
- CFO + one Director up to ₹5 lakh.
- CFO + two Directors above ₹5 lakh.
- Exception rule.
- Director/relative conflict.
- General meeting approval requirement.
- Approval action immutability.
- Sanction decision creation.
- Notifications.

### Invariants

- Approval case cannot become approved until all required approvals exist.
- Conflicted users cannot approve.
- Rejection requires reason.
- Return requires reason.
- Approval action is immutable.
- Re-approval after material change creates a new cycle.

## 13.2 Conflict of Interest Module

### Module Name

`approvals.modules.conflict_of_interest`

### Interface

```python
class ConflictOfInterestModule:
    def evaluate_for_application(self, application_id) -> ConflictAssessment: ...
    def require_no_conflicted_actor(self, *, actor, approval_case_id) -> None: ...
```

### Implementation Hides

- Borrower as Director.
- Borrower as committee member.
- Relative of Director.
- Material interest.
- Maker-checker conflicts.
- Excluded approvers.

---

# 14. Documentation Modules

## 14.1 Document Generation Module

### Module Name

`legal_documents.modules.document_generation`

### Interface

```python
class DocumentGenerationModule:
    def generate(self, *, actor, application_id, template_code: str) -> LoanDocument: ...
    def regenerate(self, *, actor, loan_document_id, reason: str) -> LoanDocument: ...
```

### Implementation Hides

- Template version selection.
- Merge field population.
- PDF generation.
- File storage.
- Document metadata.
- Version history.
- Audit.

### Invariants

- Generated documents store template version.
- Regeneration requires reason.
- Signed/executed documents cannot be silently overwritten.

## 14.2 Document Checklist Module

### Module Name

`legal_documents.modules.document_checklist`

### Interface

```python
class DocumentChecklistModule:
    def refresh_for_application(self, *, actor, application_id) -> DocumentChecklist: ...
    def mark_item_complete(self, *, actor, checklist_item_id, payload) -> ChecklistItem: ...
    def approve(self, *, actor, checklist_id, approval_role: str, comments: str | None = None) -> ChecklistApproval: ...
    def readiness(self, *, application_id) -> ChecklistReadinessResult: ...
```

### Implementation Hides

- Applicable document rules.
- Physical vs demat share security requirements.
- Signature status.
- Stamp duty.
- Notarisation.
- Bank verification.
- Checklist approval sequence.
- Blocker explanations.

### Invariants

- CS approval requires all legal docs verified.
- Credit Manager approval requires limits reviewed.
- Sanction Committee final checklist approval requires earlier approvals.
- Senior Manager Finance completion signature occurs after disbursement success.
- Missing required items block disbursement readiness.

## 14.3 Signature Mismatch Module

### Module Name

`legal_documents.modules.signature_mismatch`

### Interface

```python
class SignatureMismatchModule:
    def flag(self, *, actor, document_id, signer_id, reason) -> SignatureRecord: ...
    def resolve_with_bank_letter(self, *, actor, signature_record_id, document_file_id) -> SignatureRecord: ...
    def resolve_with_declaration(self, *, actor, signature_record_id, document_file_id) -> SignatureRecord: ...
```

### Implementation Hides

- Bank Verification Letter requirement.
- Declaration alternative.
- Checklist blocker update.
- Audit.

---

# 15. Security Instrument Modules

## 15.1 Security Package Module

### Module Name

`security_instruments.modules.security_package`

### Interface

```python
class SecurityPackageModule:
    def refresh_for_application(self, *, actor, application_id) -> SecurityPackage: ...
    def readiness(self, *, application_id) -> SecurityReadinessResult: ...
```

### Implementation Hides

- Physical shares require SH-4.
- Demat shares require CDSL pledge.
- PoA requirement.
- Blank-dated cheque requirement.
- Cancelled cheque requirement.
- Witness requirement.
- Custody status.
- Required evidence.

### Invariants

- Disbursement cannot proceed unless required security is complete or approved exception exists.
- Recovery cannot invoke security without approved recovery decision.

## 15.2 SH-4 Module

### Module Name

`security_instruments.modules.sh4_security`

### Interface

```python
class Sh4SecurityModule:
    def create(self, *, actor, application_id, payload) -> Sh4Record: ...
    def record_custody(self, *, actor, sh4_id, custody_event) -> CustodyEvent: ...
    def invoke(self, *, actor, sh4_id, recovery_decision_id, payload) -> Sh4Invocation: ...
    def release(self, *, actor, sh4_id, closure_id, payload) -> Sh4Release: ...
```

### Implementation Hides

- Witness shareholder validation.
- Physical share applicability.
- Custody movement.
- Recovery approval gate.
- Release after closure.
- Audit.

## 15.3 CDSL Pledge Module

### Module Name

`security_instruments.modules.cdsl_pledge`

### Interface

```python
class CdslPledgeModule:
    def create_record(self, *, actor, application_id, payload) -> CdslPledge: ...
    def record_prf_submitted(self, *, actor, pledge_id, payload) -> CdslPledge: ...
    def record_psn(self, *, actor, pledge_id, psn: str) -> CdslPledge: ...
    def record_acceptance(self, *, actor, pledge_id, payload) -> CdslPledge: ...
    def invoke(self, *, actor, pledge_id, recovery_decision_id, payload) -> CdslInvocation: ...
    def unpledge(self, *, actor, pledge_id, closure_id, payload) -> CdslUnpledge: ...
```

### Implementation Hides

- PRF milestone.
- PSN.
- Pledgee acceptance.
- Invocation form.
- Unpledge form.
- Evidence documents.
- Manual vs future API adapter.

## 15.4 Blank-Dated Cheque Module

### Module Name

`security_instruments.modules.blank_cheque`

### Interface

```python
class BlankChequeModule:
    def record_collected(self, *, actor, application_id, payload) -> BlankCheque: ...
    def reveal_details(self, *, actor, cheque_id, reason) -> RevealedChequeDetails: ...
    def invoke(self, *, actor, cheque_id, recovery_decision_id, payload) -> ChequeInvocation: ...
    def release(self, *, actor, cheque_id, closure_id, payload) -> ChequeRelease: ...
```

### Implementation Hides

- Cheque number encryption.
- Restricted reveal.
- Custody.
- Recovery approval.
- Release after closure.

---

# 16. SAP and Disbursement Modules

## 16.1 SAP Customer Profile Module

### Module Name

`sap_workflow.modules.sap_customer_profile`

### Interface

```python
class SapCustomerProfileModule:
    def create_request(self, *, actor, application_id) -> SapCustomerProfileRequest: ...
    def generate_excel(self, *, actor, request_id) -> DocumentFile: ...
    def complete(self, *, actor, request_id, payload) -> SapCustomerProfileRequest: ...
    def get_customer_code_for_member(self, member_id) -> SapCustomerCode | None: ...
```

### Implementation Hides

- Existing borrower SAP code reuse.
- Excel file generation.
- Required SAP fields.
- Sensitive field handling.
- Manual vs future API mode.
- Duplicate SAP code prevention.
- Audit.

### Adapter Seam

| Adapter | Use |
|---|---|
| Manual SAP adapter | MVP: user creates code in SAP and confirms |
| SAP API adapter | Future: call SAP directly |
| Fake SAP adapter | Tests |

## 16.2 Loan Account Module

### Module Name

`loans.modules.loan_account_lifecycle`

### Interface

```python
class LoanAccountLifecycle:
    def create_from_sanction(self, *, actor, application_id) -> LoanAccount: ...
    def get_ledger_summary(self, *, actor, loan_account_id) -> LoanLedgerSummary: ...
    def transition_status(self, *, actor, loan_account_id, transition, reason) -> LoanAccount: ...
```

### Implementation Hides

- Sanction snapshot.
- Loan account number.
- Initial principal.
- Current outstanding.
- Status history.
- Ledger summaries.
- Closure readiness.

## 16.3 Disbursement Readiness Module

### Module Name

`disbursements.modules.disbursement_readiness`

### Interface

```python
class DisbursementReadinessModule:
    def evaluate(self, *, actor, loan_account_id) -> DisbursementReadinessResult: ...
    def require_ready(self, *, actor, loan_account_id) -> None: ...
```

### Implementation Hides

- Sanction approved.
- Loan account created.
- Checklist approved.
- Security package complete.
- SAP code present.
- Bank account verified.
- Cancelled cheque verified.
- Signature mismatch resolved.
- Amount within sanction.
- Required approval sequence.

### Invariants

- Readiness result includes pass/fail details and blocker reasons.
- Disbursement cannot initiate unless readiness passes.

## 16.4 Disbursement Workflow Module

### Module Name

`disbursements.modules.disbursement_workflow`

### Interface

```python
class DisbursementWorkflow:
    def initiate(self, *, actor, loan_account_id, payload, idempotency_key: str) -> Disbursement: ...
    def authorise(self, *, actor, disbursement_id, payload) -> Disbursement: ...
    def mark_transfer_successful(self, *, actor, disbursement_id, payload) -> Disbursement: ...
    def mark_failed(self, *, actor, disbursement_id, payload) -> Disbursement: ...
```

### Implementation Hides

- Senior Manager Finance authority.
- CFC authority.
- Idempotency.
- UTR uniqueness.
- Bank evidence.
- Loan activation.
- Disbursement advice trigger.
- Audit.

### Adapter Seam

| Adapter | Use |
|---|---|
| Manual bank adapter | MVP: bank portal outside system |
| Bank API adapter | Future |
| Fake bank adapter | Tests |

---

# 17. Repayment and Interest Modules

## 17.1 Repayment Capture Module

### Module Name

`repayments.modules.repayment_capture`

### Interface

```python
class RepaymentCaptureModule:
    def record_direct(self, *, actor, loan_account_id, payload, idempotency_key: str) -> Repayment: ...
    def record_subsidiary_deduction(self, *, actor, loan_account_id, payload, idempotency_key: str) -> Repayment: ...
```

### Implementation Hides

- Source type.
- Bank reference uniqueness.
- Subsidiary deduction reference uniqueness.
- Bank statement link.
- Tri-party agreement warning/blocking.
- Audit.

## 17.2 Repayment Allocation Module

### Module Name

`repayments.modules.repayment_allocator`

### Interface

```python
class RepaymentAllocator:
    def allocate(self, *, actor, repayment_id) -> RepaymentAllocationResult: ...
```

### Implementation Hides

- Principal-first rule.
- Interest allocation.
- Charges allocation if configured.
- Overpayment handling.
- Outstanding updates.
- Ledger entries.
- Idempotency.

### Invariants

- Partial repayment reduces principal first.
- Duplicate allocation is blocked.
- Loan outstanding cannot become negative unless excess handling is configured.

## 17.3 Interest Engine

### Module Name

`interest.modules.interest_engine`

### Interface

```python
class InterestEngine:
    def generate_invoice(self, *, actor, loan_account_id, financial_year) -> InterestInvoice: ...
    def create_monthly_accrual(self, *, actor, loan_account_id, accrual_month) -> AccrualEntry: ...
    def capitalise_unpaid_interest(self, *, actor, loan_account_id, financial_year, idempotency_key: str) -> InterestCapitalisation: ...
```

### Implementation Hides

- Floating rate configuration.
- Financial year.
- Invoice numbering.
- Monthly accrual uniqueness.
- 30 April rule.
- Principal increase.
- Borrower communication.
- SAP posting status.

### Invariants

- One monthly accrual per loan/month.
- One capitalisation per loan/financial year.
- Capitalisation after 30 April only unless override is approved.
- Historical interest uses rate snapshot.

---

# 18. Monitoring, Default and Recovery Modules

## 18.1 DPD Monitoring Module

### Module Name

`monitoring.modules.dpd_monitoring`

### Interface

```python
class DpdMonitoringModule:
    def calculate_for_loan(self, *, loan_account_id, as_of_date) -> DpdStatus: ...
    def calculate_portfolio(self, *, actor, as_of_date) -> PortfolioDpdRun: ...
```

### Implementation Hides

- Due date calculations.
- SOP buckets: 1–2 years, 2–3 years, 3+ years.
- Operational buckets if configured.
- Reminder triggers.
- CFO MIS data.

## 18.2 Reminder Module

### Module Name

`monitoring.modules.reminder_engine`

### Interface

```python
class ReminderEngine:
    def create_reminder(self, *, actor, loan_account_id, reminder_type, channel) -> Reminder: ...
    def send_due_reminders(self, *, actor=None) -> ReminderRun: ...
```

### Implementation Hides

- SMS/email/phone channel.
- Quarterly outstanding reminders.
- Communication templates.
- Delivery logging.
- Duplicate prevention.

## 18.3 Default Workflow Module

### Module Name

`defaults.modules.default_workflow`

### Interface

```python
class DefaultWorkflow:
    def open_if_missed_repayment(self, *, loan_account_id, as_of_date) -> DefaultCase | None: ...
    def start_grace_period(self, *, actor, default_case_id) -> DefaultCase: ...
    def assess_reason(self, *, actor, default_case_id, payload) -> DefaultAssessment: ...
    def grant_extension(self, *, actor, default_case_id, payload) -> DefaultExtension: ...
```

### Implementation Hides

- Missed principal detection.
- Three-month grace period.
- Intentional/non-intentional classification.
- One-year extension.
- Extension Note document.
- Audit.

## 18.4 Recovery Module

### Module Name

`recovery.modules.recovery_workflow`

### Interface

```python
class RecoveryWorkflow:
    def create_non_payment_note(self, *, actor, default_case_id, payload) -> NonPaymentNote: ...
    def submit_for_recovery_approval(self, *, actor, non_payment_note_id) -> ApprovalCase: ...
    def record_recovery_decision(self, *, actor, approval_case_id) -> RecoveryDecision: ...
    def initiate_recovery_action(self, *, actor, recovery_decision_id, payload) -> RecoveryAction: ...
    def complete_recovery_action(self, *, actor, recovery_action_id, payload) -> RecoveryAction: ...
```

### Implementation Hides

- Extension expiry.
- Non-Payment Note.
- Approval authority.
- SH-4/CDSL/cheque action selection.
- Company Secretary execution.
- Evidence upload.
- Audit.

### Invariants

- Recovery action cannot be initiated without approved recovery decision.
- Security instrument invocation calls the appropriate security module.
- Recovery approval route is configurable due to open question.

---

# 19. Closure and Compliance Modules

## 19.1 Closure Module

### Module Name

`closure.modules.loan_closure`

### Interface

```python
class LoanClosureModule:
    def evaluate_readiness(self, *, actor, loan_account_id) -> ClosureReadinessResult: ...
    def close(self, *, actor, loan_account_id, payload) -> LoanClosure: ...
    def generate_noc(self, *, actor, closure_id) -> NocRecord: ...
    def record_security_return(self, *, actor, closure_id, payload) -> SecurityReturn: ...
    def archive(self, *, actor, closure_id, payload) -> ArchiveRecord: ...
```

### Implementation Hides

- Zero outstanding check.
- NOC template.
- SH-4 return.
- Blank cheque return.
- CDSL unpledge.
- Archive location.
- Retention at least eight years.
- Audit.

## 19.2 Section 186 Module

### Module Name

`compliance.modules.section186_tracker`

### Interface

```python
class Section186TrackerModule:
    def calculate(self, *, actor, period_id, payload) -> Section186Tracker: ...
    def submit_for_review(self, *, actor, tracker_id) -> Section186Tracker: ...
    def review(self, *, actor, tracker_id, decision, comments) -> Section186Tracker: ...
```

### Implementation Hides

- 60% of paid-up capital + free reserves + securities premium.
- 100% of free reserves + securities premium.
- Higher-of-two limit.
- Current exposure.
- Special resolution requirement.
- Evidence documents.

## 19.3 NBFC Principal Business Test Module

### Module Name

`compliance.modules.nbfc_principal_business_test`

### Interface

```python
class NbfcPrincipalBusinessTestModule:
    def calculate(self, *, actor, period_id, payload) -> NbfcTestResult: ...
```

### Implementation Hides

- Financial assets ratio.
- Financial income ratio.
- >50% and >50% trigger.
- Early warning thresholds.
- CFO review.

## 19.4 Compliance Task Module

### Module Name

`compliance.modules.compliance_task_engine`

### Interface

```python
class ComplianceTaskEngine:
    def generate_due_tasks(self, *, as_of_date) -> ComplianceTaskRun: ...
    def submit_evidence(self, *, actor, task_id, payload) -> ComplianceTask: ...
    def review_evidence(self, *, actor, task_id, decision, comments) -> ComplianceTask: ...
```

### Implementation Hides

- Frequencies.
- Owners.
- Escalation.
- Evidence requirements.
- Audit.

---

# 20. Integration Modules and Adapter Seams

## 20.1 Dependency Categories

Use these categories to decide where seams belong:

| Category | Examples in This Platform | Seam Strategy |
|---|---|---|
| In-process pure computation | Loan limit, Section 186, NBFC test, DPD calculation | No external adapter; test directly through module interface |
| Local-substitutable dependency | PostgreSQL test DB, local file storage, in-memory email/SMS | Use real/local test stand-in; no unnecessary external seam |
| Remote but owned | Future internal services, borrower portal API if separate | Define port/interface and adapter |
| True external | SAP, bank, SMS gateway, email provider, CKYC, bureau, e-sign, CDSL provider | Inject adapter at seam; fake adapter in tests |

## 20.2 Integration Provider Registry

### Module Name

`integrations.modules.integration_registry`

### Interface

```python
class IntegrationRegistry:
    def get_adapter(self, provider_code: str): ...
    def record_event(self, event: IntegrationEventInput) -> IntegrationEvent: ...
    def enqueue_job(self, job: IntegrationJobInput) -> IntegrationJob: ...
```

## 20.3 Adapter Principles

| Principle | Rule |
|---|---|
| True external systems need adapters | SAP, bank, email, SMS, storage, CDSL, CKYC, bureau and e-sign. |
| Manual mode is an adapter | Manual SAP/bank/CDSL workflows should satisfy the same seam as future APIs. |
| Test fakes are adapters | Tests use fake/in-memory adapters through the same interface. |
| Core logic owns decisions | Adapters should not decide eligibility, approval or readiness. |
| Payloads are sanitised | Integration events never store raw Aadhaar/PAN/bank data. |
| Idempotency is explicit | External actions that can duplicate effects need keys. |

## 20.4 SAP Adapter Interface

```python
class SapAdapter:
    def create_customer_profile_request(self, payload, idempotency_key: str) -> SapCustomerResult: ...
    def get_customer_status(self, external_reference: str) -> SapCustomerStatus: ...
```

### MVP Manual Adapter

- Creates internal request.
- Generates Excel.
- Waits for user confirmation.
- Stores SAP code.

### Future API Adapter

- Calls SAP API.
- Parses response.
- Handles retry.
- Stores external references.

## 20.5 Bank Adapter Interface

```python
class BankAdapter:
    def initiate_payment(self, payload, idempotency_key: str) -> BankPaymentResult: ...
    def get_payment_status(self, bank_reference: str) -> BankPaymentStatus: ...
```

### MVP Manual Adapter

- Records bank portal initiation.
- Requires CFC manual authorisation.
- Requires UTR.

### Future API Adapter

- Calls bank payment API.
- Polls or receives webhook.
- Never retries payment creation blindly.

## 20.6 Communication Adapter Interface

```python
class EmailAdapter:
    def send_email(self, payload, idempotency_key: str) -> CommunicationResult: ...

class SmsAdapter:
    def send_sms(self, payload, idempotency_key: str) -> CommunicationResult: ...
```

## 20.7 Storage Adapter Interface

```python
class StorageAdapter:
    def put_object(self, file, metadata) -> StoredObject: ...
    def signed_download_url(self, object_key, expires_in_seconds: int) -> str: ...
    def delete_or_archive_object(self, object_key) -> None: ...
```

---

# 21. State Machine Design

## 21.1 State Modules

Workflow state transitions should be implemented by modules, not direct status edits.

State machine modules:

| Workflow | Module |
|---|---|
| Loan Application | `applications.modules.loan_application_lifecycle` |
| Appraisal | `credit.modules.appraisal_workflow` |
| Approval Case | `approvals.modules.approval_case_engine` |
| Document Checklist | `legal_documents.modules.document_checklist` |
| Security Package | `security_instruments.modules.security_package` |
| SAP Request | `sap_workflow.modules.sap_customer_profile` |
| Disbursement | `disbursements.modules.disbursement_workflow` |
| Loan Account | `loans.modules.loan_account_lifecycle` |
| Repayment | `repayments.modules.repayment_capture` |
| Default Case | `defaults.modules.default_workflow` |
| Recovery | `recovery.modules.recovery_workflow` |
| Closure | `closure.modules.loan_closure` |
| Compliance Task | `compliance.modules.compliance_task_engine` |

## 21.2 State Transition Pattern

```python
def transition_to_next_state(actor, entity_id, payload):
    entity = selectors.get_for_update(entity_id)

    permission_engine.require_permission(actor, "some.permission")
    object_access.require_entity_access(actor, entity)
    workflow_guard.require_state(entity, ["allowed_state"])
    business_rule_module.validate(entity, payload)

    with transaction.atomic():
        old_snapshot = entity.snapshot()
        entity.status = "next_state"
        entity.save(update_fields=["status", "updated_at"])

        audit_recorder.record(
            actor=actor,
            action_code="entity.transitioned",
            entity=entity,
            old_value=old_snapshot,
            new_value=entity.snapshot(),
        )

    return entity
```

## 21.3 Direct Status Update Rule

Direct status updates should be disallowed except:

- Data migration with migration batch.
- Admin repair with incident/change record.
- Test setup/factories.

Production code should use workflow modules.

---

# 22. Transaction and Idempotency Design

## 22.1 Transaction Boundaries

Use database transactions for operations that create multiple related records.

Critical transactional modules:

- Application submission.
- Completeness check.
- Eligibility assessment.
- Loan limit calculation.
- Appraisal review.
- Approval action.
- Sanction decision.
- Checklist approval.
- SAP completion.
- Loan account creation.
- Disbursement initiation.
- Disbursement success.
- Repayment capture.
- Repayment allocation.
- Interest capitalisation.
- Recovery action.
- Closure.
- Security return.
- Compliance evidence review.

## 22.2 Idempotency Module

### Module Name

`shared.idempotency`

### Interface

```python
class IdempotencyModule:
    def run_once(self, *, key: str, actor, operation_name: str, fn: Callable) -> IdempotentResult: ...
```

### Required For

| Operation | Reason |
|---|---|
| Disbursement initiation | Prevent duplicate payment |
| Bank transfer success | Prevent duplicate activation |
| Repayment capture | Prevent duplicate receipt |
| Repayment allocation | Prevent duplicate ledger change |
| Interest accrual | Prevent duplicate accrual |
| Interest capitalisation | Prevent duplicate principal increase |
| Email/SMS send | Prevent duplicate borrower communication |
| Recovery action | Prevent duplicate security invocation |
| Report export | Prevent duplicate heavy job |

## 22.3 Concurrency Controls

| Scenario | Control |
|---|---|
| Reference number generation | DB sequence / row lock |
| Approval actions | Transaction and uniqueness per approver/case |
| Disbursement initiation | Idempotency + loan lock |
| Repayment allocation | Loan account row lock |
| Interest capitalisation | Unique loan/FY |
| Closure | Loan account row lock |
| Config activation | Effective-date uniqueness |
| Document checklist approval | Checklist row lock |

---

# 23. Frontend Codebase Design

## 23.1 Frontend Top-Level Structure

```text
frontend/src/
  app/
    App.tsx
    routes.tsx
    providers/
      AuthProvider.tsx
      QueryProvider.tsx
      PermissionsProvider.tsx
      ToastProvider.tsx
    layouts/
      AppShell.tsx
      AuthLayout.tsx

  shared/
    ui/
      Button/
      FormField/
      DataTable/
      StatusBadge/
      StageStepper/
      Modal/
      FileUpload/
      DocumentViewer/
      AuditTimeline/
    lib/
      apiClient.ts
      permissions.ts
      formatCurrency.ts
      formatDate.ts
      mask.ts
      errors.ts
    types/

  features/
    auth/
    dashboard/
    admin/
    members/
    kyc/
    applications/
    credit/
    approvals/
    documentation/
    security-instruments/
    sap/
    disbursements/
    loan-accounts/
    repayments/
    interest/
    monitoring/
    defaults/
    recovery/
    closure/
    compliance/
    reports/
    audit/

  test/
    fixtures/
    mocks/
    setup.ts
```

## 23.2 Frontend Module Rule

A React feature module should own:

- Routes for that feature.
- Page modules.
- Feature-specific hooks.
- Feature-specific types.
- Feature-specific UI modules.
- API call wrappers for that feature.
- Tests.

The shared folder should contain only modules used by multiple features.

## 23.3 React Page Rule

React pages should not implement business rules.

Pages should:

- Render data returned by backend.
- Submit user actions.
- Show `available_actions`.
- Show backend validation errors.
- Handle loading/empty/error states.
- Use shared UI modules.

Pages should not:

- Decide whether disbursement is ready.
- Calculate loan limits.
- Decide approvers.
- Allocate repayments.
- Decide if recovery is allowed.
- Reveal sensitive fields without backend call.
- Derive compliance status locally.

## 23.4 Frontend Available Actions Module

### Module Name

`shared/lib/availableActions.ts`

### Interface

```ts
export function findAction(
  actions: AvailableAction[],
  actionCode: string
): AvailableAction | undefined;

export function isActionEnabled(
  actions: AvailableAction[],
  actionCode: string
): boolean;
```

### Usage

React pages should render action buttons based on backend-provided `available_actions`.

```tsx
<ActionButton
  action={findAction(application.available_actions, "submit_to_sanction_committee")}
  onClick={submitToSanction}
/>
```

### Invariant

Frontend action visibility is usability only. Backend is authoritative.

## 23.5 Frontend API Client Module

### Module Name

`shared/lib/apiClient`

### Interface

```ts
apiClient.get<T>(path: string, options?: RequestOptions): Promise<T>
apiClient.post<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T>
apiClient.patch<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T>
apiClient.upload<T>(path: string, formData: FormData, options?: RequestOptions): Promise<T>
```

### Implementation Hides

- JWT access token.
- Refresh flow.
- Request ID.
- Error envelope parsing.
- 401 handling.
- 403/409 messaging.
- File upload progress.

## 23.6 Form Modules

Use form modules to keep complex forms local but not business-rule-heavy.

Example:

```text
features/applications/
  pages/
    NewLoanApplicationPage.tsx
  modules/
    loanApplicationFormSchema.ts
    useLoanApplicationDraft.ts
    applicationFieldGroups.ts
```

Client-side validation mirrors simple field requirements only. Backend remains authoritative.

---

# 24. Frontend Feature Modules

## 24.1 `features/members`

Owns:

- Member Directory.
- Member Profile.
- Nominee panel.
- Witness panel.
- Shareholding panel.
- Land/crop panel.
- Sensitive field reveal UI.

Uses backend modules:

- Member Registry.
- Active Member Status.
- KYC Profile.

## 24.2 `features/applications`

Owns:

- New Loan Application.
- Application Detail.
- Completeness Check.
- Deficiency Resolution.
- Rejection Note.

Uses backend modules:

- Loan Application Lifecycle.
- Reference Number Generator.
- Document Storage.

## 24.3 `features/credit`

Owns:

- Eligibility Assessment.
- Loan Limit Calculator.
- Appraisal Note.
- Credit Manager Review.

Uses backend modules:

- Eligibility Assessment.
- Loan Limit Calculator.
- Appraisal Workflow.

## 24.4 `features/approvals`

Owns:

- Approval Workbench.
- Approval Case Detail.
- Sanction Decision.
- Credit Sanction Register.
- Exception Register.
- Special Case Approval.

Uses backend modules:

- Approval Case Engine.
- Conflict of Interest.

## 24.5 `features/documentation`

Owns:

- Documentation Workspace.
- Template Management.
- Document Generation.
- Signature Records.
- Stamp Duty.
- Notarisation.
- Bank Verification.
- Document Checklist.

Uses backend modules:

- Document Generation.
- Document Checklist.
- Signature Mismatch.

## 24.6 `features/security-instruments`

Owns:

- PoA.
- SH-4.
- CDSL pledge.
- Blank cheque.
- Cancelled cheque.
- Custody event.

Uses backend modules:

- Security Package.
- SH-4 Security.
- CDSL Pledge.
- Blank Cheque.

## 24.7 `features/disbursements`

Owns:

- SAP request/confirmation.
- Loan account creation.
- Disbursement readiness.
- Payment initiation.
- CFC authorisation.
- Transfer success.
- Disbursement advice.

Uses backend modules:

- SAP Customer Profile.
- Loan Account Lifecycle.
- Disbursement Readiness.
- Disbursement Workflow.

## 24.8 `features/repayments`

Owns:

- Direct repayment entry.
- Subsidiary deduction entry.
- Bank statement upload.
- Reconciliation.
- Allocation.
- SAP posting reference.

Uses backend modules:

- Repayment Capture.
- Repayment Allocation.
- Bank Statement Matching.

## 24.9 `features/interest`

Owns:

- Interest invoice.
- Monthly accrual.
- Capitalisation.
- Borrower intimation.

Uses backend module:

- Interest Engine.

## 24.10 `features/defaults` and `features/recovery`

Owns:

- Default case detail.
- Grace period.
- Assessment.
- Extension.
- Non-Payment Note.
- Recovery approval.
- Recovery action.

Uses backend modules:

- Default Workflow.
- Recovery Workflow.

## 24.11 `features/closure`

Owns:

- Closure readiness.
- Loan closure.
- NOC.
- Security return.
- Archive.

Uses backend module:

- Loan Closure.

## 24.12 `features/compliance`

Owns:

- Compliance dashboard.
- Section 186.
- NBFC principal business test.
- KYC/re-KYC tracker.
- Stamp duty register.
- Money-lending review.
- Grievance register.

Uses backend modules:

- Section 186 Tracker.
- NBFC Principal Business Test.
- Compliance Task Engine.

---

# 25. HTTP Interface Design

## 25.1 HTTP Layer Responsibility

The HTTP layer exposes the platform’s module interfaces to the frontend.

It should be consistent but not leak implementation details.

## 25.2 Standard Response Envelope

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_123",
    "available_actions": []
  }
}
```

## 25.3 Error Envelope

```json
{
  "success": false,
  "error": {
    "code": "DISBURSEMENT_READINESS_FAILED",
    "message": "Disbursement cannot be initiated because required readiness checks failed.",
    "details": {
      "failed_checks": [
        {
          "check_code": "sap_customer_code",
          "message": "SAP customer code is missing."
        }
      ]
    }
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

## 25.4 HTTP Interface Rules

| Rule | Requirement |
|---|---|
| Use nouns for resources | `/loan-applications/{id}/` |
| Use actions for workflow transitions | `/loan-applications/{id}/submit/` |
| Keep transition endpoints explicit | Avoid generic `PATCH status` |
| Include available actions in details | Frontend can render accurate buttons |
| Return blocker reasons | Users need to know why action is disabled |
| Use idempotency headers | Required for financial/critical actions |
| Mask sensitive values | Default response behaviour |
| Standardise errors | QA and frontend rely on codes |

---

# 26. Testing Through Interfaces

## 26.1 Test Surface Rule

The module interface is the test surface.

Do not write long-lived tests that depend on private helper functions if the behaviour can be tested through the module interface.

## 26.2 Replace, Do Not Layer

When a deep module replaces scattered shallow logic:

- Write new tests through the deep module interface.
- Delete old brittle tests around shallow helpers.
- Keep tests focused on observable outcomes.

## 26.3 Test Types by Module

| Module Type | Test Strategy |
|---|---|
| Pure calculation modules | Unit tests through interface |
| Workflow modules | Transactional tests with test database |
| Permission modules | Role/object test matrix |
| External adapter modules | Fake adapter tests and contract tests |
| Document modules | Template fixture tests and file storage fake |
| Financial modules | Idempotency and concurrency tests |
| Scheduled job modules | Job-run tests invoking module interface |
| Frontend modules | UI behaviour tests using mocked HTTP interface |

## 26.4 Example: Loan Limit Tests

Good:

```python
def test_final_limit_is_lower_of_share_and_land_limits():
    result = loan_limit_calculator.calculate_for_application(
        actor=credit_user,
        application_id=application.id,
    )

    assert result.final_eligible_amount == Decimal("400000.00")
    assert result.exceeds_limit is False
```

Bad:

```python
def test_private_share_formula_helper():
    assert _share_formula(1000, Decimal("200.00")) == ...
```

The private helper can change. The result must remain correct.

---

# 27. Deep Module Inventory

## 27.1 Must-Be-Deep Modules

These modules should hide significant SOP complexity behind small interfaces.

| Module | Why It Must Be Deep |
|---|---|
| Permission Engine | Prevents scattered role checks and security bugs |
| Object Access | Prevents inconsistent data exposure |
| Sensitive Data Access | Centralises masking/reveal/audit |
| Document Storage | Hides storage provider, signed URLs and audit |
| Active Member Status | Encapsulates complex active/relaxation rules |
| Eligibility Assessment | Centralises pass/fail criteria |
| Loan Limit Calculator | Encapsulates policy ambiguity and lower-of-two rule |
| Appraisal Workflow | Enforces maker-checker and TAT |
| Approval Case Engine | Encapsulates threshold, approvers, conflicts and decisions |
| Document Checklist | Encapsulates document readiness gates |
| Security Package | Encapsulates physical/demat security requirements |
| SAP Customer Profile | Encapsulates manual/API SAP workflow |
| Disbursement Readiness | Prevents disbursement bypass |
| Disbursement Workflow | Enforces initiation, CFC, UTR and activation |
| Repayment Allocator | Enforces principal-first and ledger updates |
| Interest Engine | Encapsulates invoice, accrual and capitalisation |
| DPD Monitoring | Centralises ageing and MIS |
| Default Workflow | Encapsulates grace, assessment and extension |
| Recovery Workflow | Prevents unauthorised security invocation |
| Loan Closure | Encapsulates NOC, security return and archive |
| Compliance Calculators | Encapsulate Section 186 and NBFC rules |
| Report Export | Centralises export permissions and masking |

## 27.2 Should-Stay-Thin Modules

These modules can remain thin.

| Module | Reason |
|---|---|
| DRF views | Translate HTTP to module call |
| Serializers | Validate payload shape |
| React pages | Render data and submit actions |
| Formatting helpers | Currency/date formatting |
| Static status badge mapping | Simple presentation |
| URL routers | Framework wiring |
| Admin registration | Django admin wiring |
| Celery task wrapper | Call module interface |

---

# 28. Shallow Module Smells

Avoid these smells:

## 28.1 Pass-Through Module

```python
class LoanService:
    def calculate_limit(self, *args, **kwargs):
        return loan_limit_calculator.calculate(*args, **kwargs)
```

If it adds no leverage, delete it.

## 28.2 View-Owned Business Rule

```python
if amount > 500000:
    required_directors = 2
else:
    required_directors = 1
```

This belongs in Approval Case Engine.

## 28.3 React-Owned Business Rule

```tsx
const canDisburse =
  loan.hasSapCode &&
  loan.checklistStatus === "approved" &&
  loan.securityStatus === "complete";
```

This belongs in Disbursement Readiness module. Frontend should display backend result.

## 28.4 Fake Generic Manager

```python
class ApplicationManager:
    def do_action(self, action_name, payload):
        ...
```

This hides too little and makes actions untyped. Use explicit module interfaces.

## 28.5 Premature Repository Interface

```python
class MemberRepositoryInterface:
    ...
```

If the only production persistence is Django ORM and tests use test DB, this seam is usually unnecessary. Use selectors and test DB.

---

# 29. Codebase Documentation Files

## 29.1 `CONTEXT.md`

The repo should maintain a high-level context file.

Recommended contents:

- Product purpose.
- Core SOP stages.
- Core domain terms.
- Role model.
- Critical workflow gates.
- Sensitive data rules.
- Integration modes.
- Current open decisions.
- Pointers to major specs.

## 29.2 ADR Directory

Use ADRs for codebase decisions that affect long-term maintainability.

Recommended ADRs:

| ADR | Topic |
|---|---|
| ADR-001 | Monorepo structure |
| ADR-002 | Django app/module structure |
| ADR-003 | JWT/session strategy |
| ADR-004 | RBAC and object access strategy |
| ADR-005 | Audit log immutability |
| ADR-006 | Sensitive data encryption/masking |
| ADR-007 | Manual-first integration adapters |
| ADR-008 | Document storage provider |
| ADR-009 | Workflow state machine pattern |
| ADR-010 | Idempotency strategy |
| ADR-011 | Report/export architecture |
| ADR-012 | Celery job architecture |
| ADR-013 | Data migration strategy |
| ADR-014 | Feature flag strategy |
| ADR-015 | Frontend feature-slice structure |

## 29.3 Module README Files

Each major app should include a README:

```text
apps/approvals/README.md
apps/disbursements/README.md
apps/repayments/README.md
apps/security_instruments/README.md
```

Each README should include:

- Purpose.
- Public module interfaces.
- Key states.
- Permissions.
- Invariants.
- Adapter seams.
- Test strategy.
- Open questions.

---

# 30. Design It Twice Candidates

For complex modules, design at least two interface options before committing.

## 30.1 High-Value Candidates

| Candidate | Why Design Twice |
|---|---|
| Approval Case Engine | Thresholds, conflicts, exceptions and future board/general meeting routes |
| Document Checklist | Many documents, signatures, security types and approval sequence |
| Disbursement Readiness | Critical financial gate with many dependencies |
| Repayment Allocator | Financial ledger correctness and future charges/interest |
| Interest Engine | Floating rate, invoices, accruals, capitalisation |
| Recovery Workflow | Legal risk and open approval authority |
| Compliance Task Engine | Many periodic controls and owners |
| Integration Registry | Manual/API/future adapter architecture |

## 30.2 Example: Disbursement Readiness Interface Alternatives

### Option A — Minimal Interface

```python
readiness = disbursement_readiness.evaluate(actor=actor, loan_account_id=id)
readiness.require_ready()
```

High depth, simple callers.

### Option B — Flexible Interface

```python
readiness = disbursement_readiness.evaluate(
    actor=actor,
    loan_account_id=id,
    checks=[
        "sanction",
        "documentation",
        "security",
        "sap",
        "bank",
    ],
    mode="strict",
)
```

More flexible but larger interface.

### Option C — Common Caller Optimised

```python
ready, blockers = disbursement_readiness.for_initiation(actor, loan_account_id)
```

Very easy for UI and payment initiation, less general.

### Recommendation

Use Option A internally and expose a frontend-friendly response shape through HTTP. Keep check selection internal unless future use cases justify it.

---

# 31. Backend Coding Conventions

## 31.1 Naming

| Thing | Convention |
|---|---|
| Module classes | `LoanLimitCalculator`, `ApprovalCaseEngine` |
| Module files | `loan_limit_calculator.py`, `approval_case_engine.py` |
| Input dataclasses | `CreateApplicationInput`, `ApprovalActionInput` |
| Result dataclasses | `LoanLimitResult`, `ReadinessResult` |
| Enum names | `LoanApplicationStatus`, `ApprovalCaseStatus` |
| Permission codes | `module.resource.action` |
| Audit actions | `entity.action_past_tense` |
| Celery tasks | `app_name.task_name` |
| Adapter classes | `ManualSapAdapter`, `RblBankAdapter`, `FakeSmsAdapter` |

## 31.2 Error Codes

Use stable machine-readable error codes.

Examples:

```text
MEMBER_NOT_ACTIVE
NOMINEE_MINOR_NOT_ALLOWED
APPLICATION_INCOMPLETE
ELIGIBILITY_FAILED
LOAN_LIMIT_EXCEEDED
APPRAISAL_REVIEW_REQUIRED
APPROVAL_REQUIRED
CONFLICTED_APPROVER_NOT_ALLOWED
DOCUMENT_CHECKLIST_INCOMPLETE
SECURITY_PACKAGE_INCOMPLETE
SAP_CUSTOMER_CODE_MISSING
DISBURSEMENT_READINESS_FAILED
CFC_AUTHORISATION_REQUIRED
DUPLICATE_BANK_REFERENCE
OUTSTANDING_BALANCE_EXISTS
RECOVERY_APPROVAL_REQUIRED
SENSITIVE_REVEAL_REASON_REQUIRED
```

## 31.3 Decimal and Money

Use a shared Money/Decimal utility.

Rules:

- Never use float for currency.
- Store money as `Decimal`.
- Apply consistent rounding.
- Include currency code if multi-currency ever possible.
- Financial modules should use transaction locks.

## 31.4 Dates and Timezones

Rules:

- Store timestamps in UTC.
- Display dates/times in configured business timezone.
- Financial year utilities centralised.
- Due date calculations centralised.
- Grace and extension date calculations tested.

---

# 32. Frontend Coding Conventions

## 32.1 Naming

| Thing | Convention |
|---|---|
| Feature folder | `features/loan-applications` or `features/applications` |
| Page module | `LoanApplicationDetailPage.tsx` |
| Hook | `useLoanApplicationDetail` |
| API wrapper | `loanApplicationApi.ts` |
| Types | `loanApplicationTypes.ts` |
| Form schema | `loanApplicationFormSchema.ts` |
| UI module | `LoanLimitCard.tsx` |
| Test | `LoanLimitCard.test.tsx` |

## 32.2 State Management

Recommended:

- Server state: React Query or equivalent.
- Auth state: auth provider.
- Form state: React Hook Form or equivalent.
- UI state: local state.
- Global business state: avoid duplicating backend state.

## 32.3 Frontend Error Handling

Frontend should handle:

- 400 validation errors.
- 401 expired session.
- 403 permission denied.
- 404 missing entity.
- 409 workflow blocker.
- 422 business rule failure if used.
- 500 unexpected error.

Workflow errors should show blocker details.

## 32.4 Sensitive Data Rules

React must:

- Never store full PAN/Aadhaar/bank/cheque values in persistent browser storage.
- Never put sensitive values in URLs.
- Never log sensitive values.
- Clear revealed values after timeout.
- Rely on backend reveal endpoint.
- Use masked values returned by backend.

---

# 33. Report and Export Module Design

## 33.1 Report Module

### Module Name

`reports.modules.report_export`

### Interface

```python
class ReportExportModule:
    def generate(self, *, actor, report_code: str, filters: dict, idempotency_key: str) -> ReportJob: ...
    def get_download(self, *, actor, report_job_id, reason: str | None = None) -> DownloadGrant: ...
```

### Implementation Hides

- Report query.
- Permission checks.
- Sensitive column masking.
- Async job.
- Export file creation.
- Signed URL.
- Audit.

## 33.2 Reports Should Use Selectors

Reports should not query random models directly in many places.

Use report-specific selectors:

```python
reports/selectors/loan_request_register.py
reports/selectors/credit_sanction_register.py
reports/selectors/dpd_report.py
reports/selectors/compliance_dashboard.py
```

## 33.3 Export Rules

- Read permission does not imply export permission.
- Sensitive export requires separate permission.
- Export reason required for sensitive reports.
- Export links expire.
- Export action audit logged.

---

# 34. Scheduled Job Design

## 34.1 Job Module Pattern

Celery tasks should be thin wrappers:

```python
@shared_task(name="monitoring.calculate_daily_dpd")
def calculate_daily_dpd():
    return dpd_monitoring_module.calculate_portfolio(actor=system_actor(), as_of_date=today())
```

The job logic belongs in module interfaces.

## 34.2 Job Run Module

### Module Name

`operations.modules.job_run_recorder`

### Interface

```python
class JobRunRecorder:
    def start(self, job_name: str, triggered_by) -> JobRun: ...
    def complete(self, job_run_id, result) -> JobRun: ...
    def fail(self, job_run_id, error) -> JobRun: ...
```

## 34.3 Scheduled Jobs

| Job | Module Interface |
|---|---|
| DPD calculation | `DpdMonitoringModule.calculate_portfolio` |
| Grace expiry | `DefaultWorkflow.process_grace_expiries` |
| Extension expiry | `DefaultWorkflow.process_extension_expiries` |
| Monthly accrual | `InterestEngine.create_monthly_accruals_for_portfolio` |
| Interest invoice | `InterestEngine.generate_year_end_invoices` |
| Capitalisation | `InterestEngine.capitalise_due_interest` |
| Re-KYC task generation | `ComplianceTaskEngine.generate_due_tasks` |
| Section 186 reminder | `ComplianceTaskEngine.generate_due_tasks` |
| NBFC test reminder | `ComplianceTaskEngine.generate_due_tasks` |
| Email/SMS retry | `CommunicationsModule.retry_failed` |

---

# 35. Migration Code Design

## 35.1 Migration Module

### Module Name

`scripts.migration.legacy_migration_runner`

### Interface

```python
class LegacyMigrationRunner:
    def dry_run(self, source_path: str) -> MigrationReport: ...
    def execute(self, source_path: str, batch_id: str) -> MigrationReport: ...
    def rollback_batch(self, batch_id: str) -> MigrationRollbackReport: ...
```

### Implementation Hides

- Source file parsing.
- Validation.
- Deduplication.
- Mapping.
- Batch tagging.
- Error reporting.
- Reconciliation output.

## 35.2 Migration Rules

- All migrated records tagged with batch ID.
- Sensitive files handled securely.
- No production migration without dry run.
- Financial balances reconciled.
- Historical exceptions recorded.
- Audit record created for migration batch.

---

# 36. Package Dependency Rules

## 36.1 Backend Dependency Direction

Recommended dependency direction:

```text
api/views
  -> modules
    -> selectors/models
    -> shared
    -> adapters where needed
```

Avoid:

```text
models -> views
models -> api serializers
modules -> views
shared -> business apps
```

## 36.2 App Dependency Guidelines

| App | May Depend On |
|---|---|
| `accounts` | shared |
| `rbac` | accounts, shared |
| `audit` | accounts, shared |
| `documents` | accounts, rbac, audit, shared |
| `members` | documents, audit, shared |
| `kyc` | members, documents, audit, shared |
| `applications` | members, kyc, documents, audit, shared |
| `credit` | applications, members, kyc, configurations, audit |
| `approvals` | credit, applications, rbac, audit |
| `legal_documents` | approvals, applications, documents, security, audit |
| `security_instruments` | members, applications, documents, audit |
| `sap_workflow` | applications, members, documents, integrations, audit |
| `loans` | approvals, applications, audit |
| `disbursements` | loans, legal_documents, security_instruments, sap_workflow, integrations, audit |
| `repayments` | loans, integrations, audit |
| `interest` | loans, repayments, configurations, audit |
| `monitoring` | loans, repayments, interest, communications, audit |
| `defaults` | loans, monitoring, communications, audit |
| `recovery` | defaults, security_instruments, approvals, documents, audit |
| `closure` | loans, security_instruments, documents, audit |
| `compliance` | loans, members, documents, audit |
| `reports` | all read-only selectors; audit for export |
| `operations` | shared, audit, integrations |

If circular dependencies appear, the seam is probably in the wrong place.

---

# 37. Database Access Design

## 37.1 Avoid Over-Abstracting Django ORM

Django ORM can be used directly inside modules and selectors.

Do not create repository interfaces for every model unless:

- There are multiple persistence adapters.
- Tests cannot use a test database.
- The module is intended to be persistence-agnostic.
- It improves depth rather than adding indirection.

## 37.2 Use Selectors for Query Complexity

Selectors are useful when:

- Multiple views/reports need the same filtered data.
- Query optimisation matters.
- Object access scoping is repeated.
- Reports need consistent definitions.

## 37.3 Use `select_for_update` in Financial Workflows

Required for:

- Disbursement success.
- Repayment allocation.
- Interest capitalisation.
- Loan closure.
- Recovery action that changes balance.
- Any operation that updates outstanding amount.

---

# 38. Configuration Design

## 38.1 Versioned Configuration Module

### Module Name

`configurations.modules.configuration_resolver`

### Interface

```python
class ConfigurationResolver:
    def get_active_loan_policy(self, *, as_of_date) -> LoanPolicyConfig: ...
    def get_share_valuation(self, *, as_of_date) -> ShareValuationConfig: ...
    def get_scale_of_finance(self, *, crop_id, as_of_date) -> ScaleOfFinanceConfig: ...
    def get_interest_rate(self, *, loan_account_id, as_of_date) -> InterestRateConfig: ...
```

### Implementation Hides

- Effective dates.
- Board approval references.
- Historical versions.
- Active/inactive config.
- Open policy warnings.

## 38.2 Config Snapshot Rule

Any calculation or decision that depends on configuration must store the config version used.

Applies to:

- Loan limit.
- Approval matrix.
- Interest invoice.
- Accrual.
- Capitalisation.
- DPD bucket definitions.
- Compliance calculations.
- Document templates.

---

# 39. Security Codebase Design

## 39.1 No Sensitive Logic in Many Places

Central modules:

| Concern | Module |
|---|---|
| Masking | `shared.masking` |
| Sensitive reveal | `documents.modules.sensitive_data_access` |
| Document permission | `documents.modules.document_access` |
| Field encryption | `shared.encryption` |
| Audit redaction | `audit.modules.audit_redactor` |
| Export masking | `reports.modules.report_export` |
| SMS safe variables | `communications.modules.template_validator` |

## 39.2 Encryption Module

### Module Name

`shared.encryption`

### Interface

```python
class FieldEncryption:
    def encrypt(self, field_name: str, value: str) -> EncryptedValue: ...
    def decrypt(self, field_name: str, encrypted_value: EncryptedValue) -> str: ...
    def hash_for_lookup(self, field_name: str, value: str) -> str: ...
```

### Implementation Hides

- Key version.
- HMAC/hash.
- Encryption provider.
- Rotation support.

---

# 40. Communications Module Design

## 40.1 Communications Module

### Module Name

`communications.modules.communication_dispatcher`

### Interface

```python
class CommunicationDispatcher:
    def create_from_template(self, *, actor, template_code, recipient, context, related_entity) -> Communication: ...
    def send(self, *, communication_id, idempotency_key: str) -> Communication: ...
    def retry_failed(self, *, actor=None) -> CommunicationRetryRun: ...
```

### Implementation Hides

- Template lookup.
- Variable validation.
- Sensitive variable blocking.
- Channel selection.
- Email/SMS adapter.
- Attachments.
- Delivery status.
- Audit.

## 40.2 Template Validation Module

Ensures:

- SMS does not include PAN, Aadhaar, full bank or cheque values.
- Required variables are present.
- Template version is active.
- Attachments exist.
- Recipient contact is valid.

---

# 41. Example Vertical Slice

## 41.1 Slice: Submit Appraisal to Sanction Committee

### Backend Flow

```text
DRF View
  -> AppraisalWorkflow.submit_to_sanction
    -> PermissionEngine.require_permission
    -> ObjectAccess.require_application_access
    -> WorkflowGuard.require_state
    -> AppraisalWorkflow.require_reviewed
    -> EligibilityAssessment.require_pass_or_exception
    -> LoanLimitCalculator.require_current_snapshot
    -> ApprovalCaseEngine.create_for_application
    -> AuditRecorder.record
    -> CommunicationDispatcher.create approval notifications
```

### Frontend Flow

```text
CreditManagerReviewPage
  -> loads application detail
  -> displays available_actions
  -> user clicks Submit to Sanction Committee
  -> POST endpoint
  -> success toast
  -> navigate to approval case
```

### Tests

- Submit without Credit Manager permission -> 403.
- Submit before appraisal review -> 409.
- Submit ineligible application -> 409.
- Submit eligible application -> approval case created.
- Approval case approvers match threshold.
- Audit event created.
- Notification queued.

---

# 42. Code Review Checklist

## 42.1 Module Design Review

Ask:

- What is the module?
- What is its interface?
- What does the implementation hide?
- Where is the seam?
- Is an adapter justified?
- Is the module deep or shallow?
- Does the interface create leverage?
- Does the design improve locality?
- Is the interface testable?
- Are tests crossing the same seam as callers?
- Are we introducing a seam with only one adapter?
- Are workflow rules centralised?
- Are permissions backend-enforced?
- Are audit events included?
- Are sensitive values protected?
- Is idempotency needed?

## 42.2 Backend Review

Check:

- Views are thin.
- Serializers do not contain deep business logic.
- Modules own workflow transitions.
- Transactions wrap critical operations.
- Idempotency exists for duplicate-risk operations.
- Selectors handle complex read queries.
- Sensitive data is masked.
- Errors use standard codes.
- Audit logs are written.
- Tests cover success and blocked paths.

## 42.3 Frontend Review

Check:

- Pages do not implement business rules.
- Available actions come from backend.
- Sensitive values are not persisted.
- Errors show blocker details.
- Forms use backend validation messages.
- Role guard is UX-only.
- Accessibility is considered.
- API wrapper handles auth errors.
- Feature modules are cohesive.

## 42.4 Integration Review

Check:

- External provider is behind adapter seam.
- Manual adapter exists for MVP where applicable.
- Fake adapter exists for tests.
- Raw sensitive payloads are not logged.
- Retry policy is safe.
- Money movement is not blindly retried.
- Provider status is stored as integration events.
- Manual evidence can satisfy workflow gate.

---

# 43. Implementation Order by Module Depth

Build deep modules early enough that screens do not hardcode business logic.

| Build Early | Reason |
|---|---|
| Permission Engine | Every screen/API needs it |
| Audit Recorder | Critical actions must be logged from first workflow |
| Document Storage | KYC and legal docs depend on it |
| Configuration Resolver | Calculators and workflows need versioned config |
| Loan Application Lifecycle | Origination state foundation |
| Eligibility Assessment | Credit workflow foundation |
| Loan Limit Calculator | Approval/disbursement depends on it |
| Approval Case Engine | Governance foundation |
| Document Checklist | Disbursement gate depends on it |
| Security Package | Disbursement and recovery depend on it |
| Disbursement Readiness | Prevents financial bypass |
| Repayment Allocator | Loan ledger correctness |
| Interest Engine | Accounting correctness |
| Default/Recovery Workflow | Legal risk controls |
| Closure Module | End-of-lifecycle integrity |

---

# 44. Open Codebase Design Questions

## 44.1 Architecture Questions

1. Should the production deployment use one Django project with modular apps, or should any module be split into a separate service later?
2. Should the borrower portal, if added, live in the same React app or separate app?
3. Should the audit log be stored in the same PostgreSQL database or an append-only external store later?
4. Should document generation use HTML-to-PDF, DOCX-to-PDF or a dedicated document engine?
5. Should report exports use the primary database or a read replica when volume grows?

## 44.2 Policy Questions Affecting Code

1. Which loan limit rule is authoritative: 30%, 10% or ₹200/share?
2. Which role is final legal document signer?
3. Which annexure label is authoritative for Credit Sanction Register vs Grievance?
4. What is the final interest benchmark/spread/reset rule?
5. What are penal interest and fee rules?
6. Who owns SAP repayment posting?
7. What approval authority is required for recovery invocation?
8. Is full Aadhaar reveal allowed?
9. Is MFA mandatory for privileged users?
10. Is borrower portal included in MVP?

## 44.3 Integration Questions

1. Will SAP be manual, file-based or API-based for MVP?
2. Will bank disbursement remain manual through RBL portal?
3. Which object storage/DMS provider will be used?
4. Which email and SMS providers will be used?
5. Will CDSL/DP expose an API?
6. Will CKYC, bureau or e-sign be in MVP?

---

# 45. Final Codebase Design Summary

The SFPCL platform should be implemented as a modular Django + React monorepo, but the most important design unit is the **module**, not the folder.

The deepest modules should own the most important SOP behaviour:

- Eligibility Assessment.
- Loan Limit Calculator.
- Approval Case Engine.
- Document Checklist.
- Security Package.
- Disbursement Readiness.
- Disbursement Workflow.
- Repayment Allocator.
- Interest Engine.
- Default and Recovery Workflow.
- Closure Module.
- Compliance Calculators.
- Permission and Audit modules.

The most important codebase rule is:

```text
Do not let SOP complexity leak into views, serializers, React pages, reports or integrations. Put the complexity behind small, explicit module interfaces at clean seams, test through those interfaces, and use adapters only where behaviour truly varies.
```

This design gives:

- **Leverage** for callers: simple interfaces for complex workflows.
- **Locality** for maintainers: policy and workflow changes happen in one place.
- **Testability** for QA and engineering: tests exercise the same seam as production callers.
- **Auditability** for compliance: critical actions are consistently logged.
- **Extensibility** for future integrations: manual MVP adapters can be replaced with SAP, bank, CKYC, bureau, e-sign or CDSL API adapters without rewriting the domain workflow.

The platform should begin manual-first and control-first, then deepen and automate the highest-value seams after the internal workflow has proven reliable in production.
