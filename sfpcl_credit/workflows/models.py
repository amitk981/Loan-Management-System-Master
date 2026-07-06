import uuid

from django.db import models
from django.utils import timezone


class WorkflowEvent(models.Model):
    workflow_event_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    workflow_name = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    from_state = models.CharField(max_length=100, blank=True, null=True)
    to_state = models.CharField(max_length=100, db_index=True)
    triggered_by_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT
    )
    trigger_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "workflow_events"
        ordering = ["created_at"]
