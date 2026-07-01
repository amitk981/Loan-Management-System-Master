# API Contracts — SFPCL Member Credit Administration & Loan Disbursement Platform

## 1. Document Control

| Field | Value |
|---|---|
| Document name | `api-contracts.md` |
| Product / system | SFPCL Member Credit Administration & Loan Disbursement Platform |
| Client | Sahyadri Farmers Producer Company Limited |
| Backend stack | Python + Django + Django REST Framework |
| Frontend stack | React |
| Database | PostgreSQL |
| Authentication | JWT |
| API style | REST over HTTPS with JSON payloads |
| Source basis | Current analysis set: SOP review, client brief, user flows, functional specification, information architecture, screen specification, content specification, component specification, design system, domain model, data model and technical architecture |
| Intended audience | Backend engineers, frontend engineers, QA, API consumers, solution architects, implementation teams and product owners |
| Status | Draft for implementation planning |

---

## 2. Purpose

This document defines the detailed API contracts for the SFPCL Member Credit Administration & Loan Disbursement Platform.

It describes:

- API conventions.
- Authentication and JWT handling.
- Standard request / response envelopes.
- Error structure.
- Pagination, filtering and sorting.
- Idempotency and audit headers.
- Role-based access expectations.
- Common data types and enums.
- Resource groups.
- Endpoint contracts.
- Request and response payloads.
- Workflow action endpoints.
- File and document handling.
- Integration-adjacent API contracts.
- Reporting and export endpoints.
- Compliance and audit endpoints.
- Frontend integration notes.

The API contracts reflect the complete SFPCL loan lifecycle:

1. Member master and eligibility.
2. Loan application intake.
3. KYC and document collection.
4. Credit assessment and appraisal.
5. Loan limit calculation.
6. Sanction Committee approval.
7. Documentation and stamping.
8. Security package creation.
9. SAP customer code workflow.
10. Disbursement.
11. Repayment and interest.
12. Monitoring and DPD.
13. Default and recovery.
14. Closure and NOC.
15. Compliance and audit.

---

## 3. API Design Principles

| Principle | Contract Requirement |
|---|---|
| Backend-enforced workflow | The API must reject invalid state transitions even if the frontend hides unavailable actions. |
| Compliance-first | All sensitive actions must capture actor, timestamp, reason, status and audit event. |
| Explicit action endpoints | Workflow transitions must use dedicated action endpoints, not generic PATCH alone. |
| Immutable approvals | Approval actions must be append-only and cannot be edited after submission. |
| Snapshot decisions | Loan limits, sanction terms, borrower details and approval matrix must be snapshotted at decision time. |
| Idempotent financial actions | Disbursement, repayment allocation, interest accrual and capitalisation must prevent duplicates. |
| Permission-aware responses | APIs may return action availability and field-level masking based on user role. |
| Secure by default | Sensitive values such as PAN, Aadhaar, bank account and cheque details must be masked unless specifically authorised. |
| Observable | Each request should have a request ID, audit log and standard error format. |
| Versioned | API changes must be versioned under `/api/v1/`. |

---

## 4. Base URL and Versioning

## 4.1 Base URL

```http
https://<host>/api/v1
```

Examples:

```http
GET /api/v1/loan-applications/
GET /api/v1/loan-applications/{loan_application_id}/
POST /api/v1/approval-cases/{approval_case_id}/approve/
```

## 4.2 Versioning Rules

| Rule | Description |
|---|---|
| Current version | `/api/v1/` |
| Backward-compatible additions | Allowed within same version |
| Breaking changes | Require new version path |
| Deprecated endpoints | Must include deprecation metadata and migration guidance |
| OpenAPI schema | Should be exposed at `/api/v1/schema/` and Swagger UI at `/api/v1/docs/` |

---

## 5. HTTP Conventions

## 5.1 Methods

| Method | Usage |
|---|---|
| `GET` | Read resources |
| `POST` | Create resources or trigger actions |
| `PATCH` | Partial update of editable fields |
| `PUT` | Full replace, rarely used |
| `DELETE` | Soft delete where permitted |
| `OPTIONS` | Metadata / available actions if supported |

## 5.2 Content Types

| Payload | Content-Type |
|---|---|
| JSON API requests | `application/json` |
| File upload | `multipart/form-data` |
| File download | Native MIME type or signed URL |
| Export response | `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/pdf` |

## 5.3 Standard Headers

| Header | Required | Description |
|---|---:|---|
| `Authorization: Bearer <access_token>` | Yes for protected APIs | JWT access token |
| `Content-Type: application/json` | Yes for JSON write requests | Payload type |
| `X-Request-ID` | Recommended | Client-generated trace ID |
| `Idempotency-Key` | Required for critical POSTs | Prevent duplicate financial or workflow actions |
| `Accept-Language` | Optional | Future localisation |
| `X-Timezone` | Optional | Client timezone for display |
| `X-Client-Version` | Optional | Frontend app version |

---

## 6. Standard Response Envelopes

## 6.1 Success Envelope

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_01HZX9YV",
    "timestamp": "2026-06-22T10:30:00Z",
    "api_version": "v1"
  }
}
```

## 6.2 List Envelope

```json
{
  "success": true,
  "data": [
    {}
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 126,
    "total_pages": 7,
    "has_next": true,
    "has_previous": false
  },
  "meta": {
    "request_id": "req_01HZX9YV",
    "timestamp": "2026-06-22T10:30:00Z"
  }
}
```

## 6.3 Action Response Envelope

Workflow action endpoints should return:

```json
{
  "success": true,
  "data": {
    "entity_type": "loan_application",
    "entity_id": "uuid",
    "previous_status": "appraisal_reviewed",
    "new_status": "submitted_to_sanction_committee",
    "workflow_event_id": "uuid",
    "available_actions": []
  },
  "meta": {
    "request_id": "req_01HZX9YV",
    "timestamp": "2026-06-22T10:30:00Z"
  }
}
```

## 6.4 Error Envelope

```json
{
  "success": false,
  "error": {
    "code": "LOAN_LIMIT_EXCEEDED",
    "message": "Requested amount exceeds the final eligible loan amount.",
    "details": {
      "requested_amount": "600000.00",
      "final_eligible_loan_amount": "500000.00",
      "exception_required": true
    },
    "field_errors": {}
  },
  "meta": {
    "request_id": "req_01HZX9YV",
    "timestamp": "2026-06-22T10:30:00Z"
  }
}
```

---

## 7. Standard Error Codes

## 7.1 Authentication and Permission Errors

| Code | HTTP | Meaning |
|---|---:|---|
| `AUTH_REQUIRED` | 401 | Missing access token |
| `TOKEN_EXPIRED` | 401 | Access token expired |
| `INVALID_TOKEN` | 401 | Token invalid or revoked |
| `REFRESH_TOKEN_EXPIRED` | 401 | Refresh token expired |
| `FORBIDDEN` | 403 | User lacks permission |
| `OBJECT_ACCESS_DENIED` | 403 | User cannot access this specific object |
| `SENSITIVE_FIELD_ACCESS_DENIED` | 403 | User cannot view full sensitive data |
| `APPROVAL_AUTHORITY_REQUIRED` | 403 | User is not an eligible approver |

## 7.2 Validation Errors

| Code | HTTP | Meaning |
|---|---:|---|
| `VALIDATION_ERROR` | 400 | General validation error |
| `MISSING_REQUIRED_FIELD` | 400 | Required field missing |
| `INVALID_ENUM_VALUE` | 400 | Invalid status / type |
| `INVALID_AMOUNT` | 400 | Amount must be positive / valid |
| `INVALID_DATE_RANGE` | 400 | Date range invalid |
| `INVALID_PAN_FORMAT` | 400 | PAN format invalid |
| `INVALID_AADHAAR_FORMAT` | 400 | Aadhaar format invalid |
| `NOMINEE_MINOR_NOT_ALLOWED` | 400 | Nominee is minor |
| `WITNESS_NOT_SHAREHOLDER` | 400 | Witness is not existing shareholder |
| `DOCUMENT_REQUIRED` | 400 | Required document missing |
| `SIGNATURE_MISMATCH_UNRESOLVED` | 400 | Bank verification / declaration required |

## 7.3 Workflow Errors

| Code | HTTP | Meaning |
|---|---:|---|
| `INVALID_STATE_TRANSITION` | 409 | Requested transition not allowed |
| `APPLICATION_INCOMPLETE` | 409 | Application cannot move forward |
| `APPRAISAL_NOT_REVIEWED` | 409 | Credit Manager review missing |
| `APPROVAL_PENDING` | 409 | Required approvals incomplete |
| `DOCUMENTATION_INCOMPLETE` | 409 | Checklist or required documents incomplete |
| `SECURITY_PACKAGE_INCOMPLETE` | 409 | Security records incomplete |
| `SAP_CUSTOMER_CODE_REQUIRED` | 409 | SAP code missing |
| `BANK_ACCOUNT_NOT_VERIFIED` | 409 | Beneficiary account not verified |
| `CFC_AUTHORISATION_REQUIRED` | 409 | CFC approval missing |
| `LOAN_ALREADY_DISBURSED` | 409 | Duplicate disbursement attempt |
| `LOAN_NOT_ACTIVE` | 409 | Loan action requires active loan |
| `LOAN_NOT_FULLY_REPAID` | 409 | Closure not allowed |
| `RECOVERY_APPROVAL_REQUIRED` | 409 | Security invocation needs approval |

## 7.4 Financial Errors

| Code | HTTP | Meaning |
|---|---:|---|
| `LOAN_LIMIT_EXCEEDED` | 409 | Requested amount exceeds limit |
| `DISBURSEMENT_EXCEEDS_SANCTION` | 409 | Disbursement amount exceeds sanctioned amount |
| `DUPLICATE_BANK_REFERENCE` | 409 | Bank reference already used |
| `REPAYMENT_ALLOCATION_FAILED` | 409 | Allocation rule failed |
| `DUPLICATE_ACCRUAL` | 409 | Accrual already exists for month |
| `DUPLICATE_CAPITALISATION` | 409 | Interest already capitalised for year |

## 7.5 System Errors

| Code | HTTP | Meaning |
|---|---:|---|
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Data conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `INTEGRATION_UNAVAILABLE` | 503 | External system unavailable |
| `FILE_STORAGE_ERROR` | 503 | File service failed |

---

# 8. Pagination, Filtering, Sorting and Search

## 8.1 Pagination

Default:

```http
GET /api/v1/loan-applications/?page=1&page_size=20
```

Rules:

| Parameter | Type | Default | Max |
|---|---:|---:|---:|
| `page` | integer | 1 | N/A |
| `page_size` | integer | 20 | 100 |

## 8.2 Sorting

```http
GET /api/v1/loan-applications/?ordering=-application_date
GET /api/v1/loan-accounts/?ordering=repayment_date
```

Use comma-separated fields where supported:

```http
GET /api/v1/loan-applications/?ordering=current_stage,-application_date
```

## 8.3 Filtering

Example:

```http
GET /api/v1/loan-applications/?status=submitted&current_stage=appraisal&member_id=uuid
```

Common filters:

| Filter | Applies To |
|---|---|
| `status` | Most resources |
| `created_from`, `created_to` | Most resources |
| `member_id` | Member-related resources |
| `loan_application_id` | Application-related resources |
| `loan_account_id` | Loan-related resources |
| `assigned_to_user_id` | Task / workflow resources |
| `financial_year` | Reports, interest, compliance |
| `quarter` | MIS and compliance trackers |
| `document_type` | Documents |
| `approval_type` | Approvals |

## 8.4 Search

```http
GET /api/v1/members/?search=Ramesh
GET /api/v1/loan-applications/?search=LO00000025
```

Searchable fields should include:

- Member name.
- Member number.
- Folio number.
- Application reference number.
- Loan account number.
- SAP customer code.
- Bank reference number.
- Document name.
- Grievance reference.

Sensitive values such as full PAN, Aadhaar and bank account should not be directly searchable unless using hashed exact lookup in authorised workflows.

---

# 9. Common Data Types

## 9.1 UUID

```json
"78e99841-ae9c-4518-86f8-bac77c8b70b1"
```

## 9.2 Money

All money values should be serialized as strings to avoid floating point errors:

```json
"500000.00"
```

## 9.3 Percentage

Use decimal string:

```json
"12.5000"
```

## 9.4 Date

```json
"2026-06-22"
```

## 9.5 Timestamp

```json
"2026-06-22T10:30:00Z"
```

## 9.6 Masked Sensitive Value

```json
{
  "masked": "ABCDE****F",
  "last4": "1234",
  "can_view_full": false
}
```

---

# 10. Common DTOs

## 10.1 `AuditMeta`

```json
{
  "created_at": "2026-06-22T10:30:00Z",
  "created_by": {
    "user_id": "uuid",
    "full_name": "Credit Manager"
  },
  "updated_at": "2026-06-22T11:30:00Z",
  "updated_by": {
    "user_id": "uuid",
    "full_name": "Company Secretary"
  }
}
```

## 10.2 `AvailableAction`

```json
{
  "action_code": "submit_to_sanction_committee",
  "label": "Submit to Sanction Committee",
  "enabled": true,
  "disabled_reason": null,
  "required_permission": "loan_application.submit_to_sanction"
}
```

## 10.3 `UserSummary`

```json
{
  "user_id": "uuid",
  "full_name": "A. User",
  "email": "user@example.com",
  "role_codes": ["credit_manager"],
  "team_codes": ["credit_assessment"]
}
```

## 10.4 `DocumentSummary`

```json
{
  "loan_document_id": "uuid",
  "document_type": "loan_agreement",
  "document_category": "legal",
  "file_name": "loan-agreement-LO00000025.pdf",
  "generation_status": "generated",
  "execution_status": "signed",
  "verification_status": "verified",
  "stamp_status": "adequate",
  "notarisation_status": "completed"
}
```

## 10.5 `WorkflowEventSummary`

```json
{
  "workflow_event_id": "uuid",
  "workflow_name": "loan_application",
  "from_state": "appraisal_reviewed",
  "to_state": "submitted_to_sanction_committee",
  "triggered_by": {
    "user_id": "uuid",
    "full_name": "Credit Manager"
  },
  "trigger_reason": "Appraisal reviewed and ready for sanction",
  "created_at": "2026-06-22T10:30:00Z"
}
```

---

# 11. Authentication API

## 11.1 Login

```http
POST /api/v1/auth/login/
```

### Request

```json
{
  "email": "credit.manager@sfpcl.example",
  "password": "********"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
      "user_id": "uuid",
      "full_name": "Credit Manager",
      "email": "credit.manager@sfpcl.example",
      "role_codes": ["credit_manager"],
      "team_codes": ["credit_assessment"],
      "permissions": [
        "loan_application.read",
        "loan_application.create",
        "appraisal.review"
      ]
    }
  }
}
```

## 11.2 Refresh Token

```http
POST /api/v1/auth/refresh/
```

### Request

```json
{
  "refresh_token": "jwt-refresh-token"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "access_token": "new-jwt-access-token",
    "expires_in": 1800
  }
}
```

## 11.3 Logout

```http
POST /api/v1/auth/logout/
```

### Request

```json
{
  "refresh_token": "jwt-refresh-token"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully."
  }
}
```

## 11.4 Current User

```http
GET /api/v1/auth/me/
```

### Response

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "full_name": "Credit Manager",
    "email": "credit.manager@sfpcl.example",
    "mobile_number": "+919999999999",
    "status": "active",
    "roles": [
      {
        "role_code": "credit_manager",
        "role_name": "Credit Manager"
      }
    ],
    "teams": [
      {
        "team_code": "credit_assessment",
        "team_name": "Credit Assessment Team"
      }
    ],
    "permissions": [
      "loan_application.read",
      "loan_application.create",
      "appraisal.review"
    ]
  }
}
```

