# Masked HTTP Contract Examples

- Individual registration: exactly one authenticated `POST /api/v1/members/`, followed by exactly
  one canonical `GET /api/v1/members/{member_id}/`; readback asserts masked PAN and Aadhaar.
- Ordinary correction: exactly one versioned `PATCH /api/v1/members/{member_id}/`, followed by one
  canonical detail GET; the corrected server heading is rendered from that readback.
- Institution registration: exactly one authenticated create POST with all producer-profile fields,
  no individual profile/Aadhaar fields, followed by one canonical detail GET and masked PAN.
- Protected correction: requester makes one POST to the member identity-change collection and sees
  no approval action. A separately authenticated checker consumes the enabled projected action,
  makes one approval POST, refetches canonical detail, and sees only the masked corrected PAN.

Generated folio and identity values are intentionally omitted from evidence.
