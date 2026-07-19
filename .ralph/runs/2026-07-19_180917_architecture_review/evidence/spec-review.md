# Spec Review

Fixed product boundaries: `399fb954..50d91369` (009L6) and
`d17954b8..fe4b0ecb` (CR-012). Ralph infrastructure and mechanical bookkeeping
were excluded.

1. **High — 009L6 remains partial:** requirement 1 says scalar and selector consume the same
   immutable decision; requirement 2 names send/file/completion/actor/readiness/aggregate drift;
   requirement 4 retains role/object scope. Completion selection omits the send owner, S37
   selection omits actual workbook integrity, and CFC selection omits scalar frozen-owner facts.
   Such rows remain count-visible and then disappear during projection.
2. **High — implemented behavior weakens the binding read contract:** requirement 4 preserves
   authority behind its owner, while auth §34.7 and `API_CONTRACTS.md` require
   `finance.loan_account.read`. 009L6 substitutes initiation permission and grants portfolio-wide
   public reads.
3. **Medium — the executable matrix remains incomplete:** requirement 5 explicitly requires mixed
   1/21/101 rows, >4 adjacent drifts, page boundaries, every scalar component/consumer,
   action/mutation parity, query ceilings, and independent error surfaces for all five branches.
   The new tests are principally one-row examples; only Loan Accounts retain 21/101 coverage.

CR-012 passes its targeted Spec axis: the diff removes owned-API routing/token injection, every
capture follows state assertions, both trusted runs retain nine valid PNGs with nine distinct
matching hashes, and guard/idempotency tests exercise the isolated real-Django seed.