---

# 12. User, Role and Team APIs

## 12.1 List Users

```http
GET /api/v1/users/?search=&role_code=&status=&page=1&page_size=20
```

### Response Item

```json
{
  "user_id": "uuid",
  "full_name": "Company Secretary",
  "email": "cs@sfpcl.example",
  "mobile_number": "+919999999999",
  "status": "active",
  "primary_role": {
    "role_code": "company_secretary",
    "role_name": "Company Secretary"
  },
  "approval_authority_type": "company_secretary"
}
```

## 12.2 Create User

```http
POST /api/v1/users/
```

### Request

```json
{
  "full_name": "Senior Manager Finance",
  "email": "senior.finance@sfpcl.example",
  "mobile_number": "+919999999999",
  "primary_role_id": "uuid",
  "team_ids": ["uuid"],
  "approval_authority_type": "senior_manager_finance",
  "status": "active"
}
```

## 12.3 Update User

```http
PATCH /api/v1/users/{user_id}/
```

### Request

```json
{
  "status": "inactive",
  "team_ids": ["uuid"]
}
```

## 12.4 Roles

```http
GET /api/v1/roles/
GET /api/v1/roles/{role_id}/
POST /api/v1/roles/
PATCH /api/v1/roles/{role_id}/
```

## 12.5 Permissions

```http
GET /api/v1/permissions/
GET /api/v1/roles/{role_id}/permissions/
POST /api/v1/roles/{role_id}/permissions/
```

## 12.6 Teams

```http
GET /api/v1/teams/
GET /api/v1/teams/{team_id}/
POST /api/v1/teams/
PATCH /api/v1/teams/{team_id}/
```

---

# 13. Member APIs

## 13.1 List Members

```http
GET /api/v1/members/?search=&member_type=&membership_status=&kyc_status=&default_status=&page=1&page_size=20
```

### Response Item

```json
{
  "member_id": "uuid",
  "member_number": "MEM-00125",
  "member_type": "individual_farmer",
  "legal_name": "Ramesh Patil",
  "display_name": "Ramesh Patil",
  "folio_number": "FOL-456",
  "membership_status": "active",
  "kyc_status": "verified",
  "rekyc_due_date": "2027-06-22",
  "default_status": "no_default",
  "mobile_number": "******7890",
  "email": "ramesh@example.com",
  "share_summary": {
    "number_of_shares": 100,
    "holding_mode": "physical",
    "available_share_count": 100
  },
  "active_member_status": {
    "status": "active",
    "verified_at": "2026-06-22T10:30:00Z"
  }
}
```

## 13.2 Create Member

```http
POST /api/v1/members/
```

### Request: Individual Farmer

```json
{
  "member_type": "individual_farmer",
  "legal_name": "Ramesh Patil",
  "display_name": "Ramesh Patil",
  "folio_number": "FOL-456",
  "membership_start_date": "2022-04-01",
  "pan": "ABCDE1234F",
  "aadhaar": "123412341234",
  "registered_address": {
    "line1": "Village Road",
    "line2": "Near Market",
    "village_city": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "pincode": "422001"
  },
  "mobile_number": "+919999999999",
  "email": "ramesh@example.com",
  "individual_profile": {
    "first_name": "Ramesh",
    "middle_name": null,
    "last_name": "Patil",
    "gender": "male",
    "date_of_birth": "1980-01-15",
    "occupation": "Farmer",
    "land_area_under_cultivation_acres": "5.00",
    "primary_crop": "grapes",
    "services_availed_flag": true,
    "employment_or_service_years": null
  }
}
```

### Request: FPC / Producer Institution

```json
{
  "member_type": "fpc",
  "legal_name": "ABC Farmer Producer Company Limited",
  "display_name": "ABC FPC",
  "folio_number": "FOL-789",
  "membership_start_date": "2021-04-01",
  "pan": "ABCDE1234F",
  "registered_address": {
    "line1": "Registered Office",
    "village_city": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "pincode": "422001"
  },
  "mobile_number": "+919999999999",
  "email": "office@abcfpc.example",
  "producer_institution_profile": {
    "institution_type": "farmer_producer_company",
    "registration_number": "U00000MH2021PTC000000",
    "authorised_signatory_name": "Authorised Person",
    "authorised_signatory_pan": "ABCDE1234F",
    "authorised_signatory_aadhaar": "123412341234",
    "board_resolution_required_flag": true,
    "services_availed_flag": true,
    "produce_supply_years": "2.00"
  }
}
```

## 13.3 Retrieve Member

```http
GET /api/v1/members/{member_id}/
```

### Response

```json
{
  "success": true,
  "data": {
    "member_id": "uuid",
    "member_number": "MEM-00125",
    "member_type": "individual_farmer",
    "legal_name": "Ramesh Patil",
    "folio_number": "FOL-456",
    "membership_status": "active",
    "pan": {
      "masked": "ABCDE****F",
      "can_view_full": false
    },
    "aadhaar": {
      "masked": "********1234",
      "can_view_full": false
    },
    "registered_address": {
      "line1": "Village Road",
      "village_city": "Nashik",
      "district": "Nashik",
      "state": "Maharashtra",
      "pincode": "422001"
    },
    "kyc_status": "verified",
    "default_status": "no_default",
    "individual_profile": {
      "land_area_under_cultivation_acres": "5.00",
      "primary_crop": "grapes",
      "services_availed_flag": true
    },
    "available_actions": [
      {
        "action_code": "create_loan_application",
        "enabled": true,
        "disabled_reason": null
      }
    ]
  }
}
```

## 13.4 Update Member

```http
PATCH /api/v1/members/{member_id}/
```

### Request

```json
{
  "mobile_number": "+919888888888",
  "email": "updated@example.com",
  "registered_address": {
    "line1": "Updated Address",
    "village_city": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "pincode": "422001"
  }
}
```

## 13.5 View Full Sensitive Field

```http
POST /api/v1/members/{member_id}/reveal-sensitive-field/
```

### Request

```json
{
  "field_name": "aadhaar",
  "reason": "KYC verification during loan application"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "field_name": "aadhaar",
    "value": "123412341234",
    "expires_at": "2026-06-22T10:35:00Z"
  }
}
```

### Notes

- Requires sensitive-data permission.
- Must write audit log.
- Frontend should not cache the full value.

---

# 14. Nominee APIs

## 14.1 List Nominees for Member

```http
GET /api/v1/members/{member_id}/nominees/
```

## 14.2 Create Nominee

```http
POST /api/v1/members/{member_id}/nominees/
```

### Request

```json
{
  "nominee_name": "Sita Patil",
  "date_of_birth": "1985-05-20",
  "gender": "female",
  "relationship_to_borrower": "Spouse",
  "pan": "ABCDE1234F",
  "aadhaar": "123412341234",
  "signature_required_flag": true
}
```

### Response

```json
{
  "success": true,
  "data": {
    "nominee_id": "uuid",
    "nominee_name": "Sita Patil",
    "age_at_application": 41,
    "minor_flag": false,
    "kyc_status": "pending"
  }
}
```

## 14.3 Validation Rules

