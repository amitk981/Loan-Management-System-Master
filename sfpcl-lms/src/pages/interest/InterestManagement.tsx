import React, { useState } from 'react';
import {
  IndianRupee, Calendar, AlertTriangle, CheckCircle2,
  FileText, Download, TrendingUp, Clock, ArrowUpRight
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';

type InterestTab = 'accrual' | 'invoices' | 'capitalisation';

const accrualData = [
  { loanNo: 'LO00000042', borrower: 'Ganesh Thorat',   principal: 350000, rate: 12, daysInPeriod: 91, accrued: 10543, status: 'active',  dueDate: '2025-09-30' },
  { loanNo: 'LO00000044', borrower: 'Sunita Kamble',   principal: 200000, rate: 12, daysInPeriod: 91, accrued: 6024,  status: 'active',  dueDate: '2025-09-30' },
  { loanNo: 'LO00000045', borrower: 'Kiran Pawar',     principal: 150000, rate: 12, daysInPeriod: 91, accrued: 4527,  status: 'active',  dueDate: '2025-09-30' },
  { loanNo: 'LO00000038', borrower: 'Malti Shinde',    principal: 180000, rate: 14, daysInPeriod: 91, accrued: 6273,  status: 'overdue', dueDate: '2025-06-30' },
];

const invoices = [
  { id: 'INV-2025-001', loanNo: 'LO00000042', borrower: 'Ganesh Thorat', period: 'FY 2024–25', amount: 36000, status: 'sent',     sentOn: '2025-04-05', dueBy: '2025-04-30' },
  { id: 'INV-2025-002', loanNo: 'LO00000044', borrower: 'Sunita Kamble', period: 'FY 2024–25', amount: 24000, status: 'paid',     sentOn: '2025-04-05', dueBy: '2025-04-30' },
  { id: 'INV-2025-003', loanNo: 'LO00000038', borrower: 'Malti Shinde',  period: 'FY 2024–25', amount: 25200, status: 'overdue',  sentOn: '2025-04-05', dueBy: '2025-04-30' },
];

const InterestManagement: React.FC = () => {
  const { can } = useRole();
  const [activeTab, setActiveTab] = useState<InterestTab>('accrual');
  const [accrualPeriod, setAccrualPeriod] = useState('Q2 FY 2025–26 (Jul–Sep 2025)');
  const [capLoans, setCapLoans] = useState<string[]>([]);

  const totalAccrued = accrualData.reduce((sum, r) => sum + r.accrued, 0);
  const overdueInterest = accrualData.filter(r => r.status === 'overdue').reduce((sum, r) => sum + r.accrued, 0);

  const tabs: { id: InterestTab; label: string }[] = [
    { id: 'accrual',        label: 'Interest Accrual' },
    { id: 'invoices',       label: 'Yearly Invoices' },
    { id: 'capitalisation', label: 'Interest Capitalisation' },
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Interest Management</h1>
        <p className="text-sm text-slate-500 mt-1">Manage quarterly interest accruals, annual interest invoices, and post-April 30 capitalisation.</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Q2 Interest Accrued', value: `₹${totalAccrued.toLocaleString('en-IN')}`, icon: <TrendingUp size={16} />, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-100' },
          { label: 'Overdue Interest',    value: `₹${overdueInterest.toLocaleString('en-IN')}`, icon: <AlertTriangle size={16} />, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-100' },
          { label: 'Invoices Pending',    value: '1',    icon: <FileText size={16} />, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100' },
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
              <strong>Accrual Method:</strong> Interest accrues daily on outstanding principal at the agreed rate (12% p.a. standard, 14% p.a. for overdue). Posted quarterly to SAP. Per SOP Section 9.2 — unpaid interest after 30 April is capitalised (added to principal) in the next financial year.
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900">Quarterly Interest Accrual</h3>
                <div className="flex items-center gap-3 mt-2">
                  <select
                    value={accrualPeriod}
                    onChange={e => setAccrualPeriod(e.target.value)}
                    className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                  >
                    <option>Q2 FY 2025–26 (Jul–Sep 2025)</option>
                    <option>Q1 FY 2025–26 (Apr–Jun 2025)</option>
                    <option>Q4 FY 2024–25 (Jan–Mar 2025)</option>
                    <option>Q3 FY 2024–25 (Oct–Dec 2024)</option>
                  </select>
                </div>
              </div>
              {can('post_repayment') && (
                <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                  <CheckCircle2 size={15} />
                  Post to SAP
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Loan No.</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Borrower</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Principal O/S</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Rate</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Days</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Interest Accrued</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Due Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {accrualData.map(row => (
                    <tr key={row.loanNo} className={`hover:bg-slate-50 transition-colors ${row.status === 'overdue' ? 'bg-red-50/30' : ''}`}>
                      <td className="px-6 py-3 font-mono text-slate-700">{row.loanNo}</td>
                      <td className="px-4 py-3 text-slate-800">{row.borrower}</td>
                      <td className="px-4 py-3 text-right text-slate-700">₹{row.principal.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3 text-right text-slate-700">{row.rate}%</td>
                      <td className="px-4 py-3 text-right text-slate-700">{row.daysInPeriod}</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{row.accrued.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3"><StatusBadge label={row.status} size="sm" /></td>
                      <td className="px-4 py-3 text-slate-500 text-xs">{row.dueDate}</td>
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
              <strong>Annual Interest Invoices:</strong> Per SOP Section 9.3 — yearly interest invoices are to be sent to each borrower before 30 April. If interest remains unpaid by 30 April, it is capitalised (added to principal outstanding) in the next financial year.
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">FY 2024–25 Interest Invoices</h3>
              {can('post_repayment') && (
                <div className="flex gap-2">
                  <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                    <Download size={15} />
                    Export All
                  </button>
                  <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    <FileText size={15} />
                    Generate Bulk Invoices
                  </button>
                </div>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Invoice No.</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Loan</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Borrower</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Period</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Amount</th>
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
                      <td className="px-4 py-3">
                        <button className="text-xs text-green-700 font-medium hover:underline flex items-center gap-1">
                          <Download size={12} /> Download
                        </button>
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
              <strong>SOP Section 9.4 — Interest Capitalisation:</strong> If a borrower fails to pay the annual interest by 30 April, the unpaid interest is added to the principal outstanding for the next financial year. This triggers a recalculated repayment schedule. Credit Manager must approve capitalisation.
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
              <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
                <div><div className="text-red-600 text-xs">Current Principal</div><div className="font-semibold text-red-900">₹1,80,000</div></div>
                <div><div className="text-red-600 text-xs">Unpaid Interest</div><div className="font-semibold text-red-900">₹25,200</div></div>
                <div><div className="text-red-600 text-xs">New Principal (post-cap)</div><div className="font-semibold text-red-900">₹2,05,200</div></div>
                <div><div className="text-red-600 text-xs">Rate on New Principal</div><div className="font-semibold text-red-900">12% p.a.</div></div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Capitalisation Date</label>
                <input type="date" defaultValue="2025-05-01" className="w-full max-w-xs px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Authorisation Remarks (mandatory)</label>
                <textarea rows={3} placeholder="Credit Manager approval note for capitalisation…" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" />
              </div>
              <div className="flex items-center gap-2 text-amber-700 bg-amber-50 rounded-xl p-4 text-sm">
                <Clock size={16} className="flex-shrink-0" />
                Capitalisation will increase the principal to ₹2,05,200 and generate a revised repayment schedule. This action is irreversible without manual journal entries.
              </div>
              {can('do_appraisal') && (
                <div className="flex gap-3">
                  <button className="flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                    <ArrowUpRight size={16} />
                    Capitalise Unpaid Interest
                  </button>
                  <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                    <FileText size={16} />
                    Preview New Schedule
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Capitalisation History</h3>
            <div className="text-sm text-slate-500 text-center py-6">No prior capitalisation events on record</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterestManagement;
