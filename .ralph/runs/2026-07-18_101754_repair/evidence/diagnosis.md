# Diagnosis

- Symptom: both historical credit-model ownership migration cases raised `LookupError` for
  `applications.EligibilityAssessment` during fixture setup.
- Tight loop: the single forward migration test reproduced the error deterministically in about
  25 seconds.
- Confirmed hypothesis: `legal_documents.0015` is a current leaf whose disbursement/communications
  dependencies include current credit state. The historical test projected that leaf even after
  migrating the database to its pre-move targets.
- Falsified hypotheses: migration state caching and a state-mutating 0015 operation. The migration
  is operation-free, and directly excluding the legal leaf restores both historical assessment
  models in a fresh projection.
- Fix: treat `legal_documents` as another downstream owner leaf in this retained historical test.
- Prevention: historical migration tests must exclude every downstream leaf that can transitively
  outrun their target state; the explanatory list now names the legal owner explicitly.
