# Architecture Defect Probes

Four corrected behaviors pass together:

1. transfer-success exact replay uses API §45.2's retained-original wrapper;
2. changed rendered advice content makes replay conflict;
3. changed canonical member email makes historical-recipient replay conflict;
4. CFC-only advice authority is denied while canonical Credit Manager scope succeeds.

The historical CFC probe assumed the old fixture actor was still CFC; 009H2 correctly changed that
fixture to the source-authorised Senior Finance maker. The production public role-matrix test is the
stronger replacement and additionally proves Credit Manager and effective multi-role behavior.

Combined output: `terminal-logs/architecture-probes-credit-manager.log`.

