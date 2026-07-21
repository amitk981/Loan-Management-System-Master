import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Banknote, CheckCircle2, FileText, Plus, XCircle } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import Tabs from '../../components/ui/Tabs';
import RepaymentLedger, { PaginationControls } from '../../components/loan/RepaymentLedger';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError, type Pagination } from '../../services/authSession';
import { fetchLoanAccounts, type LoanAccountProjection } from '../../services/loanAccountsApi';
import {
  canPostAndAllocateRepayment,
  fetchBankStatementLines,
  fetchLoanLedger,
  fetchRepayments,
  postAndAllocateDirectRepayment,
  type AllocationResult,
  type BankStatementLineProjection,
  type LoanLedgerRow,
  type RepaymentProjection,
} from '../../services/servicingApi';
import { formatMoney } from '../../utils/formatMoney';

const emptyPagination: Pagination = { page: 1, page_size: 20, total_count: 0, total_pages: 1, has_next: false, has_previous: false };
const money = formatMoney;
const date = (value: string | null) => value ? new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';
const label = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase());
const errorState = (error: unknown, fallback: string) => ({
  message: error instanceof Error ? error.message : fallback,
  unauthorized: error instanceof AuthSessionError && [401, 403].includes(error.status || 0),
});
type SurfaceError = ReturnType<typeof errorState>;
type StatementStatus = 'unmatched' | 'exception';
interface StatementQueueState {
  rows: BankStatementLineProjection[];
  pagination: Pagination;
  loading: boolean;
  error: SurfaceError | null;
}
const emptyStatementQueue = (): StatementQueueState => ({
  rows: [], pagination: emptyPagination, loading: false, error: null,
});

