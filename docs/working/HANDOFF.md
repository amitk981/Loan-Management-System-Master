# Ralph Handoff

## Last Run
2026-07-12_214611_normal_run

## Current Status

006Z4 is complete. The public active-member module now calculates one deterministic dated projection,
stops financial-year continuity at gaps, excludes not-yet-complete years without hiding them, covers
individual/institution/service/recorded-relaxation routes, and owns governed result verification.
Credit stores the exact complete row/result snapshot used by eligibility; portal supply exposes the
same row classification and dated summary without member IDs or staff actions.

## Validation

Evidence is under `.ralph/runs/2026-07-12_214611_normal_run/`. Frontend build/typecheck/lint and 199
tests pass. Backend check/migration sync and 460 tests pass (8 expected SQLite skips) at 93% coverage;
the added verification-route test also passes. The new PostgreSQL active-status race and the existing
five-credit-race suite each pass twice with zero skips and exact winner/loser evidence assertions.

## Next Run

An architecture review is due after four completed slices. After that review, run sharpened 006Z2;
its portal limit projection must consume 006Z4's verified dated result/snapshot and strip internal
row/evidence/authority facts.
