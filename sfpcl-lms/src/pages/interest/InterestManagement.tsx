import React, { useState } from 'react';
import {
  IndianRupee, Calendar, AlertTriangle, CheckCircle2,
  FileText, Download, TrendingUp, Clock, ArrowUpRight, Lock, Send
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';

type InterestTab = 'accrual' | 'invoices' | 'capitalisation' | 'rate_history';

const accrualData = [
  { loanNo: 'LO00000042', borrower: 'Ganesh Thorat',   principal: 350000, rate: 12, daysInPeriod: 30, accrued: 3452, status: 'active',  dueDate: '2025-09-30', sapStatus: 'pending', postedDate: '-' },
  { loanNo: 'LO00000044', borrower: 'Sunita Kamble',   principal: 200000, rate: 12, daysInPeriod: 30, accrued: 1972, status: 'active',  dueDate: '2025-09-30', sapStatus: 'posted', postedDate: '2025-09-28' },
  { loanNo: 'LO00000045', borrower: 'Kiran Pawar',     principal: 150000, rate: 12, daysInPeriod: 30, accrued: 1479, status: 'active',  dueDate: '2025-09-30', sapStatus: 'pending', postedDate: '-' },
  { loanNo: 'LO00000038', borrower: 'Malti Shinde',    principal: 180000, rate: 14, daysInPeriod: 30, accrued: 2071, status: 'overdue', dueDate: '2025-06-30', sapStatus: 'posted', postedDate: '2025-09-28' },
];

const invoices = [
  { id: 'INV-2025-001', loanNo: 'LO00000042', borrower: 'Ganesh Thorat', period: 'FY 2024–25', amount: 36000, status: 'sent',     sentOn: '2025-04-05', dueBy: '2025-04-30' },
  { id: 'INV-2025-002', loanNo: 'LO00000044', borrower: 'Sunita Kamble', period: 'FY 2024–25', amount: 24000, status: 'paid',     sentOn: '2025-04-05', dueBy: '2025-04-30' },
  { id: 'INV-2025-003', loanNo: 'LO00000038', borrower: 'Malti Shinde',  period: 'FY 2024–25', amount: 25200, status: 'overdue',  sentOn: '2025-04-05', dueBy: '2025-04-30' },
];

const InterestManagement: React.FC = () => {
  const { currentUser } = useRole();
  const [activeTab, setActiveTab] = useState<InterestTab>('accrual');
  const [accrualPeriod, setAccrualPeriod] = useState('September 2025');
  
  const role = currentUser.role;
  const isAdmin = role === 'admin';
  const isAccounts = isAdmin || role.includes('finance') || role.includes('account');
  const isSales = isAdmin || role.includes('field') || role.includes('sales');
  const isCredit = isAdmin || role.includes('credit');

  const [capRemarks, setCapRemarks] = useState('');
  const [sapPosted, setSapPosted] = useState(false);

  const totalAccrued = accrualData.reduce((sum, r) => sum + r.accrued, 0);
  const sapPendingCount = accrualData.filter(r => r.sapStatus === 'pending').length;

  const tabs: { id: InterestTab; label: string }[] = [
    { id: 'accrual',        label: 'Monthly Interest Accrual' },
    { id: 'invoices',       label: 'Yearly Invoices' },
    { id: 'capitalisation', label: 'Interest Capitalisation' },
    { id: 'rate_history',   label: 'Interest Rate History' },
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Interest Management</h1>
        <p className="text-sm text-slate-500 mt-1">Manage monthly interest accruals, annual interest invoices, and post–30 April capitalisation.</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Current Month Accrued', value: `₹${totalAccrued.toLocaleString('en-IN')}`, icon: <TrendingUp size={16} />, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-100' },
          { label: 'Accrual Posting Due', value: sapPendingCount.toString(), icon: <AlertTriangle size={16} />, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-100' },
          { label: 'Invoices Pending', value: '1', icon: <FileText size={16} />, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100' },
          { label: 'Pending Capitalisation', value: '1', icon: <ArrowUpRight size={16} />, color: 'text-violet-700', bg: 'bg-violet-50', border: 'border-violet-100' },
        ].map(kpi => (
          <div key={kpi.label} className={`${kpi.bg} ${kpi.border} border rounded-xl p-4`}>
            <div className={kpi.color}>{kpi.icon}</div>
            <div className="text-xl font-bold text-slate-900 mt-2">{kpi.value}</div>
            <div className="text-xs text-slate-600 mt-0.5">{kpi.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Interest Accrual */}
      {activeTab === 'accrual' && (
        <div className="space-y-5">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-start gap-3 text-sm text-blue-800">
            <TrendingUp size={16} className="mt-0.5 flex-shrink-0 text-blue-600" />
            <div>
              <strong>Accrual method:</strong> Interest is calculated using configured rate versions and posted monthly to SAP.
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold text-slate-900">Monthly Interest Accrual</h3>
                <div className="flex items-center gap-3 mt-2">
                  <select
                    value={accrualPeriod}
                    onChange={e => setAccrualPeriod(e.target.value)}
                    className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                  >
                    <option>September 2025</option>
                    <option>August 2025</option>
                    <option>July 2025</option>
                  </select>
                </div>
              </div>
              <div>
                {isAccounts || isCredit ? (
                  sapPosted ? (
                    <button disabled className="flex items-center gap-2 bg-slate-100 text-slate-500 px-4 py-2 rounded-lg text-sm font-medium cursor-not-allowed">
                      <CheckCircle2 size={15} className="text-green-600" /> SAP Posted
                    </button>
                  ) : (
                    <button onClick={() => setSapPosted(true)} className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                      <CheckCircle2 size={15} />
                      Mark SAP Posted
                    </button>
                  )
                ) : (
                  <button disabled className="flex items-center gap-2 bg-slate-100 text-slate-400 px-4 py-2 rounded-lg text-sm font-medium cursor-not-allowed">
                    <Lock size={14} /> Mark SAP Posted
                  </button>
                )}
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Loan No.</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Borrower</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Principal Balance</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Rate</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Days</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Interest Accrued</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">SAP Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Posted Date / Due Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {accrualData.map(row => (
                    <tr key={row.loanNo} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-3 font-mono text-slate-700">
                        <div className="flex items-center gap-2">
                          {row.loanNo}
                          {row.status === 'overdue' && <span className="bg-red-100 text-red-700 text-[10px] px-1.5 py-0.5 rounded-sm font-bold uppercase">Overdue</span>}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-slate-800">{row.borrower}</td>
                      <td className="px-4 py-3 text-right text-slate-700">₹{row.principal.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3 text-right text-slate-700">{row.rate}%</td>
                      <td className="px-4 py-3 text-right text-slate-700">{row.daysInPeriod}</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{row.accrued.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3">
                        {row.sapStatus === 'posted' ? <span className="text-green-600 font-medium flex items-center gap-1"><CheckCircle2 size={14}/> Posted</span> : <span className="text-amber-600 font-medium flex items-center gap-1"><Clock size={14}/> Pending</span>}
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-xs">{row.sapStatus === 'posted' ? row.postedDate : `Due: ${row.dueDate}`}</td>
                    </tr>
                  ))}
                  <tr className="bg-slate-100 font-semibold">
                    <td colSpan={5} className="px-6 py-3 text-slate-700">Total</td>
                    <td className="px-4 py-3 text-right text-slate-900">₹{totalAccrued.toLocaleString('en-IN')}</td>
                    <td colSpan={2}></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Yearly Invoices */}
      {activeTab === 'invoices' && (
        <div className="space-y-5">
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 flex items-start gap-3 text-sm text-amber-800">
            <FileText size={16} className="mt-0.5 flex-shrink-0 text-amber-600" />
            <div>
              <strong>Annual invoices are due by 30 April. Unpaid invoices after 30 April route to capitalisation.</strong>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <h3 className="font-semibold text-slate-900">FY 2024–25 Interest Invoices</h3>
              <div className="flex gap-2">
                <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                  <Download size={15} />
                  Export All
                </button>
                {isSales && (
                  <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    <FileText size={15} />
                    Generate Invoice Batch / Issue Invoices
                  </button>
                )}
                {isAccounts && !isSales && (
                  <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    <FileText size={15} />
                    Review Invoice Batch
                  </button>
                )}
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Invoice No.</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Loan</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Borrower</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Period</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Invoice Amount</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Due By</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {invoices.map(inv => (
                    <tr key={inv.id} className={`hover:bg-slate-50 transition-colors ${inv.status === 'overdue' ? 'bg-red-50/30' : ''}`}>
                      <td className="px-6 py-3 font-mono text-sm text-slate-700">{inv.id}</td>
                      <td className="px-4 py-3 font-mono text-slate-600">{inv.loanNo}</td>
                      <td className="px-4 py-3 text-slate-800">{inv.borrower}</td>
                      <td className="px-4 py-3 text-slate-600">{inv.period}</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{inv.amount.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3"><StatusBadge label={inv.status} size="sm" /></td>
                      <td className="px-4 py-3 text-slate-500 text-xs">{inv.dueBy}</td>
                      <td className="px-4 py-3 flex items-center gap-3">
                        <button className="text-xs text-green-700 font-medium hover:underline flex items-center gap-1">
                          <Download size={12} /> Download
                        </button>
                        {isCredit && inv.status === 'overdue' && (
                          <button className="text-xs text-amber-700 font-medium hover:underline flex items-center gap-1">
                            <Send size={12} /> Send Reminder
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Interest Capitalisation */}
      {activeTab === 'capitalisation' && (
        <div className="space-y-5 max-w-2xl">
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-4 flex items-start gap-3 text-sm text-violet-800">
            <ArrowUpRight size={16} className="mt-0.5 flex-shrink-0 text-violet-600" />
            <div>
              <strong>Unpaid interest after 30 April is added to principal and recalculates the repayment schedule.</strong>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Pending Capitalisation — FY 2024–25</h3>
            <div className="border border-red-200 bg-red-50 rounded-xl p-4 mb-5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle size={16} className="text-red-600" />
                    <span className="font-semibold text-red-800">LO00000038 — Malti Shinde</span>
                  </div>
                  <div className="text-xs text-red-600 ml-6">Interest of ₹25,200 unpaid as of 30 April 2025</div>
                </div>
                <StatusBadge label="overdue" />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-sm bg-white/50 p-3 rounded-lg">
                <div><div className="text-slate-500 text-xs">Current Principal</div><div className="font-semibold text-slate-900">₹1,80,000</div></div>
                <div><div className="text-slate-500 text-xs">Unpaid Interest</div><div className="font-semibold text-slate-900">₹25,200</div></div>
                <div><div className="text-slate-500 text-xs">New Principal</div><div className="font-semibold text-slate-900">₹2,05,200</div></div>
                <div><div className="text-slate-500 text-xs">Rate Version Used</div><div className="font-semibold text-slate-900">v2.1 (12%)</div></div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3 text-sm px-1">
                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-amber-500"></div><span className="text-slate-600 text-xs font-medium">Approval Status: Pending</span></div>
                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-amber-500"></div><span className="text-slate-600 text-xs font-medium">Borrower Intimation: Pending</span></div>
                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-slate-300"></div><span className="text-slate-600 text-xs font-medium">Ledger Posting: Not Started</span></div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Capitalisation Date</label>
                <input type="date" defaultValue="2025-05-01" className="w-full max-w-xs px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  {isCredit ? 'Enter approval or posting remarks (mandatory)' : 'Approval required from configured approver'}
                </label>
                <textarea 
                  rows={3} 
                  disabled={!isCredit}
                  value={capRemarks}
                  onChange={e => setCapRemarks(e.target.value)}
                  placeholder={isCredit ? "Enter remarks..." : "Approval required from configured approver"} 
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none disabled:bg-slate-50" 
                />
              </div>
              <div className="flex items-start gap-2 text-amber-800 bg-amber-50 border border-amber-100 rounded-xl p-4 text-sm">
                <Clock size={16} className="flex-shrink-0 mt-0.5" />
                This will update principal, create a ledger entry, recalculate the repayment schedule, and queue borrower intimation.
              </div>
              <div className="flex flex-wrap gap-3">
                {isCredit ? (
                  <>
                    <button disabled={!capRemarks} className="flex items-center gap-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:hover:bg-violet-600 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                      <ArrowUpRight size={16} />
                      Approve & Post Capitalisation
                    </button>
                    <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                      <FileText size={16} />
                      Preview New Schedule & Intimation
                    </button>
                  </>
                ) : (
                  <button disabled className="flex items-center gap-2 bg-slate-100 text-slate-400 px-5 py-2.5 rounded-lg text-sm font-semibold cursor-not-allowed">
                    <Lock size={16} />
                    Submit for Approval
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Capitalisation History</h3>
            <div className="text-sm text-slate-500 text-center py-6">No prior capitalisation events on record</div>
          </div>
        </div>
      )}

      {/* Interest Rate History */}
      {activeTab === 'rate_history' && (
        <div className="space-y-5">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-start gap-3 text-sm text-blue-800">
            <IndianRupee size={16} className="mt-0.5 flex-shrink-0 text-blue-600" />
            <div>
              <strong>Interest rate versions are configured by Senior Management and approved by the Board.</strong> Changes apply to new disbursements from the effective date.
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Interest Rate Versions</h3>
              <span className="text-xs text-slate-500 bg-slate-100 px-3 py-1 rounded-full">All loan types</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Version</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Loan Type</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Short-Term Rate</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Long-Term Rate</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Penal Rate</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Effective From</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Effective To</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Approved By</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {[
                    { version: 'v3.0', shortRate: 12.5, longRate: 11.0, penal: 2.0, from: '01 Apr 2026', to: '—', status: 'active', approvedBy: 'Board — 28 Mar 2026' },
                    { version: 'v2.2', shortRate: 12.0, longRate: 11.0, penal: 2.0, from: '01 Oct 2025', to: '31 Mar 2026', status: 'superseded', approvedBy: 'Board — 26 Sep 2025' },
                    { version: 'v2.1', shortRate: 12.0, longRate: 10.5, penal: 2.0, from: '01 Apr 2025', to: '30 Sep 2025', status: 'superseded', approvedBy: 'Board — 29 Mar 2025' },
                    { version: 'v2.0', shortRate: 11.5, longRate: 10.0, penal: 2.0, from: '01 Apr 2024', to: '31 Mar 2025', status: 'superseded', approvedBy: 'Board — 30 Mar 2024' },
                    { version: 'v1.0', shortRate: 11.0, longRate: 9.5,  penal: 2.0, from: '01 Apr 2023', to: '31 Mar 2024', status: 'archived',   approvedBy: 'Board — 28 Mar 2023' },
                  ].map(row => (
                    <tr key={row.version} className={`hover:bg-slate-50 transition-colors ${row.status === 'active' ? 'bg-green-50/30' : ''}`}>
                      <td className="px-6 py-3 font-semibold text-slate-800">{row.version}</td>
                      <td className="px-4 py-3 text-slate-600">All Members</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">{row.shortRate}%</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">{row.longRate}%</td>
                      <td className="px-4 py-3 text-right text-red-700 font-semibold">+{row.penal}%</td>
                      <td className="px-4 py-3 text-slate-600">{row.from}</td>
                      <td className="px-4 py-3 text-slate-500">{row.to}</td>
                      <td className="px-4 py-3"><StatusBadge label={row.status} size="sm" type={row.status === 'active' ? 'success' : 'slate'} /></td>
                      <td className="px-4 py-3 text-slate-500 text-xs">{row.approvedBy}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterestManagement;
