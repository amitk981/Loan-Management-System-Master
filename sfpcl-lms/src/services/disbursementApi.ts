import {
  authenticatedPaginatedRequest,
  authenticatedRequest,
} from './authSession';

export interface DisbursementActionField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'money' | 'date' | 'datetime-local' | 'email';
  required: boolean;
  value?: string | null;
}

export interface DisbursementAction {
  action_code: string;
  label: string;
  enabled: boolean;
  disabled_reason: string | null;
  required_permission: string;
  action_url: string;
  method: 'POST';
  fields: DisbursementActionField[];
  fixed_payload?: Record<string, string>;
}

export interface ReadinessCheck {
  code: string;
  label: string;
  status: 'pass' | 'fail';
  reason?: string;
}

export interface DisbursementWorkspaceRow {
  workspace_id: string;
  loan_account_id: string | null;
  disbursement_id: string | null;
  loan_application_id: string;
  application_reference_number: string | null;
  loan_account_number: string | null;
  member: { member_id: string; display_name: string };
  sanctioned_amount: string;
  disbursement_amount: string;
  sap: { request_id: string | null; status: string; customer_code_masked: string | null };
  readiness: {
    ready_for_disbursement: boolean;
    evaluated_at: string | null;
    checks: ReadinessCheck[];
  };
  beneficiary_bank: null | {
    account_holder_name: string; account_number_masked: string;
    ifsc_code: string; bank_name: string; branch_name: string;
  };
  source_bank: null | {
    account_holder_name: string;
    account_number_masked: string; bank_name: string;
  };
  initiation_status: string | null;
  authorisation_status: string | null;
  bank_transfer_status: string | null;
  advice_status: string;
  bank_reference_masked: string | null;
  initiated_by: null | { user_id: string; full_name: string };
  initiated_at: string | null;
  authorised_at: string | null;
  disbursed_at: string | null;
  available_actions: DisbursementAction[];
}

export const fetchDisbursementWorkspace = (page = 1, pageSize = 20) =>
  authenticatedPaginatedRequest<DisbursementWorkspaceRow>(
    `/api/v1/disbursement-workspaces/?page=${page}&page_size=${pageSize}`,
  );

export const submitDisbursementAction = (
  action: DisbursementAction,
  payload: Record<string, string>,
  idempotencyKey?: string,
) => authenticatedRequest<Record<string, unknown>>(action.action_url, {
  method: action.method,
  body: { ...(action.fixed_payload ?? {}), ...payload },
  ...(idempotencyKey ? { headers: { 'Idempotency-Key': idempotencyKey } } : {}),
});
