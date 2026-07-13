# Sanction Handoff Dependency Graph

```text
applications HTTP adapter -> approvals.modules.sanction_handoff
approvals.modules.sanction_handoff -> credit.modules.appraisal_workflow (public interface)
approvals.modules.sanction_handoff -> applications.services (object access)
credit.modules.* -> domain_errors
approvals.modules.* -> domain_errors

credit -X-> approvals
approvals -X-> credit.modules.common
```

The static AST regression scans every production Python file, including aliased and package
imports, and enforces both rejected edges.
