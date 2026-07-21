# Impact Analysis

Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`

## Demonstrated validation domain

The prior run passed its focused slice gates and PostgreSQL acceptance but failed one independent
complete-suite regression in the generic communications worker. After a fake adapter accepts the
final allowed attempt, a simulated crash during post-acceptance payload verification leaves
`CommunicationDeliveryJob.provider_external_message_id` empty. This violates the retained-provider
evidence and no-redispatch contract.

## Affected backend pieces

- `sfpcl_credit/communications/modules/communication_dispatcher.py`: generic worker execution,
  provider acceptance persistence, and final-attempt exception transition.
- `sfpcl_credit/tests/test_communication_worker_runtime.py`: existing permanent regression at the
  public worker seam; no new test module is needed unless minimisation exposes a missing assertion.
- `CommunicationDeliveryJob`, `CommunicationProviderAttempt`, and `CommunicationException` retained
  state are in the blast radius, but schema/model changes are not expected.

## Frontend impact

None. The failed validator is entirely within the backend communication worker runtime. No frontend
file or visual behavior is in scope for this repair.

## Blast radius and regression coverage

- External side-effect integrity: accepted provider evidence must survive a local post-send crash so
  the provider is never called a second time.
- Retry/finalisation integrity: exhausted jobs still become failed with one operator exception; the
  accepted provider identity must not incorrectly mark the communication sent.
- Transaction integrity: a fix must not weaken rollback semantics before the provider call or alter
  ordinary successful delivery.
- Focused regression: rerun the exact failed test, then the complete
  `sfpcl_credit.tests.test_communication_worker_runtime` module to cover success, non-final crash,
  final crash, retry, exception, and worker claim paths.

## Scope controls

- Fix only the demonstrated communications-worker transaction/evidence boundary.
- Do not alter reminder, MIS, direct repayment, statement, portal, frontend, or slice contracts.
- Do not introduce communication cadence/content, retry-limit, or provider policy.
