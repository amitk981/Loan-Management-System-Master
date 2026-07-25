import {
  authenticatedPaginatedRequest,
  authenticatedRequest,
  type PaginatedResult,
} from './authSession';

export interface AuditActor {
  user_id: string;
  full_name: string;
}

export interface AuditLinkedRecord {
  entity_type: string;
  entity_id: string | null;
}

export interface AuditLogProjection {
  audit_log_id: string;
  actor: AuditActor | null;
  actor_type: string;
  actor_role_codes: string[];
  actor_team_codes: string[];
  action: string;
  module: string;
  entity_type: string;
  entity_id: string | null;
  linked_record: AuditLinkedRecord;
  old_value: Record<string, unknown>;
  new_value: Record<string, unknown>;
  reason: string | number | boolean | null;
  outcome: string | number | boolean | null;
  request_id: string | number | boolean | null;
  ip_address: string | null;
  device: string | null;
  created_at: string;
}

export interface AuditLogQuery {
  entityType?: string;
  action?: string;
  actorUserId?: string;
  createdFrom?: string;
  createdTo?: string;
  page?: number;
  pageSize?: number;
}

export interface AuditObservationReference {
  source_type: 'audit_log' | 'workflow_event' | 'version_history' | 'compliance_evidence';
  source_id: string;
  entity_type?: string;
  entity_id?: string | null;
  evidence_type?: string;
}

export interface AuditObservationProjection {
  audit_observation_id: string;
  creator: {
    user_id: string;
    full_name: string;
    role_code: string;
    team_codes: string[];
  };
  audit_scope: 'audit_readonly';
  observation: string;
  source_references: AuditObservationReference[];
  created_at: string;
}

export interface AuditObservationQuery {
  page?: number;
  pageSize?: number;
}

export interface CreateAuditObservationInput {
  observation: string;
  sourceReferences: Array<Pick<AuditObservationReference, 'source_type' | 'source_id'>>;
}

export const fetchAuditLogs = (
  query: AuditLogQuery = {},
): Promise<PaginatedResult<AuditLogProjection>> => {
  const params = new URLSearchParams();
  add(params, 'entity_type', query.entityType);
  add(params, 'action', query.action);
  add(params, 'actor_user_id', query.actorUserId);
  add(params, 'created_from', query.createdFrom);
  add(params, 'created_to', query.createdTo);
  add(params, 'page', query.page);
  add(params, 'page_size', query.pageSize);
  const suffix = params.size ? `?${params.toString()}` : '';
  return authenticatedPaginatedRequest<AuditLogProjection>(
    `/api/v1/audit-logs/${suffix}`,
  );
};

export const fetchAuditObservations = (
  query: AuditObservationQuery = {},
): Promise<PaginatedResult<AuditObservationProjection>> => {
  const params = new URLSearchParams({ audit_scope: 'audit_readonly' });
  add(params, 'page', query.page);
  add(params, 'page_size', query.pageSize);
  return authenticatedPaginatedRequest<AuditObservationProjection>(
    `/api/v1/audit-observations/?${params.toString()}`,
  );
};

export const fetchAuditObservation = (
  auditObservationId: string,
): Promise<AuditObservationProjection> => authenticatedRequest<AuditObservationProjection>(
  `/api/v1/audit-observations/${auditObservationId}/`,
);

export const createAuditObservation = (
  input: CreateAuditObservationInput,
): Promise<AuditObservationProjection> => authenticatedRequest<AuditObservationProjection>(
  '/api/v1/audit-observations/',
  {
    method: 'POST',
    body: {
      audit_scope: 'audit_readonly',
      observation: input.observation,
      source_references: input.sourceReferences,
    },
  },
);

const add = (
  params: URLSearchParams,
  key: string,
  value: string | number | undefined,
) => {
  if (value !== undefined && value !== '') params.set(key, String(value));
};
