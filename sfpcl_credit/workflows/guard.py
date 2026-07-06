from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TransitionDefinition:
    entity_type: str
    action_code: str
    from_states: frozenset[str]
    to_state: str
    required_permission: str
    audit_action: str
    workflow_name: str
    workflow_label: str = ""


@dataclass(frozen=True)
class TransitionResult:
    previous_state: str
    next_state: str
    definition: TransitionDefinition


class WorkflowTransitionError(Exception):
    pass


class UnknownTransitionAction(WorkflowTransitionError):
    def __init__(self, action_code: str):
        self.action_code = action_code
        super().__init__(f"Unknown workflow action {action_code}.")


class MissingTransitionPermission(WorkflowTransitionError):
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
        super().__init__(f"Permission {required_permission} is required.")


class InvalidStateTransition(WorkflowTransitionError):
    def __init__(
        self,
        current_state: str,
        allowed_states: frozenset[str],
        definition: TransitionDefinition,
    ):
        self.current_state = current_state
        self.allowed_states = allowed_states
        self.definition = definition
        super().__init__(_state_error_message(current_state, allowed_states))


def evaluate_transition(
    *,
    current_state: str,
    requested_action: str,
    actor_permissions: Iterable[str],
    transitions: Iterable[TransitionDefinition],
) -> TransitionResult:
    transition = _find_transition(requested_action, transitions)
    permissions = set(actor_permissions)
    if transition.required_permission not in permissions:
        raise MissingTransitionPermission(transition.required_permission)
    if current_state not in transition.from_states:
        raise InvalidStateTransition(current_state, transition.from_states, transition)
    return TransitionResult(
        previous_state=current_state,
        next_state=transition.to_state,
        definition=transition,
    )


def _find_transition(
    requested_action: str, transitions: Iterable[TransitionDefinition]
) -> TransitionDefinition:
    for transition in transitions:
        if transition.action_code == requested_action:
            return transition
    raise UnknownTransitionAction(requested_action)


def _state_error_message(current_state: str, allowed_states: frozenset[str]) -> str:
    if len(allowed_states) == 1:
        return f"Expected status {next(iter(allowed_states))}, found {current_state}."
    expected = ", ".join(sorted(allowed_states))
    return f"Expected one of statuses {expected}, found {current_state}."
