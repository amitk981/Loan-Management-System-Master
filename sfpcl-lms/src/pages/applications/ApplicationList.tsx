import React, { useEffect, useState } from 'react';
import { Plus, Search, Filter, ChevronDown } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import type { ApplicationStatus } from '../../types';
import {
  fetchLoanRequestRegister,
  fetchStaffApplications,
  type LoanRequestRegisterRow,
  type Pagination,
  type StaffApplication,
} from '../../services/applicationIntakeApi';

const fmt = (n?: number) => n === undefined ? '—' : '₹' + n.toLocaleString('en-IN');

interface ApplicationListProps {
  onNew: () => void;
  onSelect: (id: string) => void;
}

const STATUS_OPTIONS: Array<ApplicationStatus | 'all'> = [
  'all', 'draft', 'submitted', 'deficiency_raised', 'returned_for_rectification',
  'incomplete_returned', 'reference_generated', 'appraisal_in_progress', 'appraisal_pending',
  'pending_credit_manager_review', 'pending_sanction_committee_approval',
  'under_sanction_review', 'clarification_requested', 'sanctioned',
  'documentation_in_progress', 'pending_final_checklist_approvals',
  'disbursement_ready', 'sap_customer_code_pending', 'sap_customer_code_confirmed',
  'payment_initiated', 'payment_authorized', 'disbursed',
  'rejected_by_credit_manager', 'rejected_by_sanction_committee',
];

const STATUS_LABELS: Record<string, string> = {
  all: 'All statuses',
  draft: 'Draft', submitted: 'Submitted - Pending Completeness Check',
  deficiency_raised: 'Deficiency Raised', returned_for_rectification: 'Returned for Rectification',
  incomplete_returned: 'Incomplete - Returned to Applicant',
  reference_generated: 'Reference Generated',
  appraisal_in_progress: 'Appraisal In Progress',
  appraisal_pending: 'Appraisal Pending',
  pending_credit_manager_review: 'Pending Credit Manager Review',
  pending_sanction_committee_approval: 'Pending Sanction Committee Approval',
  under_sanction_review: 'Under Sanction Review',
  clarification_requested: 'Clarification Requested',
  sanctioned: 'Sanctioned',
  documentation_in_progress: 'Documentation In Progress',
  pending_final_checklist_approvals: 'Pending Final Checklist Approvals',
  disbursement_ready: 'Disbursement Ready',
  sap_customer_code_pending: 'SAP Customer Code Pending',
  sap_customer_code_confirmed: 'SAP Customer Code Confirmed',
  payment_initiated: 'Payment Initiated',
  payment_authorized: 'Payment Authorized',
  disbursed: 'Disbursed',
  rejected_by_credit_manager: 'Rejected by Credit Manager',
  rejected_by_sanction_committee: 'Rejected by Sanction Committee',
};

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const getTableStatusLabel = (status: string) => {
  if (status === 'draft') return 'Draft';
  if (status === 'submitted') return 'Pending Completeness';
  if (status === 'deficiency_raised' || status === 'returned_for_rectification' || status === 'incomplete' || status === 'incomplete_returned') {
    return 'Returned for Rectification';
  }
  if (status === 'reference_generated') return 'Reference Generated';
  if (status === 'appraisal_in_progress') return 'Appraisal In Progress';
  return STATUS_LABELS[status] ?? status;
};

const ApplicationList: React.FC<ApplicationListProps> = ({ onNew, onSelect }) => {
  const { can } = useRole();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | 'all'>('all');
  const [applications, setApplications] = useState<StaffApplication[]>([]);
  const [registerRows, setRegisterRows] = useState<LoanRequestRegisterRow[]>([]);
  const [pagination, setPagination] = useState<Pagination>(emptyPagination);
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    fetchStaffApplications({
      search,
      applicationStatus: statusFilter,
      ordering: '-application_date',
      page: 1,
      pageSize: 20,
    })
      .then(result => {
        if (cancelled) return;
        setApplications(result.items);
        setPagination(result.pagination);
        return fetchLoanRequestRegister({ search, ordering: '-reference_generated_date', pageSize: 20 });
      })
      .then(result => {
        if (cancelled || !result) return;
        setRegisterRows(result.items);
        setStatus('success');
        setMessage('');
      })
      .catch(error => {
        if (cancelled) return;
        setApplications([]);
        setRegisterRows([]);
        setPagination(emptyPagination);
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'Unable to load applications.');
      });
    return () => {
      cancelled = true;
    };
  }, [search, statusFilter]);

  return (
    <ApplicationListView
      status={status}
      message={message}
      applications={applications}
      registerRows={registerRows}
      pagination={pagination}
      search={search}
      statusFilter={statusFilter}
      canCreate={can('create_application')}
      onSearchChange={setSearch}
      onStatusFilterChange={setStatusFilter}
      onNew={onNew}
      onSelect={onSelect}
    />
  );
};

