import { authenticatedRequest, type Pagination } from './authSession';

export type GlobalSearchResultType =
  | 'member'
  | 'loan_application'
  | 'loan_account'
  | 'document'
  | 'repayment'
  | 'compliance_record'
  | 'audit_log';

export interface GlobalSearchAction {
  label: 'Open' | 'View documents' | 'View loan account';
  page: string;
  entity_id: string;
}

export interface GlobalSearchResult {
  id: string;
  result_type: GlobalSearchResultType;
  title: string;
  identifier: string | null;
  status: string;
  risk_status: string | null;
  amount: string | null;
  owner: string | null;
  last_updated_at: string;
  last_updated_by: string | null;
  quick_actions: GlobalSearchAction[];
}

export interface GlobalSearchGroup {
  items: GlobalSearchResult[];
  pagination: Pagination;
}

export interface GlobalSearchResponse {
  groups: Partial<Record<string, GlobalSearchGroup>>;
  continuation: string;
}

export type GlobalSearchPages = Partial<Record<string, number>>;

export type GlobalSearchRequest = {
  pages?: GlobalSearchPages;
} & ({ search: string; continuation?: never } | { continuation: string; search?: never });

export const fetchGlobalSearch = (request: GlobalSearchRequest): Promise<GlobalSearchResponse> =>
  authenticatedRequest<GlobalSearchResponse>('/api/v1/global-search/', {
    method: 'POST',
    body: request,
  });
