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
const dateTime = (value: string | null) => value ? new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(value)) : '—';
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
  const [state, setState] = useState<'loading' | 'success' | 'error'>(canRead ? 'loading' : 'error');
  const [message, setMessage] = useState(canRead ? '' : 'You do not have Credit Sanction Register read permission.');

  useEffect(() => {
    if (!canRead) {
      setRows([]);
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
      setPagination(result.pagination);
      setState('success');
      setMessage('');
    }).catch(error => {
      if (cancelled) return;
      setRows([]);
      setPagination(emptyPagination);
      setState('error');
      setMessage(error instanceof Error ? error.message : 'Unable to load the Credit Sanction Register.');
    });
    return () => { cancelled = true; };
  }, [canRead, decision, financialYear, page]);

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
            <table className="w-full text-sm">
              <thead><tr className="bg-slate-50 border-b border-slate-200">
                {['Register / decision', 'Borrower / loan', 'Amounts / authority', 'Source evidence'].map(label => <th key={label} className="table-header text-left">{label}</th>)}
              </tr></thead>
              <tbody className="divide-y divide-slate-100">
                {state === 'loading' ? <tr><td colSpan={4} className="table-cell text-center text-slate-400 py-12">Loading Credit Sanction Register…</td></tr>
                  : rows.length === 0 ? <tr><td colSpan={4} className="table-cell text-center text-slate-400 py-12">No sanction decisions match these filters.</td></tr>
                    : rows.map(row => <SanctionRow key={row.credit_sanction_register_entry_id} row={row} />)}
              </tbody>
            </table>
          </div>
          {state === 'success' && <PaginationBar pagination={pagination} onPage={setPage} />}
        </div>
      )}
    </div>
  );
};

const SanctionRow: React.FC<{ row: CreditSanctionRegisterRow }> = ({ row }) => (
  <tr className="hover:bg-slate-50" data-testid="sanction-source-evidence">
    <td className="table-cell align-top"><span className="font-semibold text-green-700 num">{row.entry_number}</span><br /><span className="num text-slate-500">{row.application_number}</span><br /><StatusBadge label={row.decision} size="sm" /><br />{date(row.approval_date)}</td>
    <td className="table-cell align-top max-w-56 whitespace-normal"><span className="font-medium">{row.borrower_name}</span><br /><span className="num">{row.folio_number ?? '—'}</span><br /><span className="capitalize">{words(row.borrower_type)} · {row.loan_type ? words(row.loan_type) : '—'}</span><br />{row.purpose.description ?? '—'} · <span className="capitalize">{row.purpose.category ? words(row.purpose.category) : '—'}</span><br />Risk: <span className="capitalize">{row.risk.overall_risk_rating ? words(row.risk.overall_risk_rating) : '—'}</span></td>
    <td className="table-cell align-top max-w-56 whitespace-normal"><span className="num">Requested {money(row.requested_amount)}<br />Eligible {money(row.eligible_amount)}<br />Sanctioned {money(row.sanctioned_amount)}</span><br />{row.approval_authority}</td>
    <td className="table-cell align-top max-w-xl whitespace-normal">
      <span className="font-medium">Decision reason:</span> {row.reasons || '—'}<br /><span className="font-medium">Rejection reason:</span> {row.rejection_reason ?? '—'}<br /><span className="font-medium">Conditions:</span> {row.conditions ?? '—'}
      <div data-testid="sanction-approver-decisions">{row.approver_decisions.map(action => <span className="block" key={action.approval_action_id}><span className="font-medium">{action.full_name}</span> · <span className="capitalize">{action.decision}</span> · {dateTime(action.acted_at ?? null)} · {action.comments || 'No comment'}</span>)}</div>
      <span className="font-medium">Communication:</span> {row.communication ? `${words(row.communication.status)} · ${row.communication.sent_at ? dateTime(row.communication.sent_at) : 'not sent'}` : '—'}<br />
      <span className="font-medium">Exception:</span>{' '}
      {row.exception_reference ? <><span className="font-medium capitalize">{words(row.exception_reference.exception_type)}</span><br />{row.exception_reference.business_reason}<br /><span className="capitalize">{words(row.exception_reference.status)} · cycle {row.exception_reference.cycle_number}</span><br /><span className="num text-xs">{row.exception_reference.exception_register_entry_id}</span></> : 'None'}
      <br /><span className="font-medium">Conflict / abstention:</span>{' '}
      {row.conflict_abstention_details.length ? row.conflict_abstention_details.map(item => <span key={`${item.user_id}-${item.conflict_code}`} className="block"><span className="font-medium capitalize">{words(item.type)} · {words(item.conflict_code)}</span><br />{item.full_name ?? item.user_id}: {item.reason}<br /><span className="num text-xs">Action: {item.approval_action_id ?? 'none'} · {item.acted_at ? date(item.acted_at) : 'not acted'}</span></span>) : 'None'}
      <br /><span className="font-medium">General meeting evidence:</span>{' '}
      {row.general_meeting_approval_reference ? <>{date(row.general_meeting_approval_reference.meeting_date)} · {words(row.general_meeting_approval_reference.approval_status)}<br /><span className="capitalize">{words(row.general_meeting_approval_reference.related_party_type)}</span> · <span className="num">{row.general_meeting_approval_reference.related_party_user_id ?? 'no user reference'}</span><br /><span className="num text-xs">Meeting: {row.general_meeting_approval_reference.general_meeting_approval_id}<br />Notice: {row.general_meeting_approval_reference.notice_document_id}<br />Minutes: {row.general_meeting_approval_reference.minutes_document_id}<br />Resolution: {row.general_meeting_approval_reference.resolution_document_id}</span></> : 'Not required'}
    </td>
  </tr>
);

