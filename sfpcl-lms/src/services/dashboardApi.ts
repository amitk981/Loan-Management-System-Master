import {
  API_BASE_URL,
  AuthSessionError,
  loadStoredAuthSession,
} from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: Record<string, unknown>;
  };
}

export type DashboardRoleContext =
  | 'credit_manager'
  | 'sanction_committee'
  | 'compliance'
  | 'treasury'
  | 'management';

export interface DashboardCard {
  code: string;
  label: string;
  count: number;
  link: string;
}

export interface DashboardTask {
  task_type: string;
  entity_id: string;
  title: string;
  due_at?: string | null;
}

export interface DashboardSummary {
  role_context: DashboardRoleContext;
  cards: DashboardCard[];
  tasks: DashboardTask[];
}

export const fetchDashboardSummary = async (): Promise<DashboardSummary> => {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
    },
  });
  const envelope = await response.json() as ApiEnvelope<DashboardSummary>;

  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }

  return normalizeDashboardSummary(envelope.data);
};

const normalizeDashboardSummary = (summary: DashboardSummary): DashboardSummary => ({
  role_context: summary.role_context,
  cards: Array.isArray(summary.cards)
    ? summary.cards.map(card => ({
        code: String(card.code ?? ''),
        label: String(card.label ?? ''),
        count: Number.isFinite(Number(card.count)) ? Number(card.count) : 0,
        link: String(card.link ?? ''),
      }))
    : [],
  tasks: Array.isArray(summary.tasks)
    ? summary.tasks.map(task => ({
        task_type: String(task.task_type ?? ''),
        entity_id: String(task.entity_id ?? ''),
        title: String(task.title ?? ''),
        due_at: task.due_at ?? null,
      }))
    : [],
});
