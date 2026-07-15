import React, { useEffect, useState } from 'react';
import { AlertOctagon, ChevronLeft, ChevronRight, Gavel } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import {
  fetchCreditSanctionRegister,
  fetchExceptionRegister,
  type CreditSanctionRegisterRow,
  type ExceptionRegisterRow,
  type Pagination,
} from '../../services/approvalRegistersApi';

const emptyPagination: Pagination = {
  page: 1, page_size: 20, total_count: 0, total_pages: 1, has_next: false, has_previous: false,
};

const money = (value: string | null) => value === null ? '—' : `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const date = (value: string | null) => value ? new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value)) : '—';
const dateTime = (value: string | null) => value ? new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Kolkata' }).format(new Date(value)) : '—';
const words = (value: string) => value.replace(/_/g, ' ');
const isCanonicalFinancialYear = (value: string) => {
  const match = /^FY(\d{4})-(\d{2})$/.exec(value);
  return Boolean(match && match[2] === String((Number(match[1]) + 1) % 100).padStart(2, '0'));
};

export const CreditSanctionRegisterPanel: React.FC = () => {
  const { currentUser } = useRole();
  const canRead = currentUser.permissions.includes('approvals.sanction_register.read');
  const [rows, setRows] = useState<CreditSanctionRegisterRow[]>([]);
  const [pagination, setPagination] = useState(emptyPagination);
  const [draftFinancialYear, setDraftFinancialYear] = useState('');
  const [financialYear, setFinancialYear] = useState('');
  const [decision, setDecision] = useState<'' | 'sanctioned' | 'rejected'>('');
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [state, setState] = useState<'loading' | 'success' | 'error'>(canRead ? 'loading' : 'error');
  const [message, setMessage] = useState(canRead ? '' : 'You do not have Credit Sanction Register read permission.');

  useEffect(() => {
    if (!canRead) {
      setRows([]);
      setSelectedId(null);
      setPagination(emptyPagination);
      setState('error');
      setMessage('You do not have Credit Sanction Register read permission.');
      return;
    }
    let cancelled = false;
    setState('loading');
    fetchCreditSanctionRegister({
      financialYear: financialYear || undefined,
      decision: decision || undefined,
      page,
      pageSize: 20,
    }).then(result => {
      if (cancelled) return;
      setRows(result.items);
      setSelectedId(current => result.items.some(row => row.credit_sanction_register_entry_id === current)
        ? current : result.items[0]?.credit_sanction_register_entry_id ?? null);
      setPagination(result.pagination);
      setState('success');
      setMessage('');
    }).catch(error => {
      if (cancelled) return;
      setRows([]);
      setSelectedId(null);
      setPagination(emptyPagination);
      setState('error');
      setMessage(error instanceof Error ? error.message : 'Unable to load the Credit Sanction Register.');
    });
    return () => { cancelled = true; };
  }, [canRead, decision, financialYear, page]);

  const selected = rows.find(row => row.credit_sanction_register_entry_id === selectedId) ?? null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <input
          aria-label="Financial year"
          className="field-input text-sm py-2 max-w-44"
          placeholder="FY2026-27"
          value={draftFinancialYear}
          onChange={event => setDraftFinancialYear(event.target.value)}
        />
        <button
          className="btn-secondary text-sm"
          disabled={draftFinancialYear !== '' && !isCanonicalFinancialYear(draftFinancialYear)}
          onClick={() => { setFinancialYear(draftFinancialYear); setPage(1); }}
        >Apply financial year</button>
        <select
          aria-label="Sanction decision"
          className="field-select text-sm py-2"
          value={decision}
          onChange={event => { setDecision(event.target.value as typeof decision); setPage(1); }}
        >
          <option value="">All decisions</option>
          <option value="sanctioned">Sanctioned</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {state === 'error' ? (
        <AlertBanner type="error" title="Credit sanction register unavailable" message={message} />
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Gavel size={14} className="text-green-600" /> Credit sanction register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">
              {state === 'loading' ? 'Loading register…' : `${pagination.total_count} record${pagination.total_count === 1 ? '' : 's'}`}
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm min-w-max">
              <thead><tr className="bg-slate-50 border-b border-slate-200">
                {['Application', 'Borrower', 'Borrower type', 'Requested', 'Eligible', 'Recommended', 'Sanctioned', 'Decision', 'Approval authority', 'Approvers', 'Approval date', 'Reasons', 'Exception', 'Conflict / abstention', 'General meeting evidence'].map(label => (
                  <th key={label} className={`table-header text-left ${['Requested', 'Eligible', 'Recommended', 'Sanctioned'].includes(label) ? 'text-right' : ''}`}>{label}</th>
                ))}
              </tr></thead>
              <tbody className="divide-y divide-slate-100">
                {state === 'loading' ? <tr><td colSpan={15} className="table-cell text-center text-slate-400 py-12">Loading Credit Sanction Register…</td></tr>
                  : rows.length === 0 ? <tr><td colSpan={15} className="table-cell text-center text-slate-400 py-12">No sanction decisions match these filters.</td></tr>
                    : rows.map(row => <SanctionRow key={row.credit_sanction_register_entry_id} row={row} onSelect={setSelectedId} />)}
              </tbody>
            </table>
          </div>
          {state === 'success' && <PaginationBar pagination={pagination} onPage={setPage} />}
        </div>
      )}
      {selected && <SanctionDetail row={selected} />}
    </div>
  );
};

const SanctionRow: React.FC<{ row: CreditSanctionRegisterRow; onSelect: (id: string) => void }> = ({ row, onSelect }) => (
  <tr className="hover:bg-slate-50">
    <td className="table-cell num font-semibold text-green-700"><button className="font-semibold text-green-700" onClick={() => onSelect(row.credit_sanction_register_entry_id)} aria-label={`View ${row.entry_number}`}>{row.application_number}</button></td>
    <td className="table-cell font-medium">{row.borrower_name}</td>
    <td className="table-cell text-slate-600 capitalize">{words(row.borrower_type)}</td>
    <td className="table-cell text-right num">{money(row.requested_amount)}</td>
    <td className="table-cell text-right num">{money(row.eligible_amount)}</td>
    <td className="table-cell text-right num">{money(row.recommended_amount)}</td>
    <td className="table-cell text-right num font-semibold">{money(row.sanctioned_amount)}</td>
    <td className="table-cell"><StatusBadge label={row.decision} size="sm" /></td>
    <td className="table-cell text-slate-600 max-w-64">{row.approval_authority}</td>
    <td className="table-cell text-slate-600 max-w-56">{row.approver_names.join(', ') || '—'}</td>
    <td className="table-cell text-slate-600">{date(row.approval_date)}</td>
    <td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.reasons || '—'}</td>
    <td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.exception_reference ? `${words(row.exception_reference.exception_type)} · ${row.exception_reference.business_reason}` : 'None'}</td>
    <td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.conflict_abstention_details.length ? `${row.conflict_abstention_details.length} recorded` : 'None'}</td>
    <td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.general_meeting_approval_reference ? `${date(row.general_meeting_approval_reference.meeting_date)} · ${words(row.general_meeting_approval_reference.approval_status)}` : 'Not required'}</td>
  </tr>
);

const SanctionDetail: React.FC<{ row: CreditSanctionRegisterRow }> = ({ row }) => (
  <div className="card" data-testid="sanction-source-evidence">
    <div className="flex items-start justify-between mb-4"><div><h3 className="font-semibold text-slate-900">Credit sanction register entry details</h3><p className="text-sm text-slate-500 num">{row.entry_number} · {row.application_number}</p></div><StatusBadge label={row.decision} size="sm" /></div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
      <div className="space-y-1"><p><span className="font-medium">Borrower:</span> {row.borrower_name} · <span className="capitalize">{words(row.borrower_type)}</span></p><p><span className="font-medium">Folio number:</span> {row.folio_number ?? '—'}</p><p><span className="font-medium">Loan type:</span> <span className="capitalize">{row.loan_type ? words(row.loan_type) : '—'}</span></p><p><span className="font-medium">Purpose:</span> {row.purpose?.description ?? '—'} · <span className="capitalize">{row.purpose?.category ? words(row.purpose.category) : '—'}</span></p><p><span className="font-medium">Risk:</span> <span className="capitalize">{row.risk?.overall_risk_rating ? words(row.risk.overall_risk_rating) : '—'}</span></p></div>
      <div className="space-y-1"><p className="num"><span className="font-medium">Amounts:</span> requested {money(row.requested_amount)} · eligible {money(row.eligible_amount)} · recommended {money(row.recommended_amount)} · sanctioned {money(row.sanctioned_amount)}</p><p><span className="font-medium">Approval authority:</span> {row.approval_authority}</p><p><span className="font-medium">Approval date:</span> {date(row.approval_date)}</p><p><span className="font-medium">Approver names:</span> {row.approver_names.join(', ') || '—'}</p><div data-testid="sanction-approver-decisions"><span className="font-medium">Approver decisions:</span> {row.approver_decisions.length === 0 ? '—' : row.approver_decisions.map(action => <span className="block" key={action.approval_action_id}>{action.full_name ?? action.user_id} · <span className="capitalize">{action.decision}</span> · {dateTime(action.acted_at ?? null)} · {action.comments || 'No comment'}</span>)}</div></div>
      <div className="space-y-1"><p><span className="font-medium">Decision reason:</span> {row.reasons || '—'}</p><p><span className="font-medium">Rejection reason:</span> {row.rejection_reason ?? '—'}</p><p><span className="font-medium">Conditions:</span> {row.conditions ?? '—'}</p><p><span className="font-medium">Communication:</span> {row.communication ? `${words(row.communication.status)} · ${row.communication.sent_at ? dateTime(row.communication.sent_at) : 'not sent'}` : '—'}</p><p><span className="font-medium">Exception:</span> {row.exception_reference ? `${words(row.exception_reference.exception_type)} · ${row.exception_reference.business_reason} · ${words(row.exception_reference.status)} · cycle ${row.exception_reference.cycle_number} · ${row.exception_reference.exception_register_entry_id}` : 'None'}</p><div><span className="font-medium">Conflict / abstention:</span> {row.conflict_abstention_details.length ? row.conflict_abstention_details.map(item => <span key={`${item.user_id}-${item.conflict_code}`} className="block">{words(item.type)} · {words(item.conflict_code)} · {item.full_name ?? item.user_id}: {item.reason} · Action {item.approval_action_id ?? 'none'} · {item.acted_at ? date(item.acted_at) : 'not acted'}</span>) : 'None'}</div><p><span className="font-medium">General meeting evidence:</span> {row.general_meeting_approval_reference ? `${date(row.general_meeting_approval_reference.meeting_date)} · ${words(row.general_meeting_approval_reference.approval_status)} · ${words(row.general_meeting_approval_reference.related_party_type)} · ${row.general_meeting_approval_reference.related_party_user_id ?? 'no user reference'} · Meeting ${row.general_meeting_approval_reference.general_meeting_approval_id} · Notice: ${row.general_meeting_approval_reference.notice_document_id} · Minutes: ${row.general_meeting_approval_reference.minutes_document_id} · Resolution: ${row.general_meeting_approval_reference.resolution_document_id}` : 'Not required'}</p></div>
    </div>
  </div>
);

export const ExceptionRegisterPanel: React.FC = () => {
  const { currentUser } = useRole();
  const canRead = currentUser.permissions.includes('approvals.exception_register.read');
  const [rows, setRows] = useState<ExceptionRegisterRow[]>([]);
  const [pagination, setPagination] = useState(emptyPagination);
  const [status, setStatus] = useState<'' | 'pending' | 'approved' | 'rejected'>('');
  const [exceptionType, setExceptionType] = useState<'' | 'exceeds_loan_limit' | 'stage_bypass' | 'waiver'>('');
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [state, setState] = useState<'loading' | 'success' | 'error'>(canRead ? 'loading' : 'error');
  const [message, setMessage] = useState(canRead ? '' : 'You do not have Exception Register read permission.');

  useEffect(() => {
    if (!canRead) {
      setRows([]);
      setSelectedId(null);
      setPagination(emptyPagination);
      setState('error');
      setMessage('You do not have Exception Register read permission.');
      return;
    }
    let cancelled = false;
    setState('loading');
    fetchExceptionRegister({ status: status || undefined, exceptionType: exceptionType || undefined, page, pageSize: 20 })
      .then(result => {
        if (cancelled) return;
        setRows(result.items);
        setSelectedId(current => result.items.some(row => row.exception_register_entry_id === current)
          ? current : result.items[0]?.exception_register_entry_id ?? null);
        setPagination(result.pagination);
        setState('success');
        setMessage('');
      }).catch(error => {
        if (cancelled) return;
        setRows([]);
        setSelectedId(null);
        setPagination(emptyPagination);
        setState('error');
        setMessage(error instanceof Error ? error.message : 'Unable to load the Exception Register.');
      });
    return () => { cancelled = true; };
  }, [canRead, exceptionType, page, status]);

  const selected = rows.find(row => row.exception_register_entry_id === selectedId) ?? null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <select aria-label="Exception status" className="field-select text-sm py-2" value={status} onChange={event => { setStatus(event.target.value as typeof status); setPage(1); }}>
          <option value="">All statuses</option><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option>
        </select>
        <select aria-label="Exception type" className="field-select text-sm py-2" value={exceptionType} onChange={event => { setExceptionType(event.target.value as typeof exceptionType); setPage(1); }}>
          <option value="">All exception types</option><option value="exceeds_loan_limit">Exceeds loan limit</option><option value="stage_bypass">Stage bypass</option><option value="waiver">Waiver</option>
        </select>
      </div>
      {state === 'error' ? (
        <AlertBanner type="error" title="Exception register unavailable" message={message} />
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2"><AlertOctagon size={14} className="text-violet-600" /> Exception register</p>
            <p className="text-xs text-slate-500 mt-0.5">{state === 'loading' ? 'Loading register…' : `${pagination.total_count} record${pagination.total_count === 1 ? '' : 's'}`}</p>
          </div>
          <div className="overflow-x-auto"><table className="w-full text-sm min-w-max"><thead><tr className="bg-slate-50 border-b border-slate-200">
            {['Exception ID', 'Application / loan', 'Cycle', 'Type', 'Description', 'Business reason', 'Risk', 'Required authority', 'Approver comments', 'Supporting documents', 'Decision', 'Case status', 'Created', 'Closed'].map(label => <th key={label} className="table-header text-left">{label}</th>)}
          </tr></thead><tbody className="divide-y divide-slate-100">
            {state === 'loading' ? <tr><td colSpan={14} className="table-cell text-center text-slate-400 py-12">Loading Exception Register…</td></tr>
              : rows.length === 0 ? <tr><td colSpan={14} className="table-cell text-center text-slate-400 py-12">No exceptions match these filters.</td></tr>
                : rows.map(row => <tr key={row.exception_register_entry_id} className="hover:bg-slate-50">
                  <td className="table-cell num font-semibold text-violet-700"><button className="font-semibold text-violet-700" onClick={() => setSelectedId(row.exception_register_entry_id)} aria-label={`View ${row.exception_register_entry_id}`}>{row.exception_register_entry_id}</button></td>
                  <td className="table-cell num">{row.loan_application_id ?? row.loan_account_id ?? '—'}</td><td className="table-cell num">{row.cycle_number}</td><td className="table-cell capitalize">{words(row.exception_type)}</td>
                  <td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.description}</td><td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.business_reason}</td><td className="table-cell">{row.risk_assessment || '—'}</td>
                  <td className="table-cell text-slate-600 max-w-72 whitespace-normal">{row.authority_applied_summary}</td><td className="table-cell text-slate-600">{row.approval_actions.length}</td><td className="table-cell text-slate-600">{row.supporting_documents.length}</td>
                  <td className="table-cell"><StatusBadge label={row.status} size="sm" /></td><td className="table-cell"><StatusBadge label={row.case_status} size="sm" /></td><td className="table-cell">{date(row.created_at)}</td><td className="table-cell">{date(row.closed_at)}</td>
                </tr>)}
          </tbody></table></div>
          {state === 'success' && <PaginationBar pagination={pagination} onPage={setPage} />}
        </div>
      )}
      {selected && <ExceptionDetail row={selected} />}
    </div>
  );
};

const ExceptionDetail: React.FC<{ row: ExceptionRegisterRow }> = ({ row }) => (
  <div className="card" data-testid="exception-source-evidence">
    <div className="flex items-start justify-between mb-4"><div><h3 className="font-semibold text-slate-900">Exception register entry details</h3><p className="text-sm text-slate-500 num">{row.exception_register_entry_id} · cycle {row.cycle_number}</p></div><StatusBadge label={row.status} size="sm" /></div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
      <div className="space-y-1"><p><span className="font-medium">Application / loan:</span> <span className="num">{row.loan_application_id ?? row.loan_account_id ?? '—'}</span></p><p><span className="font-medium">Borrower:</span> {row.borrower_name ?? '—'}</p><p><span className="font-medium">Financial impact:</span> {money(row.financial_impact)}</p><p><span className="font-medium">Requested by:</span> {row.requested_by ? `${row.requested_by.full_name} · ${row.requested_by.user_id}` : '—'}</p><p><span className="font-medium">Decision date:</span> {date(row.decision_date)}</p></div>
      <div className="space-y-1"><p><span className="font-medium">Type:</span> <span className="capitalize">{words(row.exception_type)}</span></p><p><span className="font-medium">Description:</span> {row.description}</p><p><span className="font-medium">Business reason:</span> {row.business_reason}</p><p><span className="font-medium">Risk:</span> {row.risk_assessment || '—'}</p><p><span className="font-medium">Required authority:</span> {row.authority_applied_summary}</p><p><span className="font-medium">Case status:</span> <span className="capitalize">{words(row.case_status)}</span></p></div>
      <div className="space-y-1"><div><span className="font-medium">Approver comments:</span> {row.approval_actions.length === 0 ? '—' : row.approval_actions.map(action => <span key={action.approval_action_id} className="block">{action.full_name ?? action.user_id} · <span className="capitalize">{action.decision}</span> · {dateTime(action.acted_at ?? null)} · {action.comments}</span>)}</div><div><span className="font-medium">Supporting documents:</span> {row.supporting_documents.length === 0 ? '—' : row.supporting_documents.map(document => <span key={document.document_id} className="block"><span className="font-medium">{document.file_name}</span> · <span className="capitalize">{document.sensitivity_level}</span> · {date(document.uploaded_at)} · <span className="num">{document.document_id} · {document.mime_type ?? 'unknown type'} · {document.file_size_bytes ?? 'unknown size'} bytes</span></span>)}</div><p><span className="font-medium">Created:</span> {date(row.created_at)} · <span className="font-medium">Closed:</span> {date(row.closed_at)}</p></div>
    </div>
  </div>
);

const PaginationBar: React.FC<{ pagination: Pagination; onPage: (page: number) => void }> = ({ pagination, onPage }) => (
  <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between text-sm">
    <span className="text-slate-500">Page {pagination.page} of {pagination.total_pages}</span>
    <div className="flex gap-2">
      <button className="btn-secondary flex items-center gap-1 text-sm" disabled={!pagination.has_previous} onClick={() => onPage(pagination.page - 1)}><ChevronLeft size={14} /> Previous</button>
      <button className="btn-secondary flex items-center gap-1 text-sm" disabled={!pagination.has_next} onClick={() => onPage(pagination.page + 1)}>Next <ChevronRight size={14} /></button>
    </div>
  </div>
);
