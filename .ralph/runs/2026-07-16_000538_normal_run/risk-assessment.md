# Risk Assessment

Risk: High / unacceptable for merge.

The attempted frontend projection derives applicability, blockers, workflow state, and download
authority from three independent reads. That violates the slice's locked-snapshot and
server-issued-capability requirements and could expose stale or unauthorized download controls.
It also suppresses security API failures as business state and omits required mutations. The
working tree is intentionally not marked complete and must remain quarantined for repair.

