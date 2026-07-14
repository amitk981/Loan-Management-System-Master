import { Role } from '../types';
import type { Permission } from '../contexts/RoleContext';

const AUTH_STORAGE_KEY = 'sfpcl_staff_auth_session';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export const DEMO_AUTH_ENABLED = import.meta.env.VITE_ENABLE_DEMO_AUTH === 'true';

export interface AuthSession {
  accessToken: string;
  refreshToken: string;
}

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  pagination?: Pagination;
  response_status?: number;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: Record<string, unknown>;
  };
}

export interface Pagination {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedResult<T> {
  items: T[];
  pagination: Pagination;
}

interface LoginData {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: unknown;
}

export interface BackendRole {
  role_code: string;
  role_name: string;
}

export interface BackendTeam {
  team_code: string;
  team_name: string;
}

export interface BackendCurrentUser {
  user_id: string;
  full_name: string;
  email: string;
  mobile_number?: string;
  status: string;
  roles: BackendRole[];
  teams: BackendTeam[];
  role_codes?: string[];
  team_codes?: string[];
  permissions: string[];
  available_actions: string[];
  member_id?: string;
  portal_account_id?: string;
  portal_role?: string;
  member_display_name?: string;
}

export interface FrontendCurrentUser {
  id: string;
  name: string;
  email: string;
  mobileNumber?: string;
  status?: string;
  role: Role;
  roleName: string;
  team?: string;
  teamName?: string;
  roleCodes: string[];
  teamCodes: string[];
  permissions: string[];
  availableActions: string[];
  memberId?: string;
  portalAccountId?: string;
  portalRole?: string;
  memberDisplayName?: string;
}

export interface PortalActivationStartResult {
  challengeId: string;
  maskedContact?: string;
  expiresAt?: string;
}

export interface PortalAccountResult {
  memberId: string;
  status: string;
}

export class AuthSessionError extends Error {
  code: string;
  status?: number;
  fieldErrors?: Record<string, string>;
  details?: Record<string, unknown>;

