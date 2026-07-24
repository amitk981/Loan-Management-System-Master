# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root performance_readiness has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 349
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/performance_readiness/__init__.py`
- `sfpcl_credit/performance_readiness/local.py`
- `sfpcl_credit/performance_readiness/matrix.py`
- `sfpcl_credit/performance_readiness/probes.py`
- `sfpcl_credit/performance_readiness/runner.py`
- `sfpcl_credit/performance_readiness/timed_runner.py`
- `sfpcl_credit/shared/management/commands/performance_readiness.py`
- `sfpcl_credit/tests/test_performance_readiness.py`

Impacted test labels:
- `sfpcl_credit.tests.test_performance_readiness`
