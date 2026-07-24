import {
  AuthSessionError,
  authenticatedPaginatedRequest,
  authenticatedRequest,
  type PaginatedResult,
} from './authSession';

export type TaskType =
  | 'completeness_check'
  | 'appraisal'
  | 'sanction'
  | 'document_verification'
  | 'sap_setup'
  | 'disbursement'
  | 'repayment_posting'
  | 'default_review';

export type TaskPriority = 'normal' | 'high' | 'critical';

export interface TaskActionAvailability {
  action_code: string;
  label: string;
  enabled: boolean;
  disabled_reason?: string | null;
  required_permission?: string;
}

export interface WorkflowTaskRow {
  task_id: string;
  task_reference: string;
  task_type: TaskType;
  title: string;
  application_or_loan_id: string;
  linked_entity_type: string;
  borrower: string;
  borrower_type: string;
  amount: string | null;
  priority: TaskPriority;
  sla_tat: {
    due_at: string | null;
    overdue_days: number;
  };
  current_status: string;
  assigned_to: {
    role_code: string;
    team_code: string | null;
    user: null | {
      user_id: string;
      full_name: string;
    };
  };
  blocked: boolean;
  blocked_reason: string | null;
  special_case: boolean;
  exception_required: boolean;
  created_date: string;
  due_date: string | null;
  closed_at: string | null;
  action: {
    code: 'open';
    url: string;
  };
  available_actions?: TaskActionAvailability[];
}

export interface TaskInboxQuery {
  page?: number;
  pageSize?: number;
  taskType?: TaskType;
  dueToday?: boolean;
  overdue?: boolean;
  borrowerType?: string;
  minimumAmount?: string;
  specialCase?: boolean;
  exceptionRequired?: boolean;
  assignedToUserId?: string;
  assignedToMyTeam?: boolean;
}

export const fetchTaskInbox = async (
  query: TaskInboxQuery = {},
): Promise<PaginatedResult<WorkflowTaskRow>> => {
  const params = new URLSearchParams();
  params.set('page', String(query.page ?? 1));
  params.set('page_size', String(query.pageSize ?? 20));
  if (query.taskType) params.set('task_type', query.taskType);
  if (query.dueToday) params.set('due_today', 'true');
  if (query.overdue) params.set('overdue', 'true');
  if (query.borrowerType) params.set('borrower_type', query.borrowerType);
  if (query.minimumAmount) params.set('minimum_amount', query.minimumAmount);
  if (query.specialCase) params.set('special_case', 'true');
  if (query.exceptionRequired) params.set('exception_required', 'true');
  if (query.assignedToUserId) params.set('assigned_to_user_id', query.assignedToUserId);
  if (query.assignedToMyTeam) params.set('assigned_to_my_team', 'true');
  const result = await authenticatedPaginatedRequest<WorkflowTaskRow>(
    `/api/v1/tasks/?${params.toString()}`,
  );
  return {
    ...result,
    items: result.items.map(normalizeTask),
  };
};

export const submitTaskAction = (
  taskId: string,
  action: 'reassign' | 'comments' | 'block' | 'unblock',
  payload: Record<string, string> = {},
): Promise<WorkflowTaskRow> => authenticatedRequest<WorkflowTaskRow>(
  `/api/v1/tasks/${taskId}/${action}/`,
  { method: 'POST', body: payload },
).then(normalizeTask);

const TASK_TYPES = new Set<TaskType>([
  'completeness_check',
  'appraisal',
  'sanction',
  'document_verification',
  'sap_setup',
  'disbursement',
  'repayment_posting',
  'default_review',
]);
const LINKED_ENTITY_TYPES = new Set(['loan_application', 'loan_account']);
const PRIORITIES = new Set<TaskPriority>(['normal', 'high', 'critical']);

const normalizeTask = (value: unknown): WorkflowTaskRow => {
  if (!value || typeof value !== 'object') {
    throw new AuthSessionError(
      'MALFORMED_RESPONSE',
      'The server returned an invalid task row.',
      502,
    );
  }
  const row = value as Record<string, unknown>;
  const assigned = row.assigned_to as Record<string, unknown> | undefined;
  const sla = row.sla_tat as Record<string, unknown> | undefined;
  const openAction = row.action as Record<string, unknown> | undefined;
  const assignedUser = assigned?.user as Record<string, unknown> | null | undefined;
  const optionalDate = (field: unknown) => field === null || typeof field === 'string';
  if (
    !nonblank(row.task_id)
    || !nonblank(row.task_reference)
    || !TASK_TYPES.has(row.task_type as TaskType)
    || !nonblank(row.title)
    || !nonblank(row.application_or_loan_id)
    || !nonblank(row.linked_entity_type)
    || !LINKED_ENTITY_TYPES.has(row.linked_entity_type)
    || typeof row.borrower !== 'string'
    || typeof row.borrower_type !== 'string'
    || !(row.amount === null || typeof row.amount === 'string')
    || !PRIORITIES.has(row.priority as TaskPriority)
    || !sla
    || !optionalDate(sla.due_at)
    || !Number.isInteger(sla.overdue_days)
    || (sla.overdue_days as number) < 0
    || !nonblank(row.current_status)
    || !assigned
    || !nonblank(assigned.role_code)
    || !(assigned.team_code === null || typeof assigned.team_code === 'string')
    || !(assignedUser === null || (
      assignedUser
      && nonblank(assignedUser.user_id)
      && nonblank(assignedUser.full_name)
    ))
    || typeof row.blocked !== 'boolean'
    || !(row.blocked_reason === null || typeof row.blocked_reason === 'string')
    || typeof row.special_case !== 'boolean'
    || typeof row.exception_required !== 'boolean'
    || !nonblank(row.created_date)
    || !optionalDate(row.due_date)
    || !optionalDate(row.closed_at)
    || !openAction
    || openAction.code !== 'open'
    || !nonblank(openAction.url)
    || !(row.available_actions === undefined || validActions(row.available_actions))
  ) {
    throw new AuthSessionError(
      'MALFORMED_RESPONSE',
      'The server returned an invalid task row.',
      502,
    );
  }
  return value as WorkflowTaskRow;
};

const validActions = (value: unknown) => Array.isArray(value) && value.every(action => {
  if (!action || typeof action !== 'object') return false;
  const item = action as Record<string, unknown>;
  return nonblank(item.action_code)
    && nonblank(item.label)
    && typeof item.enabled === 'boolean'
    && (item.disabled_reason === undefined || item.disabled_reason === null || typeof item.disabled_reason === 'string');
});

const nonblank = (value: unknown): value is string => typeof value === 'string' && value.length > 0;
