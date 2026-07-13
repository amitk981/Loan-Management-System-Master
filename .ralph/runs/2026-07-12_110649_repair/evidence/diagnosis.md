# 006Y4 Trusted-Browser Failure Diagnosis

## Exact symptom

Both independent runs reached `POST
/api/v1/loan-applications/00000000-0000-4000-8000-000000000601/witnesses/` and received `400`
instead of `200`, so no declared witness screenshots were produced.

## Root cause

The spec's first test approves a verified identity correction for member `...0602`. That governed
action correctly resets the member's KYC status to pending. The next test reused member `...0602`
as its witness, and the witness API correctly rejects any member whose KYC is not verified. The
failure was cross-test fixture coupling, not a production witness-validation defect.

## Repair

The deterministic E2E seed now creates member `...0611` (`MEM-E2E-006-W`) with its own active,
positive shareholding `...0612`. The witness browser flow captures that stable verified shareholder,
while the member-governance flow continues to mutate only member `...0602`.

## Regression signal

`test_seeded_witness_capture_is_independent_of_borrower_reverification` explicitly sets the
application borrower's KYC to pending and then performs the real authenticated witness POST using
the dedicated shareholder. It returns `200` and the dedicated member UUID.
