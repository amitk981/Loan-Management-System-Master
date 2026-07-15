# API Examples

## Completed action projection

```json
{"action_code":"term_sheet","status":"complete","upload_allowed":false,"reupload_allowed":false,"download":{"action_url":"/api/v1/portal/applications/<application>/documentation-actions/term_sheet/download/"}}
```

## Signed descriptor

```json
{"download_url":"/api/v1/portal/applications/<application>/documentation-actions/term_sheet/download/?content=1&token=<signed-capability>","expires_at":"<server-issued>"}
```

The content request is authenticated, current-file/scope bound, checksum verified, and returns
`Cache-Control: no-store` plus `Pragma: no-cache`. Tampered, expired, replaced, or cross-action
tokens return nondisclosing `404 NOT_FOUND`.

## Guarded resubmission

```json
{"loan_application_id":"<application>","application_status":"submitted","completeness_status":"not_started","current_stage":"initial_loan_request","pending_with":"SFPCL","responded_deficiency_count":1}
```

The canonical audit action is `applications.loan_application.resubmitted`; immutable response
workflow state advances from `responded` to `submitted_for_review` while the staff deficiency stays
`open`.