| Rule | Error |
|---|---|
| Nominee age below legal majority | `NOMINEE_MINOR_NOT_ALLOWED` |
| PAN missing | `MISSING_REQUIRED_FIELD` |
| Aadhaar missing | `MISSING_REQUIRED_FIELD` |
| Invalid PAN | `INVALID_PAN_FORMAT` |
| Invalid Aadhaar | `INVALID_AADHAAR_FORMAT` |

---

# 15. Shareholding APIs

## 15.1 List Shareholdings

```http
GET /api/v1/members/{member_id}/shareholdings/
```

### Response Item

```json
{
  "shareholding_id": "uuid",
  "folio_number": "FOL-456",
  "number_of_shares": 100,
  "holding_mode": "physical",
  "valuation_per_share": "2000.00",
  "valuation_effective_date": "2026-04-01",
  "pledged_share_count": 0,
  "available_share_count": 100,
  "future_shares_pledge_flag": false
}
```

## 15.2 Create / Update Shareholding

```http
POST /api/v1/members/{member_id}/shareholdings/
PATCH /api/v1/shareholdings/{shareholding_id}/
```

### Request

```json
{
  "folio_number": "FOL-456",
  "number_of_shares": 100,
  "holding_mode": "physical",
  "share_certificate_ids": ["uuid"],
  "future_shares_pledge_flag": false
}
```

---

# 16. Active Member Status APIs

## 16.1 Calculate Active Member Status

```http
POST /api/v1/members/{member_id}/active-status/calculate/
```

### Request

```json
{
  "as_of_date": "2026-06-22"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "active_member_status_id": "uuid",
    "status": "active",
    "member_type": "individual_farmer",
    "services_availed_flag": true,
    "continuous_supply_years": "4.00",
    "supplied_to_company_flag": true,
    "supplied_to_subsidiary_flag": true,
    "supplied_to_stepdown_flag": false,
    "supplied_through_producer_institution_flag": false,
    "employment_service_years": null,
    "relaxation_reason": null,
    "eligible_for_loan": true,
    "rule_explanation": "Member availed services and supplied primary produce continuously for four financial years."
  }
}
```

## 16.2 Manually Verify Active Status

```http
POST /api/v1/members/{member_id}/active-status/verify/
```

### Request

```json
{
  "status": "eligible_under_relaxation",
  "services_availed_flag": true,
  "continuous_supply_years": "1.00",
  "relaxation_reason": "New member supplied produce for at least one year.",
  "evidence_document_ids": ["uuid"]
}
```

---

# 17. Land Holding and Crop Plan APIs

## 17.1 Land Holdings

```http
GET /api/v1/members/{member_id}/land-holdings/
POST /api/v1/members/{member_id}/land-holdings/
GET /api/v1/land-holdings/{land_holding_id}/
PATCH /api/v1/land-holdings/{land_holding_id}/
```

### Create Request

```json
{
  "document_type": "7_12_extract",
  "survey_number": "123/4",
  "village": "Village Name",
  "taluka": "Taluka",
  "district": "Nashik",
  "state": "Maharashtra",
  "area_acres": "5.00",
  "document_id": "uuid"
}
```

## 17.2 Crop Plans

```http
GET /api/v1/members/{member_id}/crop-plans/
POST /api/v1/members/{member_id}/crop-plans/
GET /api/v1/crop-plans/{crop_plan_id}/
PATCH /api/v1/crop-plans/{crop_plan_id}/
```

### Create Request

```json
{
  "loan_application_id": "uuid",
  "crop_type": "grapes",
  "season": "FY2026 Kharif",
  "planned_area_acres": "5.00",
  "estimated_cost_amount": "100000.00",
  "loan_purpose_alignment": "agriculture_aligned",
  "document_id": "uuid"
}
```

---

# 18. KYC APIs

## 18.1 Get KYC Profile

```http
GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}
```

## 18.2 Create / Update KYC Profile

```http
POST /api/v1/kyc-profiles/
PATCH /api/v1/kyc-profiles/{kyc_profile_id}/
```

### Request

```json
{
  "party_type": "member",
  "party_id": "uuid",
  "ckyc_consent_flag": true,
  "beneficial_ownership_verified_flag": true,
  "risk_rating": "low"
}
```

## 18.3 Upload KYC Document

```http
POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/
Content-Type: multipart/form-data
```

### Multipart Fields

| Field | Required | Description |
|---|---:|---|
| `document_type` | Yes | `pan`, `aadhaar`, `photo`, `ckyc_consent`, etc. |
| `file` | Yes | Uploaded file |
| `self_attested_flag` | Optional | Self-attestation flag |

## 18.4 Verify KYC Document

```http
POST /api/v1/kyc-documents/{kyc_document_id}/verify/
```

### Request

```json
{
  "verification_status": "verified",
  "remarks": "Document verified against original."
}
```

## 18.5 Re-KYC Tasks

```http
GET /api/v1/kyc-reviews/?status=pending&due_before=2026-07-01
POST /api/v1/kyc-reviews/{kyc_review_id}/complete/
```

---

# 19. Loan Application APIs

## 19.1 List Loan Applications

```http
GET /api/v1/loan-applications/?search=&application_status=&current_stage=&member_id=&page=1&page_size=20
```

### Response Item

```json
{
  "loan_application_id": "uuid",
  "application_reference_number": "LO00000025",
  "member": {
    "member_id": "uuid",
    "display_name": "Ramesh Patil",
    "member_type": "individual_farmer",
    "folio_number": "FOL-456"
  },
  "application_date": "2026-06-22",
  "required_loan_amount": "400000.00",
  "purpose_category": "crop_production",
  "current_stage": "credit_assessment",
  "application_status": "appraisal_in_progress",
  "completeness_status": "complete",
  "assigned_owner": {
    "user_id": "uuid",
    "full_name": "Deputy Manager Finance"
  },
  "tat": {
    "due_at": "2026-06-24T10:30:00Z",
    "status": "within_tat"
  }
}
```

## 19.2 Create Loan Application

```http
POST /api/v1/loan-applications/
```

### Request

```json
{
  "member_id": "uuid",
  "application_channel": "assisted_digital",
  "application_date": "2026-06-22",
  "required_loan_amount": "400000.00",
  "declared_purpose": "Crop production loan for grape cultivation",
  "purpose_category": "crop_production",
  "nominee_id": "uuid",
  "loan_type_requested": "short_term",
  "terms_acceptance_flag": true
}
```

### Response

```json
{
  "success": true,
  "data": {
    "loan_application_id": "uuid",
    "application_reference_number": "LO00000025",
    "application_status": "draft",
    "current_stage": "initial_loan_request",
    "loan_request_register_entry_id": "uuid"
  }
}
```

## 19.3 Retrieve Loan Application

```http
GET /api/v1/loan-applications/{loan_application_id}/
```

### Response

```json
{
  "success": true,
  "data": {
    "loan_application_id": "uuid",
    "application_reference_number": "LO00000025",
    "member": {
      "member_id": "uuid",
      "display_name": "Ramesh Patil",
      "member_type": "individual_farmer",
      "folio_number": "FOL-456"
    },
    "required_loan_amount": "400000.00",
    "declared_purpose": "Crop production loan for grape cultivation",
    "purpose_category": "crop_production",
    "nominee": {
      "nominee_id": "uuid",
      "nominee_name": "Sita Patil",
      "minor_flag": false,
      "kyc_status": "verified"
    },
    "application_status": "appraisal_in_progress",
    "current_stage": "credit_assessment",
    "completeness_status": "complete",
    "available_actions": [
      {
        "action_code": "prepare_appraisal_note",
        "enabled": true,
        "disabled_reason": null
      }
    ],
    "summary": {
      "documents_required": 8,
      "documents_submitted": 8,
      "deficiencies_open": 0,
      "eligibility_result": "eligible",
      "final_eligible_loan_amount": "400000.00"
    }
  }
}
```

## 19.4 Update Draft Application

```http
PATCH /api/v1/loan-applications/{loan_application_id}/
```

### Request

```json
{
  "required_loan_amount": "450000.00",
  "declared_purpose": "Updated crop production loan purpose"
}
```

## 19.5 Submit Application

```http
POST /api/v1/loan-applications/{loan_application_id}/submit/
```

### Request

```json
{
  "submission_notes": "Application form signed by applicant and nominee."
}
```

### Gate Conditions

- Member exists.
- Borrower is member.
- Nominee is present and not minor.
- Required amount is positive.
- Purpose is agriculture / crop production.
- Application form uploaded or generated.
- Required KYC document placeholders exist.

## 19.6 Completeness Check

```http
POST /api/v1/loan-applications/{loan_application_id}/complete-check/
```

### Request

```json
{
  "completeness_status": "complete",
  "remarks": "All mandatory application documents submitted."
}
```

### Incomplete Request

```json
{
  "completeness_status": "incomplete",
  "remarks": "Nominee Aadhaar and six-month bank statement missing.",
  "deficiencies": [
    {
      "deficiency_type": "missing_document",
      "description": "Nominee Aadhaar missing"
    },
    {
      "deficiency_type": "missing_document",
      "description": "Six-month bank statement missing"
    }
  ]
}
```

## 19.7 Return Application with Deficiencies

```http
POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/
```

### Request

```json
{
  "communication_mode": "email",
  "deficiency_ids": ["uuid", "uuid"],
  "message": "Please submit the missing documents to proceed."
}
```

## 19.8 Cancel Application

```http
POST /api/v1/loan-applications/{loan_application_id}/cancel/
```

### Request

```json
{
  "reason": "Borrower withdrew application."
}
```

---

# 20. Application Document APIs

## 20.1 List Application Documents

```http
GET /api/v1/loan-applications/{loan_application_id}/application-documents/
```

## 20.2 Upload Application Document

```http
POST /api/v1/loan-applications/{loan_application_id}/application-documents/
Content-Type: multipart/form-data
```

### Multipart Fields

| Field | Required | Description |
|---|---:|---|
| `document_type` | Yes | `borrower_pan`, `nominee_aadhaar`, `land_7_12`, etc. |
| `party_type` | Yes | `borrower`, `nominee`, `witness` |
| `party_id` | Optional | Related party |
| `file` | Yes | Uploaded file |
| `remarks` | Optional | Notes |

## 20.3 Verify Application Document

```http
POST /api/v1/application-documents/{application_document_id}/verify/
```

### Request

```json
{
  "verification_status": "verified",
  "remarks": "Document is complete and legible."
}
```

---

# 21. Deficiency and Rejection APIs

## 21.1 List Deficiencies

```http
GET /api/v1/loan-applications/{loan_application_id}/deficiencies/
```

## 21.2 Resolve Deficiency

```http
POST /api/v1/deficiencies/{deficiency_id}/resolve/
```

### Request

```json
{
  "resolution_notes": "Nominee Aadhaar uploaded and verified."
}
```

## 21.3 Create Rejection Note

```http
POST /api/v1/loan-applications/{loan_application_id}/rejection-note/
```

### Request