  constructor(code: string, message: string, status?: number, fieldErrors?: Record<string, string>, details?: Record<string, unknown>) {
    super(message);
    this.name = 'AuthSessionError';
    this.code = code;
    this.status = status;
    this.fieldErrors = fieldErrors;
    this.details = details;
  }
}

const ROLE_CODE_TO_FRONTEND_ROLE: Record<string, Role> = {
  field_officer: 'field_officer',
  deputy_manager_finance: 'deputy_manager_finance',
  credit_manager: 'credit_manager',
  compliance_team_member: 'compliance_team',
  company_secretary: 'company_secretary',
  senior_manager_finance: 'senior_manager_finance',
  chief_financial_controller: 'cfc',
  cfo: 'cfo',
  director: 'director',
  accounts_head: 'accounts',
  sales_team_user: 'sales_team_user',
  it_head: 'backend_staff',
  internal_auditor: 'auditor',
  system_admin: 'admin',
  management_viewer: 'backend_staff',
  borrower_portal_user: 'borrower',
  nominee: 'backend_staff',
  bank_user: 'backend_staff',
  subsidiary_user: 'backend_staff',
  external_auditor: 'backend_staff',
};

export const CANONICAL_TO_PROTOTYPE_PERMISSIONS: Record<string, Permission> = {
  'applications.loan_application.read': 'view_applications',
  'applications.loan_application.create': 'create_application',
  'applications.loan_application.update': 'edit_application',
  'applications.loan_application.complete_check': 'do_completeness_check',
  'members.member.read': 'view_members',
  'members.member.create': 'edit_members',
  'members.member.update': 'edit_members',
  'credit.appraisal.create': 'do_appraisal',
  'credit.appraisal.update': 'do_appraisal',
  'credit.appraisal.review': 'do_appraisal',
  'approvals.case.read': 'view_sanction',
  'approvals.case.create': 'view_sanction',
  'approvals.case.approve': 'approve_sanction',
  'approvals.case.reject': 'reject_sanction',
  'approvals.sanction.read': 'view_sanction',
  'approvals.sanction_register.read': 'view_approval_registers',
  'approvals.exception_register.read': 'view_approval_registers',
  'approvals.matrix.read': 'view_approval_matrix',
  'approvals.matrix.manage': 'view_approval_matrix',
  'documents.loan_document.read': 'view_documentation',
  'documents.loan_document.generate': 'manage_documentation',
  'documents.loan_document.verify': 'manage_documentation',
  'documents.checklist.read': 'view_documentation',
  'documents.checklist.update': 'manage_documentation',
  'documents.checklist.approve_credit': 'approve_credit_checklist',
  'documents.checklist.approve_cs': 'manage_documentation',
  'documents.checklist.sign_disbursement_complete': 'initiate_disbursement',
  'finance.disbursement.readiness': 'initiate_disbursement',
  'finance.disbursement.initiate': 'initiate_disbursement',
  'finance.disbursement.authorise': 'authorise_disbursement',
  'finance.loan_account.read': 'view_loan_accounts',
  'finance.repayment.create': 'post_repayment',
  'finance.repayment.allocate': 'post_repayment',
  'finance.interest_invoice.create': 'manage_interest',
  'finance.interest_invoice.issue': 'manage_interest',
  'finance.accrual.create': 'manage_interest',
  'finance.accrual.bulk_generate': 'manage_interest',
  'monitoring.dpd.read': 'view_monitoring',
  'monitoring.dpd.calculate': 'view_monitoring',
  'monitoring.reminder.create': 'view_monitoring',
  'defaults.case.read': 'manage_defaults',
  'defaults.case.open': 'manage_defaults',
  'defaults.assessment.create': 'manage_defaults',
  'defaults.extension.grant': 'manage_defaults',
  'recovery.decision.create': 'approve_recovery',
  'closure.readiness.read': 'manage_closure',
  'closure.loan.close': 'manage_closure',
  'closure.noc.issue': 'manage_closure',
  'closure.archive.read': 'manage_closure',
  'closure.archive.create': 'manage_closure',
  'compliance.control.read': 'view_compliance',
  'compliance.control.manage': 'manage_compliance',
  'compliance.task.read': 'view_compliance',
  'compliance.task.update': 'manage_compliance',
  'compliance.evidence.submit': 'manage_compliance',
  'compliance.evidence.review': 'view_compliance',
  'compliance.section186.read': 'view_compliance',
  'compliance.nbfc_test.read': 'view_compliance',
  'reports.application_pipeline.read': 'view_reports',
  'reports.portfolio.read': 'view_reports',
  'reports.dpd.read': 'view_reports',
  'reports.compliance.read': 'view_reports',
  'reports.export': 'export_registers',
  'audit.audit_log.read': 'view_audit',
  'audit.workflow_event.read': 'view_audit',
  'audit.version_history.read': 'view_audit',
  'users.user.create': 'manage_users',
  'users.user.update': 'manage_users',
  'users.user.disable': 'manage_users',
  'users.role.read': 'view_settings',
  'users.role.create': 'manage_settings',
  'users.role.update': 'manage_settings',
  'users.permission.assign': 'manage_settings',
  'users.team.manage': 'manage_settings',
  'config.loan_policy.read': 'view_settings',
  'config.loan_policy.manage': 'manage_settings',
  'config.share_valuation.manage': 'manage_settings',
  'config.scale_of_finance.manage': 'manage_settings',
  'config.interest_rate.manage': 'manage_settings',
  'tracer.lifecycle.run': 'run_tracer',
};

export const mapCanonicalPermissions = (canonicalPermissions: string[]): Permission[] => {
  const mapped = new Set<Permission>();
  canonicalPermissions.forEach(permission => {
    const prototypePermission = CANONICAL_TO_PROTOTYPE_PERMISSIONS[permission];
    if (prototypePermission) mapped.add(prototypePermission);
  });
  return [...mapped];
};

export const mapBackendUserToFrontendUser = (user: BackendCurrentUser): FrontendCurrentUser => {
  const primaryRole = user.roles[0];
  const primaryTeam = user.teams[0];
  const roleCodes = user.roles.map(role => role.role_code);
  const teamCodes = user.teams.map(team => team.team_code);
  const mappedRole = primaryRole ? ROLE_CODE_TO_FRONTEND_ROLE[primaryRole.role_code] : undefined;

  return {
    id: user.user_id,
    name: user.full_name,
    email: user.email,
    mobileNumber: user.mobile_number,
    status: user.status,
    role: mappedRole ?? 'backend_staff',
    roleName: primaryRole?.role_name ?? 'Staff User',
    team: primaryTeam?.team_code,
    teamName: primaryTeam?.team_name,
    roleCodes,
    teamCodes,
    permissions: user.permissions,
    availableActions: user.available_actions,
    memberId: user.member_id,
    portalAccountId: user.portal_account_id,
    portalRole: user.portal_role,
    memberDisplayName: user.member_display_name,
  };
};

export const storedAuthSession = (session: AuthSession): void => {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
};

export const loadStoredAuthSession = (): AuthSession | null => {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as AuthSession;
    if (!parsed.accessToken || !parsed.refreshToken) return null;
    return parsed;
  } catch {
    clearStoredAuthSession();
    return null;
  }
};