export const ExceptionRegisterPanel: React.FC = () => {
  const { currentUser } = useRole();
  const canRead = currentUser.permissions.includes('approvals.exception_register.read');
  const [rows, setRows] = useState<ExceptionRegisterRow[]>([]);
  const [pagination, setPagination] = useState(emptyPagination);
  const [status, setStatus] = useState<'' | 'pending' | 'approved' | 'rejected'>('');
  const [exceptionType, setExceptionType] = useState<'' | 'exceeds_loan_limit' | 'stage_bypass' | 'waiver'>('');
  const [page, setPage] = useState(1);
  const [state, setState] = useState<'loading' | 'success' | 'error'>(canRead ? 'loading' : 'error');
  const [message, setMessage] = useState(canRead ? '' : 'You do not have Exception Register read permission.');

  useEffect(() => {
    if (!canRead) {
      setRows([]);
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
        setPagination(result.pagination);
        setState('success');
        setMessage('');
      }).catch(error => {
        if (cancelled) return;
        setRows([]);
        setPagination(emptyPagination);
        setState('error');
        setMessage(error instanceof Error ? error.message : 'Unable to load the Exception Register.');
      });
    return () => { cancelled = true; };
  }, [canRead, exceptionType, page, status]);

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
          <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">
            {['Exception / status', 'Borrower / impact', 'Reason / authority', 'Evidence'].map(label => <th key={label} className="table-header text-left">{label}</th>)}
          </tr></thead><tbody className="divide-y divide-slate-100">
            {state === 'loading' ? <tr><td colSpan={4} className="table-cell text-center text-slate-400 py-12">Loading Exception Register…</td></tr>
              : rows.length === 0 ? <tr><td colSpan={4} className="table-cell text-center text-slate-400 py-12">No exceptions match these filters.</td></tr>
                : rows.map(row => <tr key={row.exception_register_entry_id} className="hover:bg-slate-50" data-testid="exception-source-evidence">
                  <td className="table-cell align-top max-w-48 whitespace-normal"><span className="font-semibold text-violet-700 num">{row.exception_register_entry_id}</span><br /><span className="capitalize">{words(row.exception_type)}</span><br /><StatusBadge label={row.status} size="sm" /><br />Cycle {row.cycle_number} · {date(row.decision_date)}</td>
                  <td className="table-cell align-top max-w-48 whitespace-normal"><span className="font-medium">{row.borrower_name ?? '—'}</span><br />{money(row.financial_impact)}<br />Requested by {row.requested_by ? `${row.requested_by.full_name} · ${row.requested_by.user_id}` : '—'}<br /><span className="num">{row.loan_application_id ?? row.loan_account_id ?? '—'}</span></td>
                  <td className="table-cell align-top max-w-56 whitespace-normal"><span className="font-medium">{row.description}</span><br />{row.business_reason}<br />Risk: {row.risk_assessment || '—'}<br />{row.authority_applied_summary}<br />Case: {words(row.case_status)}</td>
                  <td className="table-cell align-top max-w-xl whitespace-normal"><span className="font-medium">Approver comments:</span>{row.approval_actions.length === 0 ? ' —' : row.approval_actions.map(action => <span key={action.approval_action_id} className="block">{action.full_name} · <span className="capitalize">{action.decision}</span> · {dateTime(action.acted_at ?? null)} · {action.comments}</span>)}<span className="font-medium">Supporting documents:</span>{row.supporting_documents.length === 0 ? ' —' : row.supporting_documents.map(document => <span key={document.document_id} className="block"><span className="font-medium">{document.file_name}</span> · <span className="capitalize">{document.sensitivity_level}</span> · {date(document.uploaded_at)}<br /><span className="num text-xs">{document.document_id} · {document.mime_type ?? 'unknown type'} · {document.file_size_bytes ?? 'unknown size'} bytes</span></span>)}Created {date(row.created_at)} · closed {date(row.closed_at)}</td>
                </tr>)}
          </tbody></table></div>
          {state === 'success' && <PaginationBar pagination={pagination} onPage={setPage} />}
        </div>
      )}
    </div>
  );
};

const PaginationBar: React.FC<{ pagination: Pagination; onPage: (page: number) => void }> = ({ pagination, onPage }) => (
  <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between text-sm">
    <span className="text-slate-500">Page {pagination.page} of {pagination.total_pages}</span>
    <div className="flex gap-2">
      <button className="btn-secondary flex items-center gap-1 text-sm" disabled={!pagination.has_previous} onClick={() => onPage(pagination.page - 1)}><ChevronLeft size={14} /> Previous</button>
      <button className="btn-secondary flex items-center gap-1 text-sm" disabled={!pagination.has_next} onClick={() => onPage(pagination.page + 1)}>Next <ChevronRight size={14} /></button>
    </div>
  </div>
);
