"""Pinned async-worker entry points; business policy stays in deep modules."""

from celery import shared_task

from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.communication_delivery import (
    execute_communication_job,
)


@shared_task(name="communications.execute_job")
def execute_communication_delivery_job(job_id):
    execute_communication_job(job_id)
    evidence = CommunicationDispatcher.job_evidence(job_id=job_id, limit=1)[0]
    return _task_evidence(evidence)


@shared_task(name="communications.dispatch_due_jobs")
def dispatch_due_communication_jobs():
    results = []
    for job_id in CommunicationDispatcher.retry_failed():
        results.append(execute_communication_delivery_job(job_id))
    blocked_ids = {item["communication_job_id"] for item in results}
    for evidence in CommunicationDispatcher.job_evidence():
        if (
            evidence["status"] == "operator_blocked"
            and evidence["communication_job_id"] not in blocked_ids
        ):
            results.append(_task_evidence(evidence))
    return results


def _task_evidence(evidence):
    return {
        "communication_job_id": evidence["communication_job_id"],
        "delivery_status": evidence["status"],
        "attempts": evidence["attempts"],
        "max_attempts": evidence["max_attempts"],
        "next_attempt_at": evidence["next_attempt_at"],
        "last_failure_code": evidence["last_failure_code"],
        "recovered": evidence["recovered"],
        "operator_attention_required": evidence["operator_attention_required"],
    }


__all__ = [
    "dispatch_due_communication_jobs",
    "execute_communication_delivery_job",
]
