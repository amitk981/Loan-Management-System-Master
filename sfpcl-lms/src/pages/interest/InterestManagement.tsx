import React, { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, FileText, TrendingUp } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError } from '../../services/authSession';
import { fetchAllLoanAccounts, type LoanAccountProjection } from '../../services/loanAccountsApi';
import { capitaliseInterest, canCapitaliseInterest, canGenerateAccrual, canGenerateInvoice, fetchAllInterestInvoices, generateInterestInvoice, PortfolioAccrualError, previewInterestCapitalisations, runPortfolioInterestAccrual, type AccrualRunProjection, type CapitalisationPreview, type InterestCapitalisationProjection, type InterestInvoiceProjection } from '../../services/servicingApi';
import { formatMoney } from '../../utils/formatMoney';

type Tab = 'accrual' | 'invoices' | 'capitalisation';
type UiError = { title: string; message: string; fields?: Record<string, string> };
const label = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase());
const errorState = (error: unknown, fallback: string): UiError => error instanceof AuthSessionError
  ? { title: [401, 403].includes(error.status || 0) ? 'Access Denied' : error.status === 400 ? 'Validation Error' : fallback, message: error.message, fields: error.fieldErrors }
  : { title: fallback, message: error instanceof Error ? error.message : fallback };

const InterestManagement: React.FC = () => {
  const { currentUser } = useRole();
  const [tab, setTab] = useState<Tab>('accrual');
  const [accounts, setAccounts] = useState<LoanAccountProjection[]>([]);
  const [invoices, setInvoices] = useState<InterestInvoiceProjection[]>([]);
  const [accountPages, setAccountPages] = useState(1);
  const [invoicePages, setInvoicePages] = useState(1);
  const [selectedLoan, setSelectedLoan] = useState('');
  const [month, setMonth] = useState('2026-06');
  const [financialYear, setFinancialYear] = useState('FY2026-27');
  const [capitalisationDate, setCapitalisationDate] = useState('2027-05-01');
  const [accrual, setAccrual] = useState<AccrualRunProjection | null>(null);
  const [preview, setPreview] = useState<CapitalisationPreview | null>(null);
  const [capitalisation, setCapitalisation] = useState<InterestCapitalisationProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<UiError | null>(null);
  const keys = useRef(new Map<string, string>());
  const keyFor = (operation: string) => {
    if (!keys.current.has(operation)) keys.current.set(operation, `${operation}-${crypto.randomUUID()}`);
    return keys.current.get(operation)!;
  };
  const accountName = (id: string) => accounts.find(row => row.loan_account_id === id);
  const refreshInvoices = async () => {
    const collection = await fetchAllInterestInvoices();
    setInvoices(collection.items);
    setInvoicePages(collection.totalPages);
  };

  useEffect(() => {
    let active = true; setLoading(true); setError(null);
    void Promise.all([fetchAllLoanAccounts(), fetchAllInterestInvoices()]).then(([loanCollection, invoiceCollection]) => {
      if (!active) return; setAccounts(loanCollection.items); setAccountPages(loanCollection.totalPages); setSelectedLoan(loanCollection.items[0]?.loan_account_id ?? ''); setInvoices(invoiceCollection.items); setInvoicePages(invoiceCollection.totalPages);
    }).catch(reason => active && setError(errorState(reason, 'Interest Management Unavailable'))).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const act = async (operation: () => Promise<void>) => {
    setWorking(true); setError(null);
    try { await operation(); } catch (reason) { setError(errorState(reason, 'Interest Operation Failed')); } finally { setWorking(false); }
  };
  const runAccrual = () => act(async () => {
    try {
      setAccrual(await runPortfolioInterestAccrual(month, accounts.map(row => row.loan_account_id), keyFor(`accrual:${month}`)));
    } catch (reason) {
      if (reason instanceof PortfolioAccrualError) setAccrual(reason.completedRun);
      throw reason;
    }
  });
  const generateInvoice = () => act(async () => { await generateInterestInvoice(selectedLoan, financialYear, keyFor(`invoice:${selectedLoan}:${financialYear}`)); await refreshInvoices(); });
  const loadPreview = () => act(async () => setPreview(await previewInterestCapitalisations(financialYear, capitalisationDate)));
  const postCapitalisation = () => act(async () => { const result = await capitaliseInterest(selectedLoan, financialYear, capitalisationDate, keyFor(`capitalisation:${selectedLoan}:${financialYear}:${capitalisationDate}`)); setCapitalisation(result); setPreview(await previewInterestCapitalisations(financialYear, capitalisationDate)); });

  if (loading) return <div className="p-6"><div className="card text-sm text-slate-500">Loading canonical interest records…</div></div>;
  if (error?.title === 'Access Denied' && accounts.length === 0) return <div className="p-6"><AlertBanner type="error" title={error.title} message={error.message} /></div>;
  const previewRow = preview?.financial_year === financialYear && preview.as_of_date === capitalisationDate ? preview.results.find(row => row.loan_account_id === selectedLoan) : undefined;
  return <div className="p-6 space-y-6">
    <div><h1 className="text-xl font-bold text-slate-900">Interest Management</h1><p className="text-sm text-slate-500 mt-1">Canonical monthly accrual, annual invoice, and post–30 April capitalisation records.</p></div>
    {error && <div className="space-y-2"><AlertBanner type="error" title={error.title} message={error.message} />{error.fields && <div className="card text-sm text-red-700">{Object.entries(error.fields).map(([field, message]) => <div key={field}>{label(field)}: {message}</div>)}</div>}</div>}
    {capitalisation && <AlertBanner type="success" title="Capitalisation Posted" message={`${formatMoney(capitalisation.unpaid_interest_amount)} was capitalised. Canonical new principal: ${formatMoney(capitalisation.new_principal_amount)}.`} />}
    <div className="border-b border-slate-200"><div className="flex gap-1">{(['accrual', 'invoices', 'capitalisation'] as Tab[]).map(value => <button key={value} onClick={() => setTab(value)} className={`px-4 py-2.5 text-sm font-medium border-b-2 ${tab === value ? 'border-green-600 text-green-700' : 'border-transparent text-slate-500'}`}>{value === 'accrual' ? 'Monthly Interest Accrual' : value === 'invoices' ? 'Yearly Invoices' : 'Interest Capitalisation'}</button>)}</div></div>
    {tab === 'accrual' && <section className="space-y-4">
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex gap-3 text-sm text-blue-800"><TrendingUp size={16} /><span>Amounts, rates, days, outcomes, and SAP status below are returned by the backend interest owner.</span></div>
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden"><div className="px-6 py-4 border-b border-slate-100 flex flex-wrap items-end gap-3"><div><label htmlFor="accrual-month" className="field-label">Accrual month</label><input id="accrual-month" type="month" value={month} onChange={event => setMonth(event.target.value)} className="field-input" /></div><div className="text-sm text-slate-500">{accounts.length} canonical loan accounts across {accountPages} {accountPages === 1 ? 'page' : 'pages'}; monthly accrual uses {Math.ceil(accounts.length / 100)} backend-authorised {accounts.length <= 100 ? 'batch' : 'batches'}.</div>{canGenerateAccrual(currentUser.availableActions) && <button disabled={working || accounts.length === 0} onClick={runAccrual} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50">Run Monthly Accrual</button>}</div><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Loan', 'Outcome', 'Interest Accrued', 'Persisted', 'Reason'].map(value => <th key={value} className="table-header text-left">{value}</th>)}</tr></thead><tbody>{!accrual?.results.length && <tr><td colSpan={5} className="table-cell py-10 text-center text-slate-400">No canonical accrual run has been loaded.</td></tr>}{accrual?.results.map(row => <tr key={row.loan_account_id}><td className="table-cell">{accountName(row.loan_account_id)?.loan_account_number ?? row.loan_account_id}</td><td className="table-cell"><StatusBadge label={label(row.outcome)} size="sm" /></td><td className="table-cell num font-semibold">{formatMoney(row.interest_accrued_amount ?? null)}</td><td className="table-cell">{row.persisted ? 'Yes' : 'No'}</td><td className="table-cell">{label(row.reason ?? 'none')}</td></tr>)}</tbody></table></div>
    </section>}
    {tab === 'invoices' && <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 flex gap-3 text-sm text-amber-800"><FileText size={16} /><strong>Annual invoices are due by 30 April. Unpaid invoices after 30 April route to capitalisation.</strong></div>}
    {tab === 'capitalisation' && <div className="bg-violet-50 border border-violet-100 rounded-xl p-4 flex gap-3 text-sm text-violet-800"><ArrowUpRight size={16} /><strong>Unpaid interest after 30 April is added to principal and recalculates the repayment schedule.</strong></div>}
    {tab === 'invoices' && <section className="space-y-4"><div className="bg-white border border-slate-200 rounded-xl overflow-hidden"><div className="px-6 py-4 border-b border-slate-100 flex flex-wrap items-end justify-between gap-3"><div><label htmlFor="invoice-loan" className="field-label">Loan account</label><select id="invoice-loan" value={selectedLoan} onChange={event => setSelectedLoan(event.target.value)} className="field-select">{accounts.map(row => <option key={row.loan_account_id} value={row.loan_account_id}>{row.loan_account_number}</option>)}</select></div><div><label htmlFor="invoice-year" className="field-label">Financial year</label><input id="invoice-year" value={financialYear} onChange={event => setFinancialYear(event.target.value)} className="field-input" /></div><div className="text-sm text-slate-500">{invoices.length} canonical invoices across {invoicePages} {invoicePages === 1 ? 'page' : 'pages'}.</div>{canGenerateInvoice(currentUser.availableActions) && <button disabled={working || !selectedLoan} onClick={generateInvoice} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"><FileText size={15} className="inline mr-2" />Generate Invoice</button>}</div><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Invoice', 'Loan / Member', 'Period', 'Amount', 'Status', 'Delivery'].map(value => <th key={value} className="table-header text-left">{value}</th>)}</tr></thead><tbody>{invoices.length === 0 && <tr><td colSpan={6} className="table-cell py-10 text-center text-slate-400">No interest invoices are available in your scope.</td></tr>}{invoices.map(row => <tr key={row.interest_invoice_id}><td className="table-cell font-mono">{row.invoice_number}</td><td className="table-cell">{accountName(row.loan_account_id)?.loan_account_number ?? row.loan_account_id}<div className="text-xs text-slate-500">{accountName(row.loan_account_id)?.member.display_name ?? 'Scoped member'}</div></td><td className="table-cell">{row.financial_year}</td><td className="table-cell num font-semibold">{formatMoney(row.interest_amount)}</td><td className="table-cell"><StatusBadge label={label(row.invoice_status)} size="sm" /></td><td className="table-cell"><StatusBadge label={label(row.delivery_status ?? 'not issued')} size="sm" /></td></tr>)}</tbody></table></div></section>}
    {tab === 'capitalisation' && <section className="space-y-4 max-w-2xl"><div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4"><div><label htmlFor="capital-loan" className="field-label">Loan account</label><select id="capital-loan" value={selectedLoan} onChange={event => setSelectedLoan(event.target.value)} className="field-select">{accounts.map(row => <option key={row.loan_account_id} value={row.loan_account_id}>{row.loan_account_number}</option>)}</select></div><div><label htmlFor="capital-year" className="field-label">Financial year</label><input id="capital-year" value={financialYear} onChange={event => setFinancialYear(event.target.value)} className="field-input" /></div><div><label htmlFor="capital-date" className="field-label">As-of / posting date</label><input id="capital-date" type="date" value={capitalisationDate} onChange={event => setCapitalisationDate(event.target.value)} className="field-input" /></div>{canCapitaliseInterest(currentUser.availableActions) && <div className="flex flex-wrap gap-3"><button disabled={working} onClick={loadPreview} className="border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium">Preview Capitalisation</button><button disabled={working || !previewRow?.eligible} onClick={postCapitalisation} className="bg-violet-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"><ArrowUpRight size={15} className="inline mr-2" />Post Capitalisation</button></div>}{previewRow ? <div className="border border-red-200 bg-red-50 rounded-xl p-4"><div className="font-semibold text-red-800">{accountName(previewRow.loan_account_id)?.loan_account_number} — {label(previewRow.reason_code)}</div><div className="grid grid-cols-3 gap-3 mt-3 text-sm"><div>Current Principal<br /><strong>{formatMoney(previewRow.old_principal_amount)}</strong></div><div>Unpaid Interest<br /><strong>{formatMoney(previewRow.unpaid_interest_amount)}</strong></div><div>New Principal<br /><strong>{formatMoney(previewRow.new_principal_amount)}</strong></div></div></div> : <div className="border border-slate-200 rounded-xl text-sm text-slate-400 text-center py-8">Run the backend preview to see capitalisation eligibility and values.</div>}</div></section>}
  </div>;
};

export default InterestManagement;
