# Exact Event Identity Evidence

The API regression proves:

```text
submit.data.workflow_event_id
  == approval_case.workflow_event_id
  == workflow_event.workflow_event_id
  == reload.data.workflow_event_id
```

The PostgreSQL duplicate-submission race also proves the winner response, stored case, and only
committed event share the same UUID, exact states and reason, with no loser evidence.