export const clearStoredAuthSession = (): void => {
  localStorage.removeItem(AUTH_STORAGE_KEY);
};

const parseAuthenticatedEnvelope = async <T>(response: Response): Promise<ApiEnvelope<T>> => {
  let envelope: ApiEnvelope<T>;
  try { envelope = await response.json() as ApiEnvelope<T>; }
  catch { throw new AuthSessionError('MALFORMED_RESPONSE', 'The server returned an invalid response.', response.status); }
  if (!response.ok || !envelope.success || envelope.data === undefined) {
    const fieldErrors = envelope.error?.field_errors
      ? Object.fromEntries(Object.entries(envelope.error.field_errors).map(([field, value]) => [field, String(value)]))
      : undefined;
    throw new AuthSessionError(envelope.error?.code ?? 'REQUEST_FAILED', envelope.error?.message ?? 'Request failed.', response.status, fieldErrors, envelope.error?.details);
  }
  return { ...envelope, response_status: response.status };
};

const isValidPagination = (value: unknown, itemCount: number): value is Pagination => {
  if (!value || typeof value !== 'object') return false;
  const pagination = value as Record<string, unknown>;
  const integer = (field: string, minimum: number) =>
    Number.isInteger(pagination[field]) && (pagination[field] as number) >= minimum;
  if (
    !integer('page', 1)
    || !integer('page_size', 1)
    || !integer('total_count', 0)
    || !integer('total_pages', 1)
    || typeof pagination.has_next !== 'boolean'
    || typeof pagination.has_previous !== 'boolean'
  ) return false;

  const { page, page_size: pageSize, total_count: totalCount, total_pages: totalPages } = pagination as unknown as Pagination;
  const expectedPages = Math.max(1, Math.ceil(totalCount / pageSize));
  const firstItemOffset = (page - 1) * pageSize;
  const expectedItemCount = totalCount === 0
    ? 0
    : page < totalPages ? pageSize : totalCount - firstItemOffset;
  return totalPages === expectedPages
    && page <= totalPages
    && pagination.has_next === (page < totalPages)
    && pagination.has_previous === (page > 1)
    && itemCount === expectedItemCount;
};

const authenticatedHeaders = (accessToken: string, jsonBody = false): Record<string, string> => ({
  Accept: 'application/json',
  Authorization: `Bearer ${accessToken}`,
  'X-Request-ID': globalThis.crypto?.randomUUID?.() ?? `web-${Date.now()}`,
  ...(jsonBody ? { 'Content-Type': 'application/json' } : {}),
});

const authenticatedEnvelopeRequest = async <T>(path: string, options: { method?: string; body?: unknown } = {}): Promise<ApiEnvelope<T>> => {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers: authenticatedHeaders(session.accessToken, options.body !== undefined),
    ...(options.body !== undefined ? { body: JSON.stringify(options.body) } : {}),
  });
  return parseAuthenticatedEnvelope<T>(response);
};

export const authenticatedRequest = async <T>(path: string, options: { method?: string; body?: unknown } = {}): Promise<T> => {
  const envelope = await authenticatedEnvelopeRequest<T>(path, options);
  return envelope.data as T;
};

export const authenticatedPaginatedRequest = async <T>(path: string): Promise<PaginatedResult<T>> => {
  const envelope = await authenticatedEnvelopeRequest<T[]>(path);
  if (!Array.isArray(envelope.data) || !isValidPagination(envelope.pagination, envelope.data.length)) {
    throw new AuthSessionError(
      'MALFORMED_RESPONSE',
      'The server returned an invalid paginated response.',
      envelope.response_status,
    );
  }
  return { items: envelope.data, pagination: envelope.pagination };
};

export const authenticatedMultipartRequest = async <T>(path: string, fields: Record<string, string | Blob>): Promise<T> => {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const body = new FormData();
  Object.entries(fields).forEach(([field, value]) => body.set(field, value));
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: authenticatedHeaders(session.accessToken),
    body,
  });
  const envelope = await parseAuthenticatedEnvelope<T>(response);
  return envelope.data as T;
};

