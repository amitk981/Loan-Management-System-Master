# Template File Reference Boundary Matrix

All examples use synthetic ids and contain no borrower/member data.

| Actor/file condition | Result | Template/audit/version write |
|---|---|---:|
| Manage + file-reference; singular matching global/template-source upload ledger | `200`, metadata-only template response | One attributable success set |
| Manage only | Nondisclosing `400 VALIDATION_ERROR` | Zero |
| Manage + file download, without file-reference | Same nondisclosing `400` | Zero |
| File-reference only, without manage | `403 FORBIDDEN` before template write | Zero |
| Missing file or bare direct file row | Same nondisclosing `400` | Zero |
| Missing, corrupt, or duplicate upload ledger | Same nondisclosing `400` | Zero |
| Application-owned/legal upload | Same nondisclosing `400` | Zero |
| Unsupported or ledger-mismatched sensitivity | Same nondisclosing `400` | Zero |

Success data contains only template/file metadata (`template_file_id`, `template_file_name`) and
never contains a download URL, storage key, descriptor, or enabled action. Reference checks write
no download audit.

## Sanitized success example

```json
{
  "success": true,
  "data": {
    "document_template_id": "00000000-0000-4000-8000-000000000001",
    "template_code": "annexure_e_term_sheet_v1",
    "document_type": "term_sheet",
    "borrower_type": "individual_farmer",
    "template_version": "1.0",
    "template_file_id": "00000000-0000-4000-8000-000000000002",
    "template_file_name": "term-sheet.docx",
    "approval_status": "approved"
  }
}
```

## Sanitized failure example

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Document template failed validation.",
    "field_errors": {
      "template_file_id": "Document file was not found or is inaccessible."
    }
  }
}
```
