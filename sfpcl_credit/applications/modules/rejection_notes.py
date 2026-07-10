"""Public module seam for rejection-note draft creation."""

from dataclasses import dataclass

from sfpcl_credit.applications import services


class RejectionNoteValidationError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Rejection note payload failed validation.")


class RejectionNoteInvalidStateError(Exception):
    pass


@dataclass(frozen=True)
class RejectionNoteResult:
    snapshot: dict


class RejectionNoteModule:
    """Expose rejection-note behavior without leaking its model or legacy service errors."""

    def create_credit_draft(
        self,
        *,
        application,
        payload,
        actor,
        request_ip="",
        request_user_agent="",
        request_id=None,
    ):
        try:
            note = services.create_credit_rejection_note(
                application,
                payload,
                actor,
                request_ip=request_ip,
                request_user_agent=request_user_agent,
                request_id=request_id,
            )
        except services.LoanApplicationValidationError as exc:
            raise RejectionNoteValidationError(exc.field_errors) from exc
        except services.LoanApplicationInvalidStateError as exc:
            raise RejectionNoteInvalidStateError(str(exc)) from exc
        return RejectionNoteResult(snapshot=services.serialize_rejection_note(note))