const RepaymentsHub: React.FC = () => {
  const { currentUser } = useRole();
  const canRead = currentUser.permissions.includes('finance.loan_account.read');
  const canReadStatements = currentUser.permissions.includes('finance.bank_statement.read');
  const canPost = canPostAndAllocateRepayment(currentUser.permissions, currentUser.roleCodes);
  const [activeTab, setActiveTab] = useState(0);
  const [accounts, setAccounts] = useState<LoanAccountProjection[]>([]);
  const [selectedLoan, setSelectedLoan] = useState('');
  const [ledger, setLedger] = useState<LoanLedgerRow[]>([]);
  const [repayments, setRepayments] = useState<RepaymentProjection[]>([]);
  const [ledgerPagination, setLedgerPagination] = useState<Pagination>(emptyPagination);
  const [repaymentPagination, setRepaymentPagination] = useState<Pagination>(emptyPagination);
  const [statementQueues, setStatementQueues] = useState<Record<StatementStatus, StatementQueueState>>({
    unmatched: emptyStatementQueue(), exception: emptyStatementQueue(),
  });
  const [loading, setLoading] = useState(true);
  const [surfaceLoading, setSurfaceLoading] = useState(false);
  const [loadError, setLoadError] = useState<{ message: string; unauthorized: boolean } | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [showPostModal, setShowPostModal] = useState(false);
  const [postAmount, setPostAmount] = useState('');
  const [postMode, setPostMode] = useState<'rtgs' | 'neft'>('rtgs');
  const [postRef, setPostRef] = useState('');
  const [postDate, setPostDate] = useState(new Date().toISOString().slice(0, 10));
  const [sapRef, setSapRef] = useState('');
  const [postError, setPostError] = useState<string | null>(null);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<{ replayed: boolean; allocation: AllocationResult | null } | null>(null);
  const attemptKey = useRef<string | null>(null);
  const loanSurfaceRequest = useRef(0);
  const statementRequests = useRef<Record<StatementStatus, number>>({ unmatched: 0, exception: 0 });

  const loadAccounts = useCallback(async () => {
    const result = await fetchLoanAccounts(1, 20);
    setAccounts(result.items);
    setSelectedLoan(current => current || result.items[0]?.loan_account_id || '');
  }, []);

  useEffect(() => {
    if (!canRead) { setLoading(false); return; }
    let current = true;
    setLoading(true);
    setLoadError(null);
    void loadAccounts().catch(error => { if (current) setLoadError(errorState(error, 'Repayment workspace could not be loaded.')); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [canRead, loadAccounts, refreshVersion]);

  const loadLoanSurfaces = useCallback(async (loanId: string, ledgerPage = 1, repaymentPage = 1) => {
    const request = ++loanSurfaceRequest.current;
    const [ledgerResult, repaymentResult] = await Promise.all([
      fetchLoanLedger(loanId, ledgerPage, 20), fetchRepayments(loanId, repaymentPage, 20),
    ]);
    if (request !== loanSurfaceRequest.current) return;
    setLedger(ledgerResult.items); setLedgerPagination(ledgerResult.pagination);
    setRepayments(repaymentResult.items); setRepaymentPagination(repaymentResult.pagination);
  }, []);

  useEffect(() => {
    if (!selectedLoan) return;
    let current = true;
    setSurfaceLoading(true); setLoadError(null);
    void loadLoanSurfaces(selectedLoan).catch(error => { if (current) setLoadError(errorState(error, 'Repayment records could not be loaded.')); })
      .finally(() => { if (current) setSurfaceLoading(false); });
    return () => { current = false; };
  }, [loadLoanSurfaces, refreshVersion, selectedLoan]);

  const loadStatementQueue = useCallback(async (status: StatementStatus, page = 1) => {
    const request = ++statementRequests.current[status];
    setStatementQueues(current => ({
      ...current, [status]: { ...current[status], loading: true, error: null },
    }));
    try {
      const result = await fetchBankStatementLines(status, page, 20);
      if (request !== statementRequests.current[status]) return;
      setStatementQueues(current => ({
        ...current, [status]: { rows: result.items, pagination: result.pagination, loading: false, error: null },
      }));
    } catch (error) {
      if (request !== statementRequests.current[status]) return;
      setStatementQueues(current => ({
        ...current,
        [status]: {
          ...current[status], loading: false,
          error: errorState(error, `${label(status)} statement lines could not be loaded.`),
        },
      }));
    }
  }, []);

  useEffect(() => {
    if (!canReadStatements) return;
    void Promise.all([loadStatementQueue('unmatched'), loadStatementQueue('exception')]);
  }, [canReadStatements, loadStatementQueue, refreshVersion]);

  const openPost = () => {
    attemptKey.current = globalThis.crypto?.randomUUID?.() ?? `repayment-${Date.now()}`;
    setPostAmount(''); setPostRef(''); setSapRef(''); setPostError(null); setPostResult(null); setShowPostModal(true);
  };

  const submit = async () => {
    if (!selectedLoan || !attemptKey.current) return;
    setPosting(true); setPostError(null);
    try {
      const result = await postAndAllocateDirectRepayment({
        loanAccountId: selectedLoan,
        capture: { repayment_source: 'direct_farmer', amount_received: postAmount, received_date: postDate, payment_method: postMode, bank_reference_number: postRef, remarks: 'Confirmed direct repayment received by SFPCL.' },
        sapPosting: { sap_entry_reference: sapRef, sap_posted_at: new Date().toISOString(), remarks: 'SAP receipt confirmed before principal-first allocation.' },
        idempotencyKey: attemptKey.current,
        permissions: currentUser.permissions,
        roleCodes: currentUser.roleCodes,
      });
      setPostResult({ replayed: result.replayed, allocation: result.allocation });
      setRefreshVersion(version => version + 1);
    } catch (error) { setPostError(error instanceof Error ? error.message : 'Repayment could not be posted.'); }
    finally { setPosting(false); }
  };

  if (!canRead) return <div className="p-6"><AlertBanner type="error" title="Access Denied" message="Loan account read permission is required to view the Repayments Hub." /></div>;
  if (loading) return <div className="p-6"><div className="card text-sm text-slate-500">Loading repayment workspace…</div></div>;
  if (loadError && accounts.length === 0) return <div className="p-6"><AlertBanner type="error" title={loadError.unauthorized ? 'Access Denied' : 'Repayments Unavailable'} message={loadError.message} /></div>;
  const loan = accounts.find(candidate => candidate.loan_account_id === selectedLoan);

  return <div className="p-6 space-y-4">
    <div className="flex items-center justify-between"><div><h1 className="text-xl font-bold text-slate-900">Repayments Hub</h1><p className="text-sm text-slate-500 mt-0.5">{accounts.length} canonical loan account{accounts.length === 1 ? '' : 's'} shown</p></div>{canPost && <button type="button" onClick={openPost} className="btn-primary flex items-center gap-2"><Plus size={16} />Record Receipt</button>}</div>
    {loadError && <AlertBanner type="error" title={loadError.unauthorized ? 'Access Denied' : 'Repayment Data Unavailable'} message={loadError.message} />}
    {accounts.length === 0 ? <div className="card text-center py-8 text-slate-400 text-sm">No loan accounts are available in your scope.</div> : <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="card p-0 overflow-hidden flex flex-col max-h-[80vh]"><div className="p-4 bg-slate-50 border-b border-slate-200"><p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Loan Accounts</p></div><div className="divide-y divide-slate-100 overflow-y-auto flex-1">{accounts.map(row => <button type="button" key={row.loan_account_id} onClick={() => setSelectedLoan(row.loan_account_id)} className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selectedLoan === row.loan_account_id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}><Banknote size={16} className="text-green-600 flex-shrink-0" /><div className="flex-1 min-w-0"><div className="font-semibold text-slate-900 num text-sm">{row.loan_account_number}</div><div className="text-xs text-slate-500 truncate">{row.member.display_name}</div><div className="text-xs text-slate-400 num">Principal O/S: {money(row.principal_outstanding)}</div></div><StatusBadge label={label(row.loan_account_status)} size="sm" /></button>)}</div></div>
      <div className="lg:col-span-2 card min-w-0"><div className="flex items-center justify-between mb-4"><div><h2 className="text-base font-bold text-slate-900 num">{loan?.loan_account_number}</h2><p className="text-sm text-slate-500">{loan?.member.display_name}</p></div>{loan && <StatusBadge label={label(loan.loan_account_status)} size="sm" />}</div>
        <Tabs tabs={[{ id: 'ledger', label: 'Repayment Ledger' }, { id: 'statements', label: 'Statement Exceptions' }, { id: 'subsidiary', label: 'Subsidiary Reconciliation' }]} activeIndex={activeTab} onChange={setActiveTab}>
          <RepaymentLedger rows={ledger} pagination={ledgerPagination} loading={surfaceLoading} error={loadError} onPage={page => void loadLoanSurfaces(selectedLoan, page, repaymentPagination.page)} />
          <StatementExceptions queues={statementQueues} canRead={canReadStatements} onPage={loadStatementQueue} />
          <SubsidiaryReconciliation rows={repayments.filter(row => row.repayment_source === 'subsidiary_deduction')} pagination={repaymentPagination} loading={surfaceLoading} error={loadError} onPage={page => void loadLoanSurfaces(selectedLoan, ledgerPagination.page, page)} />
        </Tabs>
      </div>
    </div>}
    {showPostModal && <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"><div className="bg-white rounded-xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto"><div className="p-5 border-b border-slate-200"><h3 className="text-lg font-bold text-slate-900">Record Direct Repayment</h3><p className="text-sm text-slate-500 mt-0.5">Confirm the retained bank receipt, SAP entry, and backend allocation.</p></div><div className="p-5 space-y-4">
      {postError && <AlertBanner type="error" title="Repayment Not Posted" message={postError} />}
      {postResult ? <div className="flex flex-col items-center gap-3 text-green-700 bg-green-50 border border-green-100 rounded-xl p-6 text-center"><CheckCircle2 size={32} /><div><div className="font-semibold text-green-900 text-lg">{postResult.replayed ? 'Exact Receipt Replay' : 'Receipt Posted and Allocated'}</div>{postResult.replayed ? <div className="text-sm mt-1">Canonical records were refreshed; no second SAP or allocation mutation was sent.</div> : postResult.allocation && <><div className="text-sm mt-1">{money(postResult.allocation.allocated_to_principal)} allocated to principal</div><div className="text-sm">{money(postResult.allocation.allocated_to_interest)} allocated to interest</div>{postResult.allocation.unallocated_amount !== '0.00' && <div className="text-sm">{money(postResult.allocation.unallocated_amount)} remains unallocated</div>}</>}</div></div> : <div className="grid grid-cols-2 gap-4"><div className="col-span-2"><label htmlFor="repayment-loan" className="field-label">Loan Account</label><select id="repayment-loan" value={selectedLoan} onChange={event => setSelectedLoan(event.target.value)} className="field-select">{accounts.map(row => <option key={row.loan_account_id} value={row.loan_account_id} disabled={!['active', 'partially_repaid', 'overdue', 'grace_period', 'extended'].includes(row.loan_account_status)}>{row.loan_account_number} — {row.member.display_name}</option>)}</select></div><div><label htmlFor="repayment-mode" className="field-label">Payment Mode</label><select id="repayment-mode" value={postMode} onChange={event => setPostMode(event.target.value as 'rtgs' | 'neft')} className="field-select"><option value="rtgs">RTGS</option><option value="neft">NEFT</option></select></div><div><label htmlFor="repayment-date" className="field-label">Payment Date</label><input id="repayment-date" type="date" value={postDate} onChange={event => setPostDate(event.target.value)} className="field-input" /></div><div><label htmlFor="repayment-amount" className="field-label">Amount Received (₹)</label><input id="repayment-amount" type="number" min="0.01" step="0.01" value={postAmount} onChange={event => setPostAmount(event.target.value)} className="field-input" /></div><div><label htmlFor="repayment-reference" className="field-label">Bank Reference / UTR</label><input id="repayment-reference" value={postRef} onChange={event => setPostRef(event.target.value)} className="field-input" /></div><div className="col-span-2"><label htmlFor="repayment-sap-reference" className="field-label">SAP Entry Reference</label><input id="repayment-sap-reference" value={sapRef} onChange={event => setSapRef(event.target.value)} className="field-input" /></div><div className="col-span-2 border border-slate-200 rounded-xl overflow-hidden"><div className="bg-slate-50 px-4 py-3 flex items-center justify-between"><span className="text-sm font-semibold text-slate-900">Allocation Authority</span><span className="text-[10px] text-slate-500 uppercase tracking-wide flex items-center gap-1"><FileText size={12} /> Backend Principal-First</span></div><p className="p-4 text-xs text-slate-500">Allocation values appear only after the canonical backend posts the retained SAP receipt.</p></div></div>}
    </div><div className="p-5 border-t border-slate-200 flex justify-end gap-3 bg-slate-50 rounded-b-xl"><button type="button" onClick={() => setShowPostModal(false)} className="btn-secondary">{postResult ? 'Close' : 'Cancel'}</button>{!postResult && <button type="button" className="btn-primary disabled:opacity-50" disabled={posting || !postAmount || Number(postAmount) <= 0 || !postDate || !postRef.trim() || !sapRef.trim()} onClick={() => void submit()}>{posting ? 'Posting…' : 'Post and Allocate'}</button>}</div></div></div>}
  </div>;
};

const StatementExceptions: React.FC<{
  queues: Record<StatementStatus, StatementQueueState>;
  canRead: boolean;
  onPage: (status: StatementStatus, page: number) => Promise<void>;
}> = ({ queues, canRead, onPage }) => {
  if (!canRead) return <AlertBanner type="error" title="Access Denied" message="Bank statement read permission is required." />;
  return <div className="space-y-6">{(['unmatched', 'exception'] as const).map(status => {
    const queue = queues[status];
    return <section key={status} aria-label={`${label(status)} statement lines`} className="space-y-4"><h3 className="text-sm font-semibold text-slate-700">{label(status)} statement lines</h3>
      {queue.loading && <div className="text-center py-8 text-slate-400 text-sm">Loading {status} statement lines…</div>}
      {!queue.loading && queue.error && <AlertBanner type="error" title={queue.error.unauthorized ? 'Access Denied' : `${label(status)} Statements Unavailable`} message={queue.error.message} />}
      {!queue.loading && !queue.error && queue.rows.length === 0 && <div className="text-center py-8 text-slate-400 text-sm">No {status} statement lines.</div>}
      {!queue.loading && !queue.error && queue.rows.length > 0 && <><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Line', 'Transaction Date', 'Value Date', 'Amount', 'Status', 'Reason'].map(column => <th key={column} className={`table-header ${column === 'Amount' ? 'text-right' : 'text-left'}`}>{column}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{queue.rows.map(row => <tr key={row.bank_statement_line_id}><td className="table-cell num">{row.line_number}</td><td className="table-cell">{date(row.transaction_date)}</td><td className="table-cell">{date(row.value_date)}</td><td className="table-cell text-right num">{money(row.amount)}</td><td className="table-cell"><StatusBadge label={label(row.match_status)} size="sm" /></td><td className="table-cell text-slate-600">{row.match_reason_code.replace(/_/g, ' ')}</td></tr>)}</tbody></table></div><PaginationControls pagination={queue.pagination} onPage={page => void onPage(status, page)} /></>}
    </section>;
  })}</div>;
};

const SubsidiaryReconciliation: React.FC<{
  rows: RepaymentProjection[];
  pagination: Pagination;
  loading: boolean;
  error: SurfaceError | null;
  onPage: (page: number) => void;
}> = ({ rows, pagination, loading, error, onPage }) => {
  if (loading) return <div className="text-center py-8 text-slate-400 text-sm">Loading subsidiary reconciliations…</div>;
  if (error) return <AlertBanner type="error" title={error.unauthorized ? 'Access Denied' : 'Subsidiary Reconciliation Unavailable'} message={error.message} />;
  if (rows.length === 0) return <div className="text-center py-8 text-slate-400 text-sm">No subsidiary deduction reconciliations for this loan.</div>;
  return <div className="space-y-4"><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Date', 'Transfer / Produce Reference', 'Amount', 'Principal', 'Interest', 'Reconciliation', 'Treasury', 'SAP'].map(column => <th key={column} className={`table-header ${['Amount', 'Principal', 'Interest'].includes(column) ? 'text-right' : 'text-left'}`}>{column}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{rows.map(row => <tr key={row.repayment_id}><td className="table-cell">{date(row.received_date)}</td><td className="table-cell"><div className="font-medium num">{row.subsidiary_reconciliation?.transfer_reference}</div><div className="text-xs text-slate-500 num">{row.subsidiary_reconciliation?.produce_payment_reference}</div></td><td className="table-cell text-right num">{money(row.amount_received)}</td><td className="table-cell text-right num">{money(row.allocation?.allocated_to_principal ?? null)}</td><td className="table-cell text-right num">{money(row.allocation?.allocated_to_interest ?? null)}</td><td className="table-cell"><StatusBadge label={label(row.subsidiary_reconciliation?.reconciliation_status ?? 'unknown')} size="sm" /></td><td className="table-cell"><StatusBadge label={label(row.subsidiary_reconciliation?.treasury_verification_status ?? 'unknown')} size="sm" /></td><td className="table-cell"><StatusBadge label={label(row.sap_posting_status)} size="sm" /></td></tr>)}</tbody></table></div><PaginationControls pagination={pagination} onPage={onPage} /></div>;
};

export default RepaymentsHub;
