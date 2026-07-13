# Independent Standards Axis

- Critical: `conflict_of_interest.py` can satisfy a two-Director rule with one duplicated Director,
  contrary to auth §§16.2/27.1, security §12, and codebase-design §13.1.
- High: `approval_case_engine.py` joins action history only to original required snapshots, so a
  successful alternate approval is absent from canonical public history (API §25.4).
- High (root reviewer probe): the committee-wide helper index leaks ordinary-list counts to an
  unused alternate before the Python object check (auth §§32.1/37.3).
- Medium judgment: `ApprovalCase.save()` hides engine evaluation and cross-table projection writes,
  creating cyclic ownership and weak locality under codebase-design §§42.1-42.2.

Migration-local duplication, communication writes inside the outer action transaction, and the
explicitly deferred relationship writer were reviewed and not classified as findings.
