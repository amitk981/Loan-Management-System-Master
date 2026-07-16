import type { AuditEvent } from '../types';
import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

export interface DocumentationActionField {
  name: string; label: string;
  type: 'text' | 'textarea' | 'select' | 'date' | 'datetime-local' | 'file';
  required: boolean; options?: string[];
}

export interface DocumentationAction {
  action_code: string; label: string; enabled: boolean;
  disabled_reason: string | null; required_permission: string; required_role?: string;
  action_id: string; action_key: string;
  action_url: string;
  method: 'POST' | 'PATCH';
  fields?: DocumentationActionField[];
  template_version?: string;
}

export interface DocumentationDownload {
  file_name: string; mime_type: string; action_url: string;
}

export interface DocumentationItem {
  checklist_item_id: string; item_code: string; item_label: string;
  required: boolean; applicable: boolean; status: string; blocker: string | null;
  stamp_status: string | null; notarisation_status: string | null; poa_status: string | null;
  available_actions: DocumentationAction[];
  document: null | {
    loan_document_id: string; version: string;
    generation_status: string; execution_status: string; verification_status: string;
    download: DocumentationDownload | null;
  };
}

interface TimelineRow {
  id: string; entity_type: string; entity_id: string; event_type: string;
  timestamp: string; actor_name: string;
  actor_role: AuditEvent['actorRole'];
  previous_state?: string; new_state?: string; reason?: string; comment?: string;
}

export interface DocumentationWorkspace {
  snapshot_id: string; loan_application_id: string;
  application_reference_number: string | null; borrower_name: string;
  checklist_status: string; bank_verification_status: string;
  pack_summary: {
    status: string; available_count: number; missing_count: number; pending_review_count: number;
  };
  items: DocumentationItem[];
  blockers: { item_code: string; label: string; reason: string }[];
  approval_stages: { role: string; status: string }[];
  available_actions: DocumentationAction[];
  security_workflows: Record<string, {
    required: boolean; status: string; available_actions: DocumentationAction[];
  }>;
  timeline: AuditEvent[];
}

type RawDocumentationWorkspace = Omit<DocumentationWorkspace, 'timeline'> & { timeline: TimelineRow[] };

export interface DocumentationQueueRow {
  loan_application_id: string; application_reference_number: string | null; borrower_name: string;
  sanctioned_amount: string | null; shareholding_mode: string | null;
  required_document_summary: { complete: number; required: number };
  poa_status: string; tri_party_status: string; sh4_status: string; cdsl_pledge_status: string;
  term_sheet_status: string; loan_agreement_status: string; bank_verification_status: string;
  checklist_status: string; current_owner: string;
}

export interface Pagination {
  page: number; page_size: number; total_count: number; total_pages: number;
  has_next: boolean; has_previous: boolean;
}

interface Envelope<T> {
  success: boolean; data?: T; pagination?: Pagination;
  error?: { code: string; message: string; field_errors?: Record<string, string> };
}

export async function fetchDocumentationQueue(page = 1, pageSize = 20) {
  const envelope = await requestEnvelope<DocumentationQueueRow[]>(
    `/api/v1/documentation-workspaces/?page=${page}&page_size=${pageSize}`,
  );
  return {
    items: envelope.data ?? [],
    pagination: envelope.pagination ?? {
      page, page_size: pageSize, total_count: 0, total_pages: 1,
      has_next: false, has_previous: false,
    },
  };
}

export async function fetchDocumentationWorkspace(applicationId: string): Promise<DocumentationWorkspace> {
  const workspace = await request<RawDocumentationWorkspace>(
    `/api/v1/loan-applications/${applicationId}/documentation-workspace/`,
  );
  return {
    ...workspace,
    timeline: workspace.timeline.map(row => ({
      id: row.id, entityType: row.entity_type, entityId: row.entity_id,
      eventType: row.event_type, timestamp: row.timestamp,
      actorName: row.actor_name, actorRole: row.actor_role,
      previousState: row.previous_state, newState: row.new_state,
      reason: row.reason, comment: row.comment,
    })),
  };
}

export function submitDocumentationAction(
  action: DocumentationAction,
  payload: Record<string, string | File>,
) {
  if (Object.values(payload).some(value => value instanceof File)) {
    const body = new FormData();
    Object.entries(payload).forEach(([name, value]) => body.append(name, value));
    return request<Record<string, unknown>>(action.action_url, action.method, body);
  }
  return request<Record<string, unknown>>(action.action_url, action.method, payload);
}

export async function downloadStaffDocument(download: DocumentationDownload) {
  if (!/^\/api\/v1\/loan-applications\/[0-9a-f-]+\/documentation-workspace\/[a-z0-9_-]+\/download\/$/i.test(download.action_url)) {
    throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Document download action is invalid.', 400);
  }
  const descriptor = await request<{ download_url: string }>(download.action_url);
  if (!descriptor.download_url.startsWith(`${download.action_url}?content=1&token=`)) {
    throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Document download capability is invalid.', 400);
  }
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${descriptor.download_url}`, {
    headers: { Authorization: `Bearer ${session.accessToken}` },
  });
  if (!response.ok) throw new AuthSessionError('DOWNLOAD_FAILED', 'Document download failed.', response.status);
  return response.blob();
}

export function openStaffDocumentBlob(content: Blob) {
  const url = URL.createObjectURL(content);
  window.open(url, '_blank', 'noopener,noreferrer');
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const envelope = await requestEnvelope<T>(path, method, body);
  return envelope.data as T;
}

async function requestEnvelope<T>(path: string, method = 'GET', body?: unknown) {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    // The browser owns multipart boundaries; JSON actions retain the standard envelope.
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      'X-Request-ID': crypto.randomUUID(),
      ...(body && !(body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: body instanceof FormData ? body : JSON.stringify(body) } : {}),
  });
  const envelope = await response.json() as Envelope<T>;
  if (!response.ok || !envelope.success || envelope.data === undefined) {
    throw new AuthSessionError(envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.', response.status, envelope.error?.field_errors);
  }
  return envelope;
}