export const ApplicationListView: React.FC<{
  status: 'loading' | 'success' | 'error';
  message: string;
  applications: StaffApplication[];
  registerRows: LoanRequestRegisterRow[];
  pagination: Pagination;
  search: string;
  statusFilter: ApplicationStatus | 'all';
  canCreate: boolean;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: ApplicationStatus | 'all') => void;
  onNew: () => void;
  onSelect: (id: string) => void;
}> = ({
  status,
  message,
  applications,
  registerRows,
  pagination,
  search,
  statusFilter,
  canCreate,
  onSearchChange,
  onStatusFilterChange,
  onNew,
  onSelect,
}) => {
  const countLabel = status === 'loading' ? 'Loading applications' : `${pagination.total_count} application${pagination.total_count !== 1 ? 's' : ''}`;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Loan Applications</h1>
          <p className="text-sm text-slate-500 mt-0.5">{countLabel}</p>
        </div>
        {canCreate && (
          <button onClick={onNew} className="btn-primary flex items-center gap-2">
            <Plus size={16} />
            New Application
          </button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by number or member…"
            value={search}
            onChange={e => onSearchChange(e.target.value)}
            className="field-input pl-8 text-sm py-2"
          />
        </div>

        <div className="relative">
          <select
            value={statusFilter}
            onChange={e => onStatusFilterChange(e.target.value as ApplicationStatus | 'all')}
            className="field-select text-sm py-2 pr-8 appearance-none"
          >
            {STATUS_OPTIONS.map(s => (
              <option key={s} value={s}>{STATUS_LABELS[s]}</option>
            ))}
          </select>
          <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="table-header text-left">ID / Reference</th>
                <th className="table-header text-left">Member</th>
                <th className="table-header text-left">Type</th>
                <th className="table-header text-right">Requested</th>
                <th className="table-header text-right">Eligible</th>
                <th className="table-header text-left">Status</th>
                <th className="table-header text-left">Current Owner</th>
                <th className="table-header text-left">TAT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {status === 'loading' ? (
                <tr>
                  <td colSpan={8} className="table-cell text-center text-slate-400 py-12">
                    Loading applications…
                  </td>
                </tr>
              ) : status === 'error' ? (
                <tr>
                  <td colSpan={8} className="table-cell text-center text-red-600 py-12">
                    {message || 'Unable to load applications.'}
                  </td>
                </tr>
              ) : applications.length === 0 ? (
                <tr>
                  <td colSpan={8} className="table-cell text-center text-slate-400 py-12">
                    No applications match your filters.
                  </td>
                </tr>
              ) : (
                applications.map(app => (
                  <tr
                    key={app.loan_application_id}
                    onClick={() => onSelect(app.loan_application_id)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="table-cell">
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-green-700 num">{app.application_reference_number ?? app.loan_application_id.slice(0, 8)}</span>
                      </div>
                      <div className="text-xs text-slate-400">{app.application_date}</div>
                    </td>
                    <td className="table-cell">
                      <div className="font-medium text-slate-900">{app.member.display_name}</div>
                      <div className="text-xs text-slate-400">{app.member.folio_number}</div>
                    </td>
                    <td className="table-cell">
                      <span className="text-xs capitalize text-slate-600">{formatMemberType(app.member.member_type)}</span>
                    </td>
                    <td className="table-cell text-right num">{fmtMoney(app.required_loan_amount)}</td>
                    <td className="table-cell text-right num">—</td>
                    <td className="table-cell">
                      <StatusBadge
                        label={getTableStatusLabel(app.application_status)}
                        family={
                          app.application_status === 'draft' ? 'neutral' :
                          app.application_status === 'submitted' ? 'info' :
                          ['deficiency_raised', 'returned_for_rectification', 'incomplete', 'incomplete_returned'].includes(app.application_status) ? 'blocked' :
                          app.application_status === 'reference_generated' || app.application_status === 'appraisal_in_progress' ? 'pending' :
                          undefined
                        }
                        size="sm"
                      />
                    </td>
                    <td className="table-cell">
                      <div className="text-slate-700">{app.assigned_owner?.full_name ?? '—'}</div>
                    </td>
                    <td className="table-cell">
                      <span className="text-xs font-semibold text-slate-500">{app.tat?.status ?? '—'}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-3 bg-slate-50 border-b border-slate-200 flex items-center gap-2">
          <Filter size={15} className="text-slate-500" />
          <h2 className="text-sm font-semibold text-slate-900">Loan Request Register</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="table-header text-left">Application No.</th>
                <th className="table-header text-left">Borrower Name</th>
                <th className="table-header text-left">Folio No.</th>
                <th className="table-header text-right">Requested Amount</th>
                <th className="table-header text-left">Current Status</th>
                <th className="table-header text-left">Assigned To</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {registerRows.length === 0 ? (
                <tr>
                  <td colSpan={6} className="table-cell text-center text-slate-400 py-10">
                    No register entries generated yet.
                  </td>
                </tr>
              ) : registerRows.map(row => (
                <tr key={row.loan_request_register_entry_id} className="hover:bg-slate-50 transition-colors">
                  <td className="table-cell font-semibold text-green-700 num">{row.application_reference_number}</td>
                  <td className="table-cell">{row.borrower_name ?? '—'}</td>
                  <td className="table-cell">{row.folio_number ?? '—'}</td>
                  <td className="table-cell text-right num">{fmtMoney(row.requested_amount)}</td>
                  <td className="table-cell">
                    <StatusBadge label={getTableStatusLabel(row.register_status)} size="sm" />
                  </td>
                  <td className="table-cell">{row.current_owner_role ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const fmtMoney = (value?: string | number | null) => {
  if (value === undefined || value === null || value === '') return '—';
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? `₹${numberValue.toLocaleString('en-IN')}` : '—';
};

const formatMemberType = (type: string) => (
  type === 'fpc' ? 'FPC' : type.replace(/_/g, ' ')
);

export default ApplicationList;
