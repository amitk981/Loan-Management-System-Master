# Exact-Candidate Gate Snapshot

Candidate: `767b1f29c4dae0634a8af8c01513f57ec81dedef`

Produced by the Ralph independent validator for source run `2026-07-25_123004_normal_run`.
This bounded snapshot retains the decision facts and original artifact hashes needed by 012I.

| Gate | Result | Counts | Original SHA-256 |
|---|---|---|---|
| Authoritative backend lane | PASS | Full lane | `cfcbc4e59224819bce8e5e5e2bf7cf4ea59530044bc285accc20270de000d51e` |
| Backend tests/coverage | PASS | 1,889 total; 176 skipped; zero failures; 90% | `e63eda7307d0514a935f4af71cb8e9e9b74a51d64befa775295da02e0434c09e` |
| Frontend tests | PASS | 515 passed; 64 files; zero failures/skips | `b911bc46299e2c1108bc348d229b51f42c27e6ebb885483d45be84548afe82e4` |
| Frontend production build | PASS | Exit zero | `dc70a7ed413d3a5059db09d400421f1d34f895e175a9fb12c50948d05d97e8b3` |
| Migration drift | PASS | No changes detected | `6ffa22aaa087232bf570dcd8a36e38183a5d828b3cce18ba53175c32783593ed` |

The backend skips are not classified here as mandatory or authorised, so this snapshot does not
claim source-defined P0/full-regression acceptance.
