# MP14 Safe-Error Diagnosis

## Independent failure

The retained trusted-browser log from run `2026-07-19_012341_repair` proves:

- real Django login, application listing, explicit selection, and detail loading completed;
- the processing and accepted-advice browser cases passed and produced their screenshots;
- only the HTTP 503 case failed because the expected safe message was absent;
- the missing screenshot was only `mp14-safe-error.png`.

The exact browser assertion waited for:

```text
Disbursement status could not be loaded. Please try again.
```

## Root cause

The shared portal client converts a non-success envelope into an `AuthSessionError` carrying the
server's message. MP14 correctly overrides 401 and 403 with tailored borrower copy, but returned
`error.message` for every other `AuthSessionError`. The trusted browser's 503 envelope therefore
rendered `Unavailable.` instead of the safe MP14 fallback.

The previous unit test rejected with a plain `Error('offline')`, so it did not reproduce the real
shared-client error shape. Replacing that fixture with
`AuthSessionError('SERVICE_UNAVAILABLE', 'Unavailable.', 503)` made the focused test fail with the
same rendered DOM as the trusted browser.

## Minimal repair

MP14 now returns the existing operation-specific fallback for every `AuthSessionError` except the
deliberately tailored 401 and 403 messages. The regression asserts both that the safe copy appears
and that `Unavailable.` does not.