export const loginAndLoadCurrentUser = async (credentials: { email: string; password: string }): Promise<FrontendCurrentUser> => {
  const loginData = await request<LoginData>('/api/v1/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
  const session = {
    accessToken: loginData.access_token,
    refreshToken: loginData.refresh_token,
  };
  storedAuthSession(session);

  try {
    return await fetchCurrentUser(session.accessToken);
  } catch (error) {
    clearStoredAuthSession();
    throw error;
  }
};

export const portalLoginAndLoadCurrentUser = async (credentials: { identifier: string; password: string }): Promise<FrontendCurrentUser> => {
  const loginData = await request<LoginData>('/api/v1/portal/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
  const session = {
    accessToken: loginData.access_token,
    refreshToken: loginData.refresh_token,
  };
  storedAuthSession(session);

  try {
    return await fetchCurrentUser(session.accessToken);
  } catch (error) {
    clearStoredAuthSession();
    throw error;
  }
};

export const startPortalActivation = async (payload: {
  folioOrMemberId: string;
  contact: string;
  panLast4?: string;
  aadhaarLast4?: string;
}): Promise<PortalActivationStartResult> => {
  const data = await request<{ challenge_id: string; masked_contact?: string; expires_at?: string }>('/api/v1/portal/auth/activation/start/', {
    method: 'POST',
    body: JSON.stringify({
      folio_or_member_id: payload.folioOrMemberId,
      contact: payload.contact,
      pan_last4: payload.panLast4,
      aadhaar_last4: payload.aadhaarLast4,
    }),
  });
  return {
    challengeId: data.challenge_id,
    maskedContact: data.masked_contact,
    expiresAt: data.expires_at,
  };
};

export const completePortalActivation = async (payload: {
  challengeId: string;
  otp: string;
  password: string;
  confirmPassword: string;
}): Promise<PortalAccountResult> => {
  const data = await request<{ portal_account: { member_id: string; status: string } }>('/api/v1/portal/auth/activation/complete/', {
    method: 'POST',
    body: JSON.stringify({
      challenge_id: payload.challengeId,
      otp: payload.otp,
      password: payload.password,
      confirm_password: payload.confirmPassword,
    }),
  });
  return {
    memberId: data.portal_account.member_id,
    status: data.portal_account.status,
  };
};

export const startPortalPasswordReset = async (payload: { identifier: string }): Promise<PortalActivationStartResult> => {
  const data = await request<{ challenge_id: string; masked_contact?: string; expires_at?: string }>('/api/v1/portal/auth/password-reset/start/', {
    method: 'POST',
    body: JSON.stringify({ identifier: payload.identifier }),
  });
  return {
    challengeId: data.challenge_id,
    maskedContact: data.masked_contact,
    expiresAt: data.expires_at,
  };
};

export const completePortalPasswordReset = async (payload: {
  challengeId: string;
  otp: string;
  password: string;
  confirmPassword: string;
}): Promise<{ reset: boolean }> => {
  return request<{ reset: boolean }>('/api/v1/portal/auth/password-reset/complete/', {
    method: 'POST',
    body: JSON.stringify({
      challenge_id: payload.challengeId,
      otp: payload.otp,
      password: payload.password,
      confirm_password: payload.confirmPassword,
    }),
  });
};

export const changePortalPassword = async (payload: {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}): Promise<{ passwordChanged: boolean }> => {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Member portal session is required.', 401);
  }
  const data = await request<{ password_changed: boolean }>('/api/v1/portal/auth/password/change/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${session.accessToken}` },
    body: JSON.stringify({
      current_password: payload.currentPassword,
      new_password: payload.newPassword,
      confirm_password: payload.confirmPassword,
    }),
  });
  return { passwordChanged: data.password_changed };
};

export const restoreCurrentUserFromStoredSession = async (): Promise<FrontendCurrentUser | null> => {
  const session = loadStoredAuthSession();
  if (!session) return null;

  try {
    return await fetchCurrentUser(session.accessToken);
  } catch (error) {
    clearStoredAuthSession();
    throw error;
  }
};

export const logoutSession = async (): Promise<void> => {
  const session = loadStoredAuthSession();
  clearStoredAuthSession();
  if (!session) return;

  await request<{ logged_out: boolean }>('/api/v1/auth/logout/', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: session.refreshToken }),
  });
};

const fetchCurrentUser = async (accessToken: string): Promise<FrontendCurrentUser> => {
  const currentUser = await request<BackendCurrentUser>('/api/v1/auth/me/', {
    method: 'GET',
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return mapBackendUserToFrontendUser(currentUser);
};

const request = async <T>(path: string, options: RequestInit): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers || {}),
    },
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }
  return envelope.data;
};
