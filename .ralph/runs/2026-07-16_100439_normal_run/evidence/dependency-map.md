# 008M4 Dependency Map

## Before

`staff_documentation_workspace` owned queue scanning, cross-domain prerequisite queries, action URL
and payload construction, action-code dispatch, concrete exception translation, and DTO assembly.
The documentation frontend independently loaded the session and implemented JSON/multipart/blob
transport.

## After

```text
views
  -> staff_documentation_workspace (composition, locked read, DTO, opaque HMAC)
       -> staff_documentation_queue (approval-scoped count/page before projection)
       -> legal_documents.staff_workspace_actions
            -> legal/checklist/template/signature/stamp/document owners
            <- injected cross-domain checklist gateways
       -> applications.staff_workspace_actions -> bank_verification owner
       -> security_instruments.staff_workspace_actions
            <- legal-issued prerequisite facts
            <- injected atomic security creation gateways

DocumentationHub -> documentationWorkspaceApi (DTO mapping)
  -> authSession authenticated JSON/pagination/multipart/blob transport
```

Owner modules do not import process coordinators. The process composition root contains no owner
action executor, action-code dispatcher, URL-derived identifier parser, request contract, or
concrete owner exception vocabulary. Approval read scope and terminal sanctioned amount are issued
by approval-owned modules.
