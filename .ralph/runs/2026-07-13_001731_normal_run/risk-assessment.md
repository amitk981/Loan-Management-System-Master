# Risk Assessment

Risk: High. This slice changes eligibility evidence provenance, permissions, effective history, and
concurrency. Controls: public-interface TDD, atomic row locks, forward-only dates, zero new schema or
dependencies, full gates, and two authoritative PostgreSQL race runs. Residual risk is limited to
future evidence mutation APIs, which must preserve the same member/evidence lock order.