```json
{
  "rejection_stage": "credit_assessment",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Borrower is not currently eligible as active member criteria are not met.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

## 21.4 Send Rejection Note

```http
POST /api/v1/rejection-notes/{rejection_note_id}/send/
```

### Request

```json
{
  "recipient_email": "borrower@example.com",
  "message_override": null
}
```

---

# 22. Eligibility Assessment APIs

## 22.1 Run Eligibility Assessment

```http
POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/
```

### Response

```json
{
  "success": true,
  "data": {
    "eligibility_assessment_id": "uuid",
    "member_active_check": "pass",
    "default_check": "no_default",
    "document_check": "complete",
    "terms_acceptance_check": "accepted",
    "purpose_check": "agriculture_aligned",
    "nominee_check": "valid",
    "overall_result": "eligible",
    "assessment_notes": "All mandatory eligibility criteria passed."
  }
}
```

## 22.2 Get Eligibility Assessment

```http
GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/
```

## 22.3 Override Eligibility Assessment

```http
POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/override/
```

### Request

```json
{
  "overall_result": "conditionally_eligible",
  "override_reason": "Eligible under new member relaxation route.",
  "evidence_document_ids": ["uuid"],
  "approval_case_required": true
}
```

### Notes

- Should create an exception approval if policy requires.
- Must write audit log.

---

# 23. Loan Limit APIs

## 23.1 Calculate Loan Limit

```http
POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/
```

### Request

```json
{
  "shareholding_id": "uuid",
  "land_holding_ids": ["uuid"],
  "crop_plan_id": "uuid",
  "requested_amount": "400000.00",
  "calculation_date": "2026-06-22"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "loan_limit_assessment_id": "uuid",
    "number_of_shares": 100,
    "valuation_per_share": "2000.00",
    "share_limit_percentage": "10.0000",
    "per_share_cap_amount": "200.00",
    "shareholding_based_limit_amount": "20000.00",
    "land_area_acres": "25.00",
    "scale_of_finance_per_acre_amount": "20000.00",
    "land_based_limit_amount": "500000.00",
    "final_eligible_loan_amount": "20000.00",
    "requested_amount": "400000.00",
    "amount_within_limit_flag": false,
    "exception_required_flag": true,
    "calculation_rule_version": "loan-policy-v1.0",
    "warnings": [
      {
        "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
        "message": "Requested amount exceeds final eligible loan amount."
      }
    ]
  }
}
```

## 23.2 Formula Contract

```text
shareholding_based_limit = number_of_shares × configured percentage or per-share cap
land_based_limit = scale_of_finance_per_acre × land_area_acres
final_eligible_loan_amount = min(shareholding_based_limit, land_based_limit)
```

## 23.3 Important Configuration Note

The current analysis identified a policy ambiguity around:

- 30% of valuation per share.
- 10% of valuation per share.
- Current result of ₹200 per share.

Therefore, the API must return:

- The exact percentage / cap used.
- The rule version.
- The configuration source.
- Any warnings if configuration is marked `pending_client_confirmation`.

---

# 24. Loan Appraisal APIs

## 24.1 Create Appraisal Note

```http
POST /api/v1/loan-applications/{loan_application_id}/appraisal-note/
```

### Request

```json
{
  "borrower_summary": "Active individual farmer member with verified KYC and crop plan.",
  "eligibility_summary": "All eligibility criteria passed.",
  "loan_limit_summary": "Final eligible amount calculated as lower of shareholding and land-based limits.",
  "recommended_amount": "400000.00",
  "recommended_tenure_months": 12,
  "recommended_interest_type": "floating",
  "recommended_security_summary": "PoA, SH-4 for physical shares, blank-dated cheque and cancelled cheque.",
  "risk_assessment": {
    "market_risk_rating": "medium",
    "operational_risk_rating": "low",
    "borrower_risk_rating": "low",
    "overall_risk_rating": "low",
    "risk_mitigation_notes": "Produce deduction arrangement available through subsidiary."
  },
  "recommendation": "approve"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "loan_appraisal_note_id": "uuid",
    "loan_application_id": "uuid",
    "prepared_by": {
      "user_id": "uuid",
      "full_name": "Deputy Manager Finance"
    },
    "prepared_at": "2026-06-22T10:30:00Z",
    "tat_due_at": "2026-06-24T10:30:00Z",
    "tat_status": "within_tat",
    "appraisal_status": "draft"
  }
}
```

## 24.2 Get Appraisal Note

```http
GET /api/v1/loan-applications/{loan_application_id}/appraisal-note/
```

## 24.3 Submit Appraisal for Review

```http
POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/submit-for-review/
```

### Request

```json
{
  "remarks": "Appraisal completed for Credit Manager review."
}
```

## 24.4 Credit Manager Review

```http
POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/review/
```

### Request

```json
{
  "decision": "reviewed",
  "review_comments": "Reviewed and recommended for Sanction Committee."
}
```

## 24.5 Submit to Sanction Committee

```http
POST /api/v1/loan-applications/{loan_application_id}/submit-to-sanction-committee/
```

### Request

```json
{
  "remarks": "Credit Manager reviewed appraisal and recommends sanction."
}
```

### Gate Conditions

- Eligibility assessment completed.
- Loan limit assessment completed.
- Appraisal note prepared.
- Credit Manager review completed.
- Required documents for appraisal available.
- If amount exceeds limit, exception approval route is created or flagged.

---

# 25. Approval and Sanction APIs

## 25.1 Approval Matrix Rules

```http
GET /api/v1/approval-matrix-rules/
POST /api/v1/approval-matrix-rules/
PATCH /api/v1/approval-matrix-rules/{approval_matrix_rule_id}/
```

### Response Item

```json
{
  "approval_matrix_rule_id": "uuid",
  "decision_type": "loan_sanction",
  "amount_min": "0.00",
  "amount_max": "500000.00",
  "condition_code": null,
  "required_approver_roles": ["cfo", "director"],
  "required_director_count": 1,
  "joint_approval_required_flag": true,
  "register_required": "credit_sanction_register",
  "effective_from": "2026-04-01",
  "status": "active"
}
```

## 25.2 Create Approval Case

```http
POST /api/v1/loan-applications/{loan_application_id}/approval-cases/
```

### Request

```json
{
  "approval_type": "sanction",
  "amount": "400000.00",
  "reason_for_approval": "Loan appraisal recommended approval.",
  "force_exception_route": false
}
```

### Response

```json
{
  "success": true,
  "data": {
    "approval_case_id": "uuid",
    "approval_type": "sanction",
    "approval_matrix_rule_id": "uuid",
    "required_approvers": [
      {
        "role_code": "cfo",
        "user_id": "uuid",
        "full_name": "CFO"
      },
      {
        "role_code": "director",
        "user_id": "uuid",
        "full_name": "Director 1"
      }
    ],
    "current_status": "pending"
  }
}
```

## 25.3 List Approval Cases

```http
GET /api/v1/approval-cases/?current_status=pending&approval_type=sanction&assigned_to_me=true
```

## 25.4 Retrieve Approval Case

```http
GET /api/v1/approval-cases/{approval_case_id}/
```

### Response

```json
{
  "success": true,
  "data": {
    "approval_case_id": "uuid",
    "approval_type": "sanction",
    "related_entity_type": "loan_application",
    "related_entity_id": "uuid",
    "amount": "400000.00",
    "current_status": "pending",
    "required_approvers": [
      {
        "role_code": "cfo",
        "user_id": "uuid",
        "full_name": "CFO",
        "decision": null
      },
      {
        "role_code": "director",
        "user_id": "uuid",
        "full_name": "Director 1",
        "decision": "approved",
        "acted_at": "2026-06-22T11:00:00Z"
      }
    ],
    "excluded_approvers": [],
    "available_actions": [
      {
        "action_code": "approve",
        "enabled": true
      },
      {
        "action_code": "reject",
        "enabled": true
      }
    ]
  }
}
```

## 25.5 Approve

```http
POST /api/v1/approval-cases/{approval_case_id}/approve/
```

### Request

```json
{
  "comments": "Approved as per appraisal note and authority matrix."
}
```

### Response

```json
{
  "success": true,
  "data": {
    "approval_action_id": "uuid",
    "approval_case_id": "uuid",
    "decision": "approved",
    "approval_case_status": "approved",
    "sanction_decision_created": true,
    "sanction_decision_id": "uuid"
  }
}
```

## 25.6 Reject

```http
POST /api/v1/approval-cases/{approval_case_id}/reject/
```

### Request

```json
{
  "comments": "Rejected due to insufficient eligibility evidence."
}
```

## 25.7 Return for Clarification

```http
POST /api/v1/approval-cases/{approval_case_id}/return-for-clarification/
```

### Request

```json
{
  "comments": "Please clarify crop plan and landholding evidence."
}
```

## 25.8 Sanction Decision

```http
GET /api/v1/loan-applications/{loan_application_id}/sanction-decision/
```

### Response

```json
{
  "success": true,
  "data": {
    "sanction_decision_id": "uuid",
    "decision": "sanctioned",
    "sanctioned_amount": "400000.00",
    "sanctioned_tenure_months": 12,
    "interest_rate_type": "floating",
    "interest_rate_value": "12.0000",
    "repayment_date": "2027-06-22",
    "penal_interest_rate": null,
    "charges": {},
    "security_required_summary": "PoA, SH-4, blank-dated cheque and cancelled cheque required.",
    "conditions_precedent": "Complete documentation and SAP customer code before disbursement.",
    "decision_reason": "Approved by CFO and one Director."
  }
}
```

## 25.9 Credit Sanction Register

```http
GET /api/v1/credit-sanction-register/?financial_year=FY2026-27&decision=sanctioned
```

## 25.10 Exception Register

```http
GET /api/v1/exception-register/?status=approved&exception_type=exceeds_loan_limit
```

## 25.11 General Meeting Approval

For director / relative / Sanction Committee member borrowing.

```http
POST /api/v1/loan-applications/{loan_application_id}/general-meeting-approval/
```

### Request

```json
{
  "related_party_type": "director_relative",
  "related_party_user_id": "uuid",
  "relationship_description": "Borrower is relative of Director.",
  "meeting_date": "2026-07-15",
  "notice_document_id": "uuid",
  "minutes_document_id": "uuid",
  "resolution_document_id": "uuid",
  "approval_status": "approved"
}
```

---

# 26. Document APIs

## 26.1 Upload File

```http
POST /api/v1/document-files/
Content-Type: multipart/form-data
```

### Multipart Fields

| Field | Required | Description |
|---|---:|---|
| `file` | Yes | File binary |
| `document_category` | Yes | KYC / legal / security / finance |
| `sensitivity_level` | Yes | internal / confidential / restricted |
| `related_entity_type` | Optional | application / loan / compliance |
| `related_entity_id` | Optional | Related ID |

### Response

```json
{
  "success": true,
  "data": {
    "document_id": "uuid",
    "file_name": "borrower-pan.pdf",
    "mime_type": "application/pdf",
    "file_size_bytes": 245600,
    "sensitivity_level": "restricted",
    "uploaded_at": "2026-06-22T10:30:00Z"
  }
}
```

## 26.2 Download File

```http
GET /api/v1/document-files/{document_id}/download/
```

### Response Option A: Signed URL

```json
{
  "success": true,
  "data": {
    "download_url": "https://signed-url",
    "expires_at": "2026-06-22T10:40:00Z"
  }
}
```

### Response Option B: Stream

Native file stream.

## 26.3 Document Templates

```http
GET /api/v1/document-templates/
POST /api/v1/document-templates/
PATCH /api/v1/document-templates/{document_template_id}/
```

### Create Template Request

```json
{
  "template_code": "annexure_e_term_sheet_v1",
  "template_name": "Term Sheet",
  "document_type": "term_sheet",
  "borrower_type": "individual_farmer",
  "template_version": "1.0",
  "template_file_id": "uuid",
  "merge_fields": [
    "borrower_name",
    "nominee_name",
    "loan_amount",
    "interest_rate",
    "repayment_date"
  ],
  "approval_status": "approved",
  "effective_from": "2026-04-01"
}
```

## 26.4 Generate Loan Document

```http
POST /api/v1/loan-applications/{loan_application_id}/loan-documents/generate/
```

### Request

```json
{
  "document_type": "term_sheet",
  "template_id": "uuid",
  "output_format": "pdf"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "loan_document_id": "uuid",
    "document_type": "term_sheet",
    "generation_status": "generated",
    "document_id": "uuid",
    "file_name": "term-sheet-LO00000025.pdf"
  }
}
```

## 26.5 List Loan Documents

```http
GET /api/v1/loan-applications/{loan_application_id}/loan-documents/
```

## 26.6 Verify Loan Document

```http
POST /api/v1/loan-documents/{loan_document_id}/verify/
```

### Request

```json
{
  "verification_status": "verified",
  "remarks": "Signed copy verified."
}
```

## 26.7 Record Signature

```http
POST /api/v1/loan-documents/{loan_document_id}/signatures/
```

### Request

```json
{
  "signer_party_type": "borrower",
  "signer_party_id": "uuid",
  "signer_name_snapshot": "Ramesh Patil",
  "signature_method": "wet_ink",
  "signature_status": "signed",
  "signed_at": "2026-06-22T10:30:00Z",
  "signature_mismatch_flag": false
}
```

## 26.8 Resolve Signature Mismatch

```http
POST /api/v1/signature-records/{signature_record_id}/resolve-mismatch/
```

### Request

```json
{
  "mismatch_resolution_type": "bank_verification_letter",
  "mismatch_resolution_document_id": "uuid",
  "remarks": "Bank signed and stamped verification received."
}
```

## 26.9 Stamp Duty Record

```http
POST /api/v1/loan-documents/{loan_document_id}/stamp-duty-record/
```

### Request

```json
{
  "stamp_paper_amount": "500.00",
  "stamp_type": "physical",
  "stamp_number": "MH-STAMP-123",
  "stamp_purchase_date": "2026-06-22",
  "executed_date": "2026-06-22",
  "status": "adequate",
  "remarks": "₹500 stamp paper verified."
}
```

## 26.10 Notarisation Record

```http
POST /api/v1/loan-documents/{loan_document_id}/notarisation-record/
```

### Request

```json
{
  "notary_name": "Notary Name",
  "notary_registration_number": "NOT-123",
  "notarised_date": "2026-06-22",
  "status": "completed",
  "evidence_document_id": "uuid"
}
```

---

# 27. Document Checklist APIs

## 27.1 Get Checklist

```http
GET /api/v1/loan-applications/{loan_application_id}/document-checklist/
```

### Response

```json
{
  "success": true,
  "data": {
    "document_checklist_id": "uuid",
    "loan_application_id": "uuid",
    "checklist_status": "in_progress",
    "items": [
      {
        "checklist_item_id": "uuid",
        "item_code": "poa",
        "item_label": "Power of Attorney",
        "required_flag": true,
        "applicable_flag": true,
        "completion_status": "complete"
      },
      {
        "checklist_item_id": "uuid",
        "item_code": "loan_agreement",
        "item_label": "Loan Agreement",
        "required_flag": true,
        "applicable_flag": true,
        "completion_status": "pending"
      }
    ],
    "signature_status": {
      "company_secretary": "signed",
      "credit_manager": "pending",
      "sanction_committee": "pending",
      "senior_manager_finance": "not_applicable_until_disbursement"
    }
  }
}
```

## 27.2 Create / Refresh Checklist

```http
POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/
```

### Request

```json
{
  "reason": "Refresh checklist after sanction approval."
}
```

## 27.3 Mark Checklist Item Complete

```http
POST /api/v1/checklist-items/{checklist_item_id}/complete/
```

### Request

```json
{
  "loan_document_id": "uuid",
  "remarks": "Document signed, stamped and verified."
}
```

## 27.4 Company Secretary Checklist Approval

```http
POST /api/v1/document-checklists/{document_checklist_id}/approve-as-company-secretary/
```

### Request

```json
{
  "comments": "All documents required for loan disbursement verified and attached."
}
```

## 27.5 Credit Manager Checklist Approval

```http
POST /api/v1/document-checklists/{document_checklist_id}/approve-as-credit-manager/
```

### Request

```json
{
  "comments": "Loan limits reviewed and confirmed."
}
```

## 27.6 Sanction Committee Checklist Approval

```http
POST /api/v1/document-checklists/{document_checklist_id}/approve-as-sanction-committee/
```

### Request

```json
{
  "comments": "Final approval for loan disbursement as per authority matrix."
}
```

## 27.7 Senior Manager Finance Disbursement Signature

```http
POST /api/v1/document-checklists/{document_checklist_id}/sign-disbursement-complete/
```

### Request

```json
{
  "comments": "Loan has been disbursed to loan applicant's account."
}
```

---

# 28. Security Package APIs

## 28.1 Get Security Package

```http
GET /api/v1/loan-applications/{loan_application_id}/security-package/
```

## 28.2 Create / Refresh Security Package

```http
POST /api/v1/loan-applications/{loan_application_id}/security-package/refresh/
```

### Response

```json
{
  "success": true,
  "data": {
    "security_package_id": "uuid",
    "security_status": "pending",
    "physical_share_security_required_flag": true,
    "demat_pledge_required_flag": false,
    "poa_required_flag": true,
    "blank_cheque_required_flag": true,
    "cancelled_cheque_required_flag": true
  }
}
```

## 28.3 Power of Attorney

```http
POST /api/v1/security-packages/{security_package_id}/power-of-attorney/
GET /api/v1/security-packages/{security_package_id}/power-of-attorney/
PATCH /api/v1/power-of-attorneys/{power_of_attorney_id}/
```

### Request

```json
{
  "borrower_member_id": "uuid",
  "nominee_id": "uuid",
  "attorney_user_id": "uuid",
  "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
  "loan_document_id": "uuid",
  "stamp_duty_record_id": "uuid",
  "notarisation_record_id": "uuid",
  "execution_status": "executed",
  "effective_from": "2026-06-22",
  "status": "active"
}
```

## 28.4 SH-4 Share Transfer Form

```http
POST /api/v1/security-packages/{security_package_id}/sh4-share-transfer-form/
GET /api/v1/security-packages/{security_package_id}/sh4-share-transfer-form/
PATCH /api/v1/sh4-share-transfer-forms/{sh4_share_transfer_form_id}/
```

### Request

```json
{
  "member_id": "uuid",
  "witness_id": "uuid",
  "shareholding_id": "uuid",
  "share_count": 100,
  "loan_document_id": "uuid",
  "form_status": "held_in_custody",
  "custody_location": "CS physical custody cabinet",
  "signed_at": "2026-06-22"
}
```

## 28.5 CDSL Pledge

```http
POST /api/v1/security-packages/{security_package_id}/cdsl-share-pledge/
GET /api/v1/security-packages/{security_package_id}/cdsl-share-pledge/
PATCH /api/v1/cdsl-share-pledges/{cdsl_share_pledge_id}/
```

### Request

```json
{
  "pledgor_member_id": "uuid",
  "pledgee_entity_name": "Sahyadri Farmers Producer Company Limited",
  "pledgor_bo_account": "1234567890123456",
  "pledgee_bo_account": "9876543210987654",
  "pledgor_dp_name": "Pledgor DP",
  "pledgee_dp_name": "Pledgee DP",
  "prf_status": "submitted",
  "pledge_sequence_number": "PSN123456",
  "pledge_acceptance_status": "accepted",
  "pledged_share_count": 100,
  "agreement_number": "LA-LO00000025",
  "pledge_status": "created",
  "evidence_document_id": "uuid"
}
```

## 28.6 Blank-Dated Cheque

```http
POST /api/v1/security-packages/{security_package_id}/blank-dated-cheque/
GET /api/v1/security-packages/{security_package_id}/blank-dated-cheque/
PATCH /api/v1/blank-dated-cheques/{blank_dated_cheque_id}/
```

### Request

```json
{
  "member_id": "uuid",
  "bank_account_id": "uuid",
  "cheque_number": "123456",
  "document_id": "uuid",
  "cheque_status": "held",
  "custody_location": "CS secure custody",
  "collected_at": "2026-06-22"
}
```

## 28.7 Security Custody Event

```http
POST /api/v1/security-packages/{security_package_id}/custody-events/
```

### Request

```json
{
  "security_item_type": "blank_dated_cheque",
  "security_item_id": "uuid",
  "event_type": "moved",
  "from_location": "Compliance desk",
  "to_location": "CS secure custody",
  "acknowledgement_document_id": "uuid"
}
```

---

# 29. SAP Customer Code APIs

## 29.1 Create SAP Customer Profile Request

```http
POST /api/v1/loan-applications/{loan_application_id}/sap-customer-profile-request/
```

### Request

```json
{
  "assigned_to_user_id": "uuid",
  "farmer_full_name": "Ramesh Patil",
  "aadhaar_number": "123412341234",
  "pan_number": "ABCDE1234F",
  "address_text": "Village Road, Nashik, Maharashtra, 422001",
  "email_id": "ramesh@example.com",
  "loan_application_number": "LO00000025"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "sap_customer_profile_request_id": "uuid",
    "request_status": "draft",
    "excel_file_id": "uuid"
  }
}
```

## 29.2 Send SAP Request

```http
POST /api/v1/sap-customer-profile-requests/{sap_customer_profile_request_id}/send/
```

### Request

```json
{
  "remarks": "Excel template sent to Senior Manager – Finance."
}
```

## 29.3 Complete SAP Request

```http
POST /api/v1/sap-customer-profile-requests/{sap_customer_profile_request_id}/complete/
```

### Request

```json
{
  "sap_customer_code": "CUST000123",
  "sap_vendor_code": null,
  "created_at_sap": "2026-06-22T12:00:00Z",
  "confirmation_document_id": "uuid",
  "confirmation_notes": "Customer code created in SAP."
}
```

## 29.4 Get SAP Customer Code for Member

```http
GET /api/v1/members/{member_id}/sap-customer-code/
```

---

# 30. Loan Account APIs

## 30.1 Create Loan Account from Sanction

```http
POST /api/v1/loan-applications/{loan_application_id}/create-loan-account/
```

### Request

```json
{
  "sanction_decision_id": "uuid",
  "loan_account_number": "LN-2026-00025"
}
```

### Gate Conditions

- Sanction decision exists and is approved.
- Loan account does not already exist.
- Required sanction fields are present.

## 30.2 List Loan Accounts

```http
GET /api/v1/loan-accounts/?search=&loan_account_status=&member_id=&dpd_bucket=&page=1&page_size=20
```

### Response Item

```json
{
  "loan_account_id": "uuid",
  "loan_account_number": "LN-2026-00025",
  "application_reference_number": "LO00000025",
  "member": {
    "member_id": "uuid",
    "display_name": "Ramesh Patil"
  },
  "sanctioned_amount": "400000.00",
  "disbursed_amount": "400000.00",
  "principal_outstanding": "250000.00",
  "interest_outstanding": "20000.00",
  "total_outstanding": "270000.00",
  "loan_account_status": "active",
  "repayment_date": "2027-06-22",
  "dpd": {
    "days_past_due": 0,
    "sop_bucket": "current"
  }
}
```

## 30.3 Retrieve Loan Account

```http
GET /api/v1/loan-accounts/{loan_account_id}/
```

## 30.4 Update Loan Terms

```http
PATCH /api/v1/loan-accounts/{loan_account_id}/terms/
```

### Request

```json
{
  "repayment_date": "2027-06-22",
  "current_interest_rate": "12.0000"
}
```

### Notes

- Must be restricted.
- Must write audit log.
- Significant changes may require approval case.

## 30.5 Loan Status History

```http
GET /api/v1/loan-accounts/{loan_account_id}/status-history/
```

---

# 31. Disbursement APIs

## 31.1 Disbursement Readiness Check

```http
GET /api/v1/loan-accounts/{loan_account_id}/disbursement-readiness/
```

### Response

```json
{
  "success": true,
  "data": {
    "ready_for_disbursement": true,
    "checks": [
      {
        "code": "sanction_approved",
        "label": "Sanction approved",
        "status": "pass"
      },
      {
        "code": "documentation_complete",
        "label": "Documentation complete",
        "status": "pass"
      },
      {
        "code": "security_package_complete",
        "label": "Security package complete",
        "status": "pass"
      },
      {
        "code": "sap_customer_code_present",
        "label": "SAP customer code present",
        "status": "pass"
      },
      {
        "code": "bank_account_verified",
        "label": "Borrower bank account verified",
        "status": "pass"
      }
    ]
  }
}
```

## 31.2 Initiate Disbursement

```http
POST /api/v1/loan-accounts/{loan_account_id}/disbursements/initiate/
```

### Headers

```http
Idempotency-Key: disbursement-LN-2026-00025-001
```

### Request

```json
{
  "disbursement_amount": "400000.00",
  "borrower_bank_account_id": "uuid",
  "source_bank_account_id": "uuid",
  "final_verification_comments": "All approved documents and details verified."
}
```

### Response

```json
{
  "success": true,
  "data": {
    "disbursement_id": "uuid",
    "initiation_status": "initiated",
    "authorisation_status": "pending",
    "bank_transfer_status": "pending"
  }
}
```

## 31.3 CFC Authorise Disbursement

```http
POST /api/v1/disbursements/{disbursement_id}/authorise/
```

### Request

```json
{
  "decision": "approved",
  "comments": "Authorised for online transfer through RBL Bank."
}
```

## 31.4 Mark Bank Transfer Successful

```http
POST /api/v1/disbursements/{disbursement_id}/mark-transfer-successful/
```

### Request

```json
{
  "bank_reference_number": "RBLUTR123456",
  "disbursed_at": "2026-06-22T14:00:00Z",
  "bank_transfer_evidence_document_id": "uuid"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "disbursement_id": "uuid",
    "bank_transfer_status": "successful",
    "loan_account_status": "active",
    "disbursement_advice_communication_id": "uuid"
  }
}
```

## 31.5 Send Disbursement Advice

```http
POST /api/v1/disbursements/{disbursement_id}/send-advice/
```

### Request

```json
{
  "channel": "email",
  "recipient_email": "borrower@example.com"
}
```

---

# 32. Repayment APIs

## 32.1 List Repayments

```http
GET /api/v1/loan-accounts/{loan_account_id}/repayments/
```

## 32.2 Capture Direct Repayment

```http
POST /api/v1/loan-accounts/{loan_account_id}/repayments/
```

### Headers

```http
Idempotency-Key: repayment-UTR123456
```

### Request

```json
{
  "repayment_source": "direct_farmer",
  "amount_received": "100000.00",
  "received_date": "2026-12-01",
  "payment_method": "neft",
  "bank_reference_number": "UTR123456",
  "bank_statement_line_id": "uuid",
  "remarks": "Direct NEFT repayment received."
}
```

## 32.3 Capture Subsidiary Deduction Repayment

```http
POST /api/v1/loan-accounts/{loan_account_id}/repayments/
```

### Request

```json
{
  "repayment_source": "subsidiary_deduction",
  "amount_received": "75000.00",
  "received_date": "2026-12-15",
  "payment_method": "subsidiary_transfer",
  "bank_reference_number": "SUBTRF123",
  "subsidiary_company_id": "uuid",
  "produce_payment_reference": "PROD-PAY-567",
  "bank_statement_line_id": "uuid",
  "remarks": "Deducted from produce payment as per tri-party agreement."
}
```

## 32.4 Allocate Repayment

```http
POST /api/v1/repayments/{repayment_id}/allocate/
```

### Request

```json
{
  "allocation_rule": "principal_first",
  "remarks": "Partial repayment allocated to principal first as per SOP."
}
```

### Response

```json
{
  "success": true,
  "data": {
    "repayment_allocation_id": "uuid",
    "allocated_to_principal": "100000.00",
    "allocated_to_interest": "0.00",
    "allocated_to_charges": "0.00",
    "loan_account": {
      "principal_outstanding": "300000.00",
      "interest_outstanding": "0.00",
      "total_outstanding": "300000.00"
    }
  }
}
```

## 32.5 Mark SAP Repayment Posting

```http
POST /api/v1/repayments/{repayment_id}/mark-sap-posted/
```

### Request

```json
{
  "sap_entry_reference": "SAP-RCPT-123",
  "sap_posted_at": "2026-12-02T10:00:00Z",
  "remarks": "Receipt entry posted in SAP."
}
```

---

# 33. Interest APIs

## 33.1 Generate Interest Invoice

```http
POST /api/v1/loan-accounts/{loan_account_id}/interest-invoices/
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "interest_period_start": "2026-04-01",
  "interest_period_end": "2027-03-31",
  "principal_base_amount": "400000.00",
  "interest_rate": "12.0000",
  "interest_amount": "48000.00",
  "invoice_date": "2027-03-31"
}
```

## 33.2 List Interest Invoices

```http
GET /api/v1/loan-accounts/{loan_account_id}/interest-invoices/
GET /api/v1/interest-invoices/?financial_year=FY2026-27&invoice_status=issued
```

## 33.3 Issue Interest Invoice

```http
POST /api/v1/interest-invoices/{interest_invoice_id}/issue/
```

### Request

```json
{
  "channel": "email",
  "recipient_email": "borrower@example.com",
  "remarks": "Year-end interest invoice issued."
}
```

## 33.4 Create Monthly Accrual

```http
POST /api/v1/loan-accounts/{loan_account_id}/accrual-entries/
```

### Request

```json
{
  "accrual_month": "2026-06",
  "principal_base_amount": "400000.00",
  "interest_rate": "12.0000",
  "interest_accrued_amount": "4000.00"
}
```

## 33.5 Bulk Generate Monthly Accruals

```http
POST /api/v1/accrual-entries/bulk-generate/
```

### Request

```json
{
  "accrual_month": "2026-06",
  "loan_account_ids": ["uuid", "uuid"],
  "dry_run": false
}
```

## 33.6 Interest Capitalisation Check

```http
POST /api/v1/interest-capitalisations/check/
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "as_of_date": "2027-04-30",
  "dry_run": true
}
```

## 33.7 Capitalise Interest

```http
POST /api/v1/loan-accounts/{loan_account_id}/interest-capitalisations/
```

### Headers

```http
Idempotency-Key: capitalisation-LN-2026-00025-FY2026-27
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "unpaid_interest_amount": "48000.00",
  "capitalisation_date": "2027-05-01",
  "send_borrower_intimation": true
}
```

### Response

```json
{
  "success": true,
  "data": {
    "interest_capitalisation_id": "uuid",
    "old_principal_amount": "400000.00",
    "new_principal_amount": "448000.00",
    "borrower_intimation_email_id": "uuid",
    "borrower_intimation_letter_document_id": "uuid"
  }
}
```

---

# 34. Monitoring and Reminder APIs

## 34.1 DPD Status

```http
GET /api/v1/loan-accounts/{loan_account_id}/dpd-status/
POST /api/v1/loan-accounts/{loan_account_id}/dpd-status/calculate/
```

### Calculate Response

```json
{
  "success": true,
  "data": {
    "dpd_status_id": "uuid",
    "as_of_date": "2027-06-30",
    "days_past_due": 8,
    "sop_bucket": "current",
    "standard_bucket": "0_30",
    "principal_overdue_amount": "50000.00",
    "interest_overdue_amount": "0.00",
    "total_overdue_amount": "50000.00"
  }
}
```

## 34.2 Bulk DPD Calculation

```http
POST /api/v1/dpd-statuses/bulk-calculate/
```

### Request

```json
{
  "as_of_date": "2027-06-30",
  "loan_account_ids": [],
  "include_all_active_loans": true
}
```

## 34.3 Send Reminder

```http
POST /api/v1/loan-accounts/{loan_account_id}/reminders/
```

### Request

```json
{
  "reminder_type": "outstanding_beyond_one_year",
  "channel": "sms",
  "content_template_id": "uuid",
  "message_body": "Your loan is outstanding. Please contact SFPCL Credit Team.",
  "send_now": true
}
```

## 34.4 Phone Reminder Log

```http
POST /api/v1/loan-accounts/{loan_account_id}/reminders/
```

### Request

```json
{
  "reminder_type": "repayment_due",
  "channel": "phone",
  "message_body": "Called borrower regarding repayment due.",
  "call_outcome": "Borrower confirmed payment by next week.",
  "send_now": false
}
```

## 34.5 Quarterly MIS

```http
POST /api/v1/quarterly-mis-reports/generate/
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "quarter": "Q1",
  "as_of_date": "2026-06-30"
}
```

```http
GET /api/v1/quarterly-mis-reports/?financial_year=FY2026-27&quarter=Q1
POST /api/v1/quarterly-mis-reports/{quarterly_mis_report_id}/submit-to-cfo/
POST /api/v1/quarterly-mis-reports/{quarterly_mis_report_id}/mark-reviewed/
```

---

# 35. Default and Recovery APIs

## 35.1 Open Default Case

```http
POST /api/v1/loan-accounts/{loan_account_id}/default-cases/open/
```

### Request

```json
{
  "trigger_event": "missed_principal_repayment",
  "scheduled_due_date": "2027-06-22",
  "reason": "Scheduled principal repayment missed."
}
```

### Response

```json
{
  "success": true,
  "data": {
    "default_case_id": "uuid",
    "default_case_status": "grace_period_active",
    "grace_period_start_date": "2027-06-22",
    "grace_period_end_date": "2027-09-22"
  }
}
```

## 35.2 Get Default Case

```http
GET /api/v1/default-cases/{default_case_id}/
```

## 35.3 List Default Cases

```http
GET /api/v1/default-cases/?default_case_status=grace_period_active&member_id=&loan_account_id=
```

## 35.4 Default Assessment

```http
POST /api/v1/default-cases/{default_case_id}/assess/
```

### Request

```json
{
  "assessment_type": "post_grace",
  "payment_failure_classification": "non_intentional",
  "reason_summary": "Crop loss and delayed produce payment.",
  "evidence_document_ids": ["uuid"],
  "borrower_interaction_summary": "Borrower contacted and explained delay.",
  "recommended_action": "grant_extension"
}
```

## 35.5 Grant One-Year Extension

```http
POST /api/v1/default-cases/{default_case_id}/grant-extension/
```

### Request

```json
{
  "extension_reason": "Non-intentional non-payment due to crop loss.",
  "extension_start_date": "2027-09-23",
  "extension_end_date": "2028-09-22",
  "document_id": "uuid"
}
```

## 35.6 Create Non-Payment Note

```http
POST /api/v1/default-cases/{default_case_id}/non-payment-note/
```

### Request

```json
{
  "reason_for_non_payment": "Borrower unable to repay after one-year extension.",
  "intentionality_assessment": "unclear",
  "outstanding_principal_amount": "300000.00",
  "outstanding_interest_amount": "45000.00",
  "recommended_recovery_action": "present_to_sanction_committee"
}
```

## 35.7 Submit Non-Payment Note to Sanction Committee

```http
POST /api/v1/non-payment-notes/{non_payment_note_id}/submit-to-sanction-committee/
```

## 35.8 Create Recovery Decision

```http
POST /api/v1/default-cases/{default_case_id}/recovery-decision/
```

### Request

```json
{
  "approval_case_id": "uuid",
  "decision": "invoke_sh4",
  "decision_reason": "Approved by Sanction Committee after review of Non-Payment Note."
}
```

## 35.9 Execute Recovery Action

```http
POST /api/v1/recovery-decisions/{recovery_decision_id}/actions/
```

### Request

```json
{
  "action_type": "invoke_sh4",
  "initiated_at": "2028-09-30T10:00:00Z",
  "evidence_document_ids": ["uuid"],
  "remarks": "SH-4 invocation initiated."
}
```

## 35.10 Mark Recovery Action Complete

```http
POST /api/v1/recovery-actions/{recovery_action_id}/complete/
```

### Request

```json
{
  "completed_at": "2028-10-15T10:00:00Z",
  "amount_recovered": "250000.00",
  "evidence_document_ids": ["uuid"],
  "remarks": "Recovery action completed."
}
```

---

# 36. Closure APIs

## 36.1 Closure Readiness Check

```http
GET /api/v1/loan-accounts/{loan_account_id}/closure-readiness/
```

### Response

```json
{
  "success": true,
  "data": {
    "ready_for_closure": true,
    "checks": [
      {
        "code": "principal_paid",
        "status": "pass"
      },
      {
        "code": "interest_paid",
        "status": "pass"
      },
      {
        "code": "charges_paid",
        "status": "pass"
      }
    ],
    "total_outstanding": "0.00"
  }
}
```

## 36.2 Close Loan

```http
POST /api/v1/loan-accounts/{loan_account_id}/closure/
```

### Request

```json
{
  "closure_type": "full_repayment",
  "closure_notes": "Principal and interest fully repaid."
}
```

### Response

```json
{
  "success": true,
  "data": {
    "loan_closure_id": "uuid",
    "loan_account_status": "closed",
    "noc_required": true,
    "security_return_required": true,
    "archive_required": true
  }
}
```

## 36.3 Issue NOC

```http
POST /api/v1/loan-closures/{loan_closure_id}/noc/
```

### Request

```json
{
  "document_id": "uuid",
  "delivery_mode": "email",
  "recipient_email": "borrower@example.com"
}
```

## 36.4 Record Security Return

```http
POST /api/v1/loan-closures/{loan_closure_id}/security-return/
```

### Request

```json
{
  "security_package_id": "uuid",
  "sh4_returned_flag": true,
  "blank_cheque_returned_flag": true,
  "cdsl_unpledge_completed_flag": false,
  "poa_released_flag": true,
  "returned_to_party_name": "Ramesh Patil",
  "returned_at": "2027-06-30T10:00:00Z",
  "acknowledgement_document_id": "uuid"
}
```

## 36.5 Archive Loan File

```http
POST /api/v1/loan-closures/{loan_closure_id}/archive/
```

### Request

```json
{
  "file_location_physical": "Archive Room / Rack A / Box 12",
  "file_location_digital": "s3://bucket/archive/LN-2026-00025",
  "retention_start_date": "2027-06-30",
  "retention_until_date": "2035-06-30"
}
```

---

# 37. Compliance APIs

## 37.1 Compliance Controls

```http
GET /api/v1/compliance-controls/
POST /api/v1/compliance-controls/
PATCH /api/v1/compliance-controls/{compliance_control_id}/
```

### Response Item

```json
{
  "compliance_control_id": "uuid",
  "control_code": "NBFC_PRINCIPAL_TEST",
  "control_name": "NBFC Principal Business Test",
  "control_area": "nbfc",
  "legal_basis": "RBI principal business test monitoring requirement.",
  "control_type": "detective",
  "frequency": "quarterly",
  "owner_role_code": "cfo",
  "evidence_required": "Ratio calculation and Board minutes.",
  "risk_if_missed": "Potential NBFC registration non-compliance.",
  "status": "active"
}
```

## 37.2 Compliance Tasks

```http
GET /api/v1/compliance-tasks/?task_status=overdue&assigned_to_me=true
POST /api/v1/compliance-tasks/
PATCH /api/v1/compliance-tasks/{compliance_task_id}/
```

## 37.3 Submit Compliance Evidence

```http
POST /api/v1/compliance-tasks/{compliance_task_id}/evidence/
```

### Request

```json
{
  "evidence_type": "board_minutes",
  "document_id": "uuid",
  "summary": "NBFC ratio presented to Board.",
  "review_status": "pending"
}
```

## 37.4 Review Compliance Evidence

```http
POST /api/v1/compliance-evidence/{compliance_evidence_id}/review/
```

### Request

```json
{
  "review_status": "accepted",
  "review_comments": "Evidence accepted."
}
```

## 37.5 Section 186 Tracker

```http
POST /api/v1/compliance/section-186-trackers/
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "quarter": "Q1",
  "paid_up_capital_amount": "10000000.00",
  "free_reserves_amount": "5000000.00",
  "securities_premium_amount": "2000000.00",
  "total_loans_exposure_amount": "8000000.00"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "section_186_tracker_id": "uuid",
    "limit_60_percent_basis_amount": "10200000.00",
    "limit_100_percent_basis_amount": "7000000.00",
    "applicable_limit_amount": "10200000.00",
    "total_loans_exposure_amount": "8000000.00",
    "within_limit_flag": true,
    "special_resolution_required_flag": false
  }
}
```

## 37.6 NBFC Principal Test

```http
POST /api/v1/compliance/nbfc-principal-tests/
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "quarter": "Q1",
  "financial_assets_amount": "20000000.00",
  "total_assets_amount": "60000000.00",
  "financial_income_amount": "1000000.00",
  "gross_income_amount": "8000000.00"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "nbfc_principal_test_id": "uuid",
    "financial_asset_ratio": "33.3333",
    "financial_income_ratio": "12.5000",
    "registration_triggered_flag": false,
    "early_warning_flag": false
  }
}
```

## 37.7 Money-Lending Law Review

```http
POST /api/v1/compliance/money-lending-law-reviews/
```

### Request

```json
{
  "financial_year": "FY2026-27",
  "state": "Maharashtra",
  "exemption_applicable_flag": true,
  "legal_opinion_document_id": "uuid",
  "board_note_document_id": "uuid",
  "remarks": "Annual legal opinion confirms exemption for member-only lending."
}
```

---

# 38. Grievance APIs

## 38.1 Create Grievance

```http
POST /api/v1/grievances/
```

### Request

```json
{
  "member_id": "uuid",
  "loan_account_id": "uuid",
  "loan_application_id": null,
  "grievance_category": "repayment",
  "description": "Borrower disputes interest invoice amount.",
  "received_date": "2026-06-22",
  "received_channel": "phone",
  "assigned_to_user_id": "uuid",
  "resolution_due_date": "2026-06-29"
}
```

## 38.2 List Grievances

```http
GET /api/v1/grievances/?status=open&member_id=&grievance_category=
```

## 38.3 Resolve Grievance

```http
POST /api/v1/grievances/{grievance_id}/resolve/
```

### Request

```json
{
  "resolution_summary": "Interest invoice clarified and corrected.",
  "resolution_document_id": "uuid"
}
```

---

# 39. Communication APIs

## 39.1 Content Templates

```http
GET /api/v1/content-templates/
POST /api/v1/content-templates/
PATCH /api/v1/content-templates/{content_template_id}/
```

### Create Request

```json
{
  "template_code": "loan_rejection_email_v1",
  "template_name": "Loan Rejection Email",
  "template_type": "email",
  "language_code": "en",
  "audience": "borrower",
  "subject_template": "Loan Application {{application_reference_number}} - Rejection Note",
  "body_template": "Dear {{borrower_name}}, your application has been rejected for the following reason: {{rejection_reason}}.",
  "variables": [
    "application_reference_number",
    "borrower_name",
    "rejection_reason"
  ],
  "approval_status": "approved",
  "template_version": "1.0",
  "effective_from": "2026-04-01"
}
```

## 39.2 Send Communication

```http
POST /api/v1/communications/send/
```

### Request

```json
{
  "related_entity_type": "loan_application",
  "related_entity_id": "uuid",
  "recipient_party_type": "borrower",
  "recipient_party_id": "uuid",
  "recipient_address": "borrower@example.com",
  "channel": "email",
  "content_template_id": "uuid",
  "merge_data": {
    "application_reference_number": "LO00000025",
    "borrower_name": "Ramesh Patil",
    "rejection_reason": "Eligibility criteria not met."
  }
}
```

## 39.3 List Communications

```http
GET /api/v1/communications/?related_entity_type=loan_application&related_entity_id=uuid
```

---

# 40. Reporting APIs

## 40.1 Application Pipeline Report

```http
GET /api/v1/reports/application-pipeline/?from_date=2026-04-01&to_date=2026-06-30&status=&stage=
```

## 40.2 Documentation Readiness Report

```http
GET /api/v1/reports/documentation-readiness/?status=pending
```

## 40.3 Disbursement Pending Report

```http
GET /api/v1/reports/disbursement-pending/
```

## 40.4 Loan Portfolio Report

```http
GET /api/v1/reports/loan-portfolio/?as_of_date=2026-06-30
```

## 40.5 DPD Report

```http
GET /api/v1/reports/dpd/?as_of_date=2026-06-30&sop_bucket=one_to_two_years
```

## 40.6 Compliance Dashboard

```http
GET /api/v1/reports/compliance-dashboard/?financial_year=FY2026-27
```

## 40.7 Export Report

```http
POST /api/v1/reports/exports/
```

### Request

```json
{
  "report_code": "loan_portfolio",
  "format": "xlsx",
  "filters": {
    "as_of_date": "2026-06-30",
    "loan_account_status": "active"
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "export_job_id": "uuid",
    "status": "queued"
  }
}
```

## 40.8 Export Job Status

```http
GET /api/v1/reports/exports/{export_job_id}/
```

### Response

```json
{
  "success": true,
  "data": {
    "export_job_id": "uuid",
    "status": "completed",
    "download_url": "https://signed-url",
    "expires_at": "2026-06-22T11:00:00Z"
  }
}
```

---

# 41. Configuration APIs

## 41.1 Loan Policy Config

```http
GET /api/v1/config/loan-policy/
POST /api/v1/config/loan-policy/
PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/
POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/
```

### Request

```json
{
  "policy_name": "SFPCL Loan Policy",
  "policy_version": "1.0",
  "effective_from": "2026-04-01",
  "short_term_duration_months": 12,
  "min_secured_loan_months": 3,
  "max_secured_loan_years": 7,
  "approval_threshold_amount": "500000.00",
  "default_scale_of_finance_per_acre_amount": "20000.00",
  "share_limit_percentage": "10.0000",
  "per_share_cap_amount": "200.00",
  "interest_rate_type": "floating",
  "interest_benchmark": null,
  "penal_interest_rate": null,
  "rekyc_frequency_months": 24,
  "record_retention_years": 8,
  "grace_period_months": 3,
  "non_intentional_extension_months": 12,
  "board_approval_reference": "BOARD-REF-001"
}
```

## 41.2 Share Valuation Config

```http
GET /api/v1/config/share-valuations/
POST /api/v1/config/share-valuations/
PATCH /api/v1/config/share-valuations/{share_valuation_id}/
POST /api/v1/config/share-valuations/{share_valuation_id}/approve/
```

## 41.3 Scale of Finance Config

```http
GET /api/v1/config/scale-of-finance/
POST /api/v1/config/scale-of-finance/
```

## 41.4 Interest Rate Config

```http
GET /api/v1/config/interest-rates/
POST /api/v1/config/interest-rates/
POST /api/v1/config/interest-rates/{interest_rate_config_id}/activate/
```

---

# 42. Audit and Workflow APIs

## 42.1 Audit Logs

```http
GET /api/v1/audit-logs/?entity_type=loan_application&entity_id=uuid
```

### Response Item

```json
{
  "audit_log_id": "uuid",
  "actor": {
    "user_id": "uuid",
    "full_name": "Credit Manager"
  },
  "actor_type": "user",
  "action": "loan_application.submitted",
  "entity_type": "loan_application",
  "entity_id": "uuid",
  "old_value": {
    "application_status": "draft"
  },
  "new_value": {
    "application_status": "submitted"
  },
  "ip_address": "10.0.0.1",
  "created_at": "2026-06-22T10:30:00Z"
}
```

## 42.2 Workflow Events

```http
GET /api/v1/workflow-events/?entity_type=loan_application&entity_id=uuid
```

## 42.3 Version History

```http
GET /api/v1/version-histories/?versioned_entity_type=loan_policy_config&versioned_entity_id=uuid
```

---

# 43. Dashboard APIs

## 43.1 Role-Based Dashboard

```http
GET /api/v1/dashboard/
```

### Response for Credit Manager

```json
{
  "success": true,
  "data": {
    "role_context": "credit_manager",
    "cards": [
      {
        "code": "applications_pending_completeness",
        "label": "Applications Pending Completeness",
        "count": 12,
        "link": "/applications?status=completeness_check_pending"
      },
      {
        "code": "appraisals_due_today",
        "label": "Appraisals Due Today",
        "count": 4,
        "link": "/applications?tat=due_today"
      },
      {
        "code": "loans_outstanding_beyond_one_year",
        "label": "Outstanding Beyond One Year",
        "count": 18,
        "link": "/loans?outstanding_beyond_one_year=true"
      }
    ],
    "tasks": [
      {
        "task_type": "review_appraisal",
        "entity_id": "uuid",
        "title": "Review appraisal for LO00000025",
        "due_at": "2026-06-24T10:30:00Z"
      }
    ]
  }
}
```

## 43.2 Sanction Committee Dashboard

```http
GET /api/v1/dashboard/sanction-committee/
```

## 43.3 Compliance Dashboard

```http
GET /api/v1/dashboard/compliance/
```

## 43.4 Treasury Dashboard

```http
GET /api/v1/dashboard/treasury/
```

---

# 44. Frontend Action Availability Contract

Every detail endpoint should optionally return `available_actions`.

Example:

```json
{
  "available_actions": [
    {
      "action_code": "submit",
      "label": "Submit Application",
      "enabled": false,
      "disabled_reason": "Nominee Aadhaar document is missing.",
      "required_permission": "loan_application.submit",
      "required_role": "credit_manager"
    },
    {
      "action_code": "return_with_deficiencies",
      "label": "Return with Deficiencies",
      "enabled": true,
      "disabled_reason": null,
      "required_permission": "loan_application.return_deficiency"
    }
  ]
}
```

Frontend must use this for UI display, but backend must still enforce all permissions and workflow guards.

---

# 45. Idempotency Contract

Critical endpoints must require `Idempotency-Key`.

## 45.1 Endpoints Requiring Idempotency

| Endpoint | Reason |
|---|---|
| `POST /loan-accounts/{id}/disbursements/initiate/` | Prevent duplicate disbursement |
| `POST /disbursements/{id}/mark-transfer-successful/` | Prevent duplicate loan activation |
| `POST /loan-accounts/{id}/repayments/` | Prevent duplicate repayment capture |
| `POST /repayments/{id}/allocate/` | Prevent duplicate allocation |
| `POST /loan-accounts/{id}/interest-capitalisations/` | Prevent duplicate capitalisation |
| `POST /loan-accounts/{id}/closure/` | Prevent duplicate closure |
| `POST /recovery-decisions/{id}/actions/` | Prevent duplicate recovery action |

## 45.2 Idempotency Response

If a duplicate idempotency key is submitted, return the original response:

```json
{
  "success": true,
  "data": {
    "idempotency_replayed": true,
    "original_response": {}
  }
}
```

---

# 46. Webhook / Event Callback Contracts

Webhooks are optional for future integrations.

## 46.1 Bank Payment Status Webhook

```http
POST /api/v1/webhooks/bank/payment-status/
```

### Request

```json
{
  "bank_reference_number": "RBLUTR123456",
  "status": "successful",
  "amount": "400000.00",
  "completed_at": "2026-06-22T14:00:00Z",
  "signature": "provider-signature"
}
```

## 46.2 Email Delivery Webhook

```http
POST /api/v1/webhooks/email/delivery-status/
```

### Request

```json
{
  "external_message_id": "email-provider-id",
  "delivery_status": "delivered",
  "delivered_at": "2026-06-22T10:31:00Z"
}
```

## 46.3 SMS Delivery Webhook

```http
POST /api/v1/webhooks/sms/delivery-status/
```

### Request

```json
{
  "external_message_id": "sms-provider-id",
  "delivery_status": "delivered",
  "delivered_at": "2026-06-22T10:31:00Z"
}
```

---

# 47. OpenAPI Tag Structure

Recommended OpenAPI tags:

| Tag | Description |
|---|---|
| Auth | Login, refresh, logout, current user |
| Users and Roles | User, role, team and permission administration |
| Members | Member master and profiles |
| KYC | KYC profiles, documents and re-KYC |
| Shareholding | Shareholdings, share certificates and demat accounts |
| Applications | Loan application intake and lifecycle |
| Credit Assessment | Eligibility, loan limit, appraisal and risk |
| Approvals | Approval matrix, cases, actions and sanction |
| Documents | Files, templates, loan documents and checklist |
| Security | PoA, SH-4, CDSL pledge and cheques |
| SAP | SAP customer code workflow |
| Loans | Loan accounts, terms and schedules |
| Disbursement | Disbursement readiness and transfer workflow |
| Repayment | Repayments and allocations |
| Interest | Invoices, accruals and capitalisation |
| Monitoring | DPD, reminders and MIS |
| Default | Default cases, assessments and extensions |
| Recovery | Recovery decisions and actions |
| Closure | NOC, security return and archive |
| Compliance | Controls, tasks and statutory trackers |
| Communications | Templates and outbound communication |
| Grievances | Complaint handling |
| Reports | Operational and compliance reports |
| Configuration | Policy, valuation, interest and scale-of-finance config |
| Audit | Audit logs, workflow events and version history |

---

# 48. MVP Endpoint Prioritisation

## 48.1 MVP 1: Origination and Approval

Required endpoints:

- Auth.
- Users / roles / teams.
- Members.
- Nominees.
- Shareholdings.
- Land holdings.
- Crop plans.
- KYC document upload.
- Loan applications.
- Application documents.
- Deficiencies.
- Eligibility assessment.
- Loan limit calculation.
- Appraisal note.
- Approval cases.
- Sanction decisions.
- Credit Sanction Register.
- Exception Register.
- Rejection notes.

## 48.2 MVP 2: Documentation and Disbursement

Required endpoints:

- Document templates.
- Loan document generation.
- Checklist.
- Signature records.
- Stamp duty records.
- Notarisation records.
- Security package.
- PoA.
- SH-4.
- CDSL pledge.
- Blank-dated cheque.
- SAP customer request.
- SAP customer code.
- Loan account creation.
- Disbursement readiness.
- Disbursement initiation.
- CFC authorisation.
- Disbursement advice.

## 48.3 MVP 3: Servicing and Monitoring

Required endpoints:

- Loan accounts.
- Repayment schedules.
- Repayments.
- Repayment allocation.
- Interest invoices.
- Accrual entries.
- Interest capitalisation.
- DPD calculation.
- Reminders.
- Quarterly MIS.
- Reports.

## 48.4 MVP 4: Default, Recovery, Closure and Compliance

Required endpoints:

- Default cases.
- Default assessments.
- Extension notes.
- Non-payment notes.
- Recovery decisions.
- Recovery actions.
- Loan closure.
- NOC.
- Security return.
- Archive record.
- Compliance controls.
- Compliance tasks.
- Section 186 tracker.
- NBFC principal test.
- KYC reviews.
- Grievances.
- Audit and workflow events.

---

# 49. QA Contract Checklist

QA should verify the following API behaviours:

| Area | Expected Behaviour |
|---|---|
| Authentication | Expired access token rejected; refresh works; logout revokes token |
| Permissions | Users cannot access unauthorised modules or objects |
| Sensitive data | PAN, Aadhaar and bank details masked by default |
| Application sequence | Application references are unique and sequential |
| Completeness gate | Incomplete applications cannot move to appraisal |
| Eligibility gate | Ineligible applications cannot proceed without exception |
| Loan limit | Final eligible amount is lower of share and land limits |
| Approval matrix | Correct approvers required based on amount and exception |
| Approvals | Approval actions are immutable |
| Documentation gate | Disbursement blocked until documents complete |
| Security gate | Required PoA / SH-4 / CDSL / cheque controls enforced |
| SAP gate | Disbursement blocked without SAP customer code |
| Bank gate | Disbursement blocked without verified bank account |
| CFC gate | Transfer cannot complete without CFC authorisation |
| Repayment | Partial repayment allocated to principal first |
| Interest | Duplicate accrual and duplicate capitalisation prevented |
| DPD | DPD buckets calculated correctly |
| Default | Missed principal creates grace period |
| Extension | Non-intentional default allows one-year extension |
| Recovery | SH-4 / cheque invocation blocked without approval |
| Closure | Loan cannot close with outstanding amount |
| NOC | NOC generated after full repayment |
| Archive | Retention date at least eight years |
| Compliance | Section 186 and NBFC tests calculate correctly |
| Audit | Critical actions create audit logs |

---

# 50. Final API Contract Summary

The SFPCL API architecture must support a strict, auditable and workflow-driven lending lifecycle. The API should not expose generic CRUD alone. It must expose explicit, permission-controlled action endpoints that correspond to the SOP controls:

- Submit application.
- Complete check.
- Run eligibility.
- Calculate loan limit.
- Prepare and review appraisal.
- Submit to Sanction Committee.
- Approve or reject sanction.
- Generate and verify documents.
- Complete checklist.
- Create security package.
- Request SAP customer code.
- Initiate and authorise disbursement.
- Capture and allocate repayment.
- Generate interest invoice.
- Capitalise unpaid interest.
- Calculate DPD.
- Open default case.
- Grant extension.
- Approve recovery.
- Close loan.
- Issue NOC.
- Return security.
- Archive file.
- Track compliance.

The most important implementation rule is that **the backend must enforce every workflow gate, permission and policy rule independently of the frontend**. React should use `available_actions` for user experience, but Django services must remain the source of truth for allowed transitions and compliance controls.

This API contract should be converted into an OpenAPI specification during implementation and used as the basis for backend development, frontend integration, QA automation and UAT test planning.
