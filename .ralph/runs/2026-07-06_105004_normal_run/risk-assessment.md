# Risk Assessment

Selected slice: `003I-notification-adapter-shell`

Risk level: Medium

## Why
- Adds one new backend table (`communications`) and two protected API endpoints.
- Touches authorization, template rendering, audit logging, and source communication metadata.
- Does not send real communications, call external providers, alter money/business calculations, or change frontend behavior.

## Controls
- TDD red/green captured:
  - Red: `evidence/terminal-logs/communications-red.log`
  - Green: `evidence/terminal-logs/communications-green.log`
- All send/list routes require session-bound bearer auth and narrow communication permissions.
- Failed auth, permission, validation, inactive/unapproved template, and bad query requests do not write `Communication` or communication audit rows.
- Audit metadata excludes rendered subject/body snapshots, merge data, provider credentials, and secrets.
- Delivery remains `pending`; no email, SMS, courier, phone, in-app notification, or provider call is performed.

## Residual Risk
- A-025 records that exact communication read/send permission codes are source-catalogue assumptions until the source docs add §12 entries or a dedicated Communication role.
- A-025 also records deterministic merge behavior: extra `merge_data` keys are rejected, not ignored.
- Notification Center read/unread/action state remains deferred to `003IA`; `communications` is not overloaded with those fields.

Manual review required: normal Ralph review only.
