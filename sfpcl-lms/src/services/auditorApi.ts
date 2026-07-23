import { authenticatedRequest } from './authSession';

export interface AuditorDefaultCase {
  default_case_id: string;
  loan_account_number: string;
  borrower_name: string;
  default_case_status: string;
  total_outstanding: string;
  audit_references: string[];
  workflow_references: string[];
  [key: string]: unknown;
}

export interface AuditorClosure {
  loan_closure_id: string;
  loan_account_number: string;
  borrower_name: string;
  closure_stage: string;
  closed_at: string;
  audit_references: string[];
  workflow_references: string[];
  [key: string]: unknown;
}

export interface AuditorComplianceItem {
  record_type: string;
  record_id: string;
  details: Record<string, unknown>;
  audit_references: string[];
  workflow_references: string[];
}

export interface AuditorGrievance {
  grievance_id: string;
  grievance_reference: string;
  grievance_category: string;
  status: string;
  description: string;
  audit_references: string[];
  workflow_references: string[];
  [key: string]: unknown;
}

export interface AuditorEpic011Projection {
  summary: {
    default_cases: number;
    closures: number;
    compliance_items: number;
    grievances: number;
  };
  default_cases: AuditorDefaultCase[];
  closures: AuditorClosure[];
  compliance_items: AuditorComplianceItem[];
  grievances: AuditorGrievance[];
}

export const fetchAuditorEpic011 = () =>
  authenticatedRequest<AuditorEpic011Projection>('/api/v1/auditor/epic-011/');
