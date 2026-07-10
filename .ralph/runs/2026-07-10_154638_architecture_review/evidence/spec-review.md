# Independent Spec Review

## Finding 1 — High — Implemented-looking wrong owner state

005I4 requires `assigned_owner` to be backend-owned or neutral and forbids role/status inference;
API §19.1 models it as an explicit assignment. `serialize_application_detail()` instead derives it
from `received_by_user or created_by_user`. A portal-created application can therefore show the
borrower as staff's current internal owner. Backend coverage asserts only the derived owner, while
the later-stage frontend regression injects an arbitrary DTO rather than proving backend ownership.

## Finding 2 — Medium — Portal nominee detail is partial

005I3 requires ID, name, age, minor/KYC/relationship/signature facts on portal detail. The DTO
contains them, but MP10 renders neither nominee ID nor minor/adult status. New frontend coverage
tests only selector views, not portal detail.

## Finding 3 — Medium / Watch — Configuration seam acceptance wording is unproven for eligibility

006D2A says the configuration resolver is the only effective-policy query seam and asks for an
eligibility-path regression. Eligibility itself does not query policy; only the legacy loan-limit
path does. The boundary test proves function identity rather than a call path. Because behavior
preservation forbids adding a new eligibility policy lookup, this is retained as a test/seam watch,
not a request to invent one. 006D2B must prove the actual calculator calls the public resolver with
locking and prevent direct policy queries.

No additional scope creep or formula regression was confirmed. 006C2 preserves the source-backed
lower-of-two formula and explicit A-049 blocker; 006D2A preserves eligibility payload, permissions,
object access, rerun, and transaction behavior.
