# Independent Standards Review

The Standards agent reviewed `git diff 8b1af41...HEAD` against Ralph's decision/quality rules and
the cited auth, API, data-model, codebase-design, and frontend standards.

Material results:

- High: 006Z13's actorless-calculation guard asserts exact source filenames/strings, while the new
  `calculate_for_actor` has no production caller. This is not interface-level security proof.
- Medium: 007A4 proves one PostgreSQL winner but uses counts instead of complete effective/history/
  audit/case state equality for the claimed zero-write loser.
- Low judgment: proposal reader authority remains locally duplicated rather than centralized.
- Low judgment: CR-003 retains a `userEvent.type` invocation-count spy in addition to observable
  HTTP/readback assertions.

The agent also identified empty production case snapshot fields. Root reconciliation confirmed the
Epic 007 digest explicitly assigns population of the pre-existing 006G shell to 007B; 007B was
sharpened so empty shells are never routable and acceptance must traverse the real case interface.

