# Sanitized SAP Request Evidence

## Public response shape

```json
{
  "success": true,
  "data": {
    "sap_customer_profile_request_id": "<uuid>",
    "request_status": "draft",
    "excel_file_id": "<uuid>",
    "assigned_to_user": {
      "user_id": "<uuid>",
      "full_name": "SAP Senior Manager Finance"
    }
  },
  "error": null,
  "meta": {
    "request_id": "req-sap-profile-001",
    "timestamp": "<utc-timestamp>"
  }
}
```

The response contains no PAN, Aadhaar, bank account, address, or sanction values.

## Programmatic workbook inspection

The focused test opens the retained ZIP/OOXML package, parses
`xl/worksheets/sheet1.xml`, and verifies these headings:

1. Loan Application Number
2. Borrower Full Name
3. Borrower Type
4. Aadhaar Number
5. PAN Number
6. Registered Address
7. Email ID
8. Mobile Number
9. Folio Number
10. Sanctioned Amount
11. Sanction Date
12. Bank Account Last Four
13. IFSC

The same test verifies that the restricted outbound workbook contains the canonical fixture values,
while the ordinary API response and audit evidence contain none of the synthetic PAN, Aadhaar, or
address values. It also verifies that persisted PAN/Aadhaar snapshots are shared-field-encryption
ciphertexts rather than plaintext. The post-review test additionally reads the physical retained
bytes, proves that they are authenticated ciphertext rather than a ZIP/XLSX or secret-bearing
payload, and recovers the readable workbook only through the Finance encrypted-storage adapter.
See `009A-focused-api-service-post-review.log` and `009A-review-green.log` for the passing results.
