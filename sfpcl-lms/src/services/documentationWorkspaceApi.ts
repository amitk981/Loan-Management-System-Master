import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';
export type DocumentationAction = { action: string; action_url: string; method?: 'POST' | 'PATCH'; loan_document_id?: string; document_type?: string; template_id?: string; template_version?: string; output_formats?: string[] };
export type DocumentationDownload = { file_name: string; mime_type: string; action_url: string };
export type DocumentationItem = { checklist_item_id: string; item_code: string; item_label: string; required: boolean; applicable: boolean; status: string; blocker: string | null; stamp_status: string | null; notarisation_status: string | null; poa_status: string | null; available_actions: DocumentationAction[]; document: null | { loan_document_id: string; version: string; generation_status: string; execution_status: string; verification_status: string; download: DocumentationDownload | null } };
export type DocumentationWorkspace = { snapshot_id: string; loan_application_id: string; application_reference_number: string | null; borrower_name: string; checklist_status: string; pack_summary: { status: string; available_count: number; missing_count: number; pending_review_count: number }; items: DocumentationItem[]; blockers: { item_code: string; label: string; reason: string }[]; approval_stages: { role: string; status: string }[]; available_actions: DocumentationAction[]; security_workflows: Record<string, { required: boolean; status: string; available_actions: DocumentationAction[] }> };
type Envelope<T> = { success: boolean; data?: T; error?: { code: string; message: string; field_errors?: Record<string, string> } };
export const fetchDocumentationWorkspace = (applicationId: string) => request<DocumentationWorkspace>(`/api/v1/loan-applications/${applicationId}/documentation-workspace/`);
export const submitDocumentationAction = (action: DocumentationAction, payload: Record<string, unknown>) => request<Record<string, unknown>>(action.action_url, action.method ?? 'POST', payload);
export const downloadStaffDocument = async (download: DocumentationDownload) => {
  if (!/^\/api\/v1\/loan-applications\/[0-9a-f-]+\/documentation-workspace\/[a-z0-9_-]+\/download\/$/i.test(download.action_url)) throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Document download action is invalid.', 400);
  const descriptor = await request<{ download_url: string }>(download.action_url); if (!descriptor.download_url.startsWith(`${download.action_url}?content=1&token=`)) throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Document download capability is invalid.', 400);
  const session = loadStoredAuthSession(); if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${descriptor.download_url}`, { headers: { Authorization: `Bearer ${session.accessToken}` } }); if (!response.ok) throw new AuthSessionError('DOWNLOAD_FAILED', 'Document download failed.', response.status);
  return response.blob();
};
export const openStaffDocumentBlob = (content: Blob) => { const url = URL.createObjectURL(content); window.open(url, '_blank', 'noopener,noreferrer'); window.setTimeout(() => URL.revokeObjectURL(url), 60_000); };
const request = async <T>(path: string, method = 'GET', body?: unknown): Promise<T> => {
  const session = loadStoredAuthSession(); if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${path}`, { method, headers: { Accept: 'application/json', Authorization: `Bearer ${session.accessToken}`, ...(body ? { 'Content-Type': 'application/json' } : {}) }, ...(body ? { body: JSON.stringify(body) } : {}) });
  const envelope = await response.json() as Envelope<T>; if (!response.ok || !envelope.success || envelope.data === undefined) throw new AuthSessionError(envelope.error?.code ?? 'REQUEST_FAILED', envelope.error?.message ?? 'Request failed.', response.status, envelope.error?.field_errors);
  return envelope.data;
};
