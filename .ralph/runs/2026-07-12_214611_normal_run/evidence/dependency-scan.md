# Dependency scan

`credit/modules/eligibility_assessment.py` imports only the public
`members.modules.active_member_status.ActiveMemberStatusModule` interface for active-member facts.
It has no member-model, produce-supply-model, member-service, continuity, service-year, or row-
classification implementation. Portal supply likewise consumes the public result projection.

The existing loan-limit module's member model imports are outside this slice and remain the
documented calculator's persisted input seam.
