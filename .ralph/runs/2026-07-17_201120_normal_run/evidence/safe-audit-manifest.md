# Safe Advice Audit Manifest

The protected `communications` row retains the normalized full recipient address because the email
adapter requires it for delivery. General `disbursement.advice_sent` audit evidence retains only:

- protected communication, disbursement, loan, application, and member UUIDs;
- template id/code/version;
- masked recipient (`b***@example.com`) and SHA-256 recipient digest;
- channel, provider message id, provider status, and accepted time;
- safe amount, masked bank reference, transfer action id, and transfer evidence digest;
- actor user id, source-authorised role, active team codes, request id, IP, user agent, and outcome.

The workflow trigger contains only action, communication, and request ids. Neither general ledger
contains the full email or full UTR. The public response contains only disbursement id, the stable
communication id, delivery status, and UTC sent time.

Verified by `test_send_consumes_stable_pending_identity_and_keeps_ledgers_recipient_safe` and the
success/no-financial-side-effects test.

