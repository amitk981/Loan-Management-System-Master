# Notification Contract and Mock-Removal Proof

## Bounded summary request

- Header request: `GET /api/v1/notifications/?read_status=unread&page_size=4`.
- Badge source: response pagination `total_count`.
- Rows: response data only, in backend order, with title, message, severity, timestamp, id, and
  `read_state_version` retained from the API.
- Verified by `NotificationsCenter.test.tsx` exact URL/header assertion and
  `Header.notifications.test.tsx` bounded-summary assertion.

## Versioned mark-read request

- URL: `POST /api/v1/notifications/notif-1/mark-read/`.
- Body: `{ "read_state_version": 1 }`.
- Header behavior: calls the service with `("notif-1", 1)` and refreshes the unread summary after
  success or `409 STALE_WRITE`.
- Verified by the existing exact URL/body API-client assertion plus the new header success and
  stale-refresh tests.

## Final mock removal

`Header.notifications.test.tsx` reads `Header.tsx` as source and asserts that it contains none of:

- `mockData`
- `const notifications = [`
- `Sanction approval required`
- `Appraisal TAT will breach`

The direct repository search also returned no match for those strings in `Header.tsx`.
