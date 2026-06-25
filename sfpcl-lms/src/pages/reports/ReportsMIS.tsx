import React, { useState } from 'react';
import {
  BarChart2, Download, TrendingUp, TrendingDown, IndianRupee,
  FileText, Calendar, Filter, ChevronRight, PieChart, Users
} from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';

type ReportTab = 'portfolio' | 'dpd' | 'compliance' | 'member' | 'custom';

const ReportsMIS: React.FC = () => {
  const { can } = useRole();
  const [activeTab, setActiveTab] = useState<ReportTab>('portfolio');
  const [reportPeriod, setReportPeriod] = useState('Q1 FY 2025–26');

  if (!can('view_reports')) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center py-20 text-center">
          <BarChart2 size={40} className="text-slate-300 mb-4" />
          <h2 className="text-lg font-semibold text-slate-700 mb-2">Access Restricted</h2>
          <p className="text-sm text-slate-400">Reports are accessible to CFO, Credit Manager, Accounts, and Auditor roles.</p>
        </div>
      </div>
    );
  }

  const tabs: { id: ReportTab; label: string }[] = [
    { id: 'portfolio',  label: 'Portfolio Summary' },
    { id: 'dpd',        label: 'DPD & Aging Analysis' },
    { id: 'compliance', label: 'Compliance MIS' },
    { id: 'member',     label: 'Member Exposure' },
    { id: 'custom',     label: 'Custom Reports' },
  ];

  const portfolioMetrics = [
    { label: 'Total Loan Portfolio',     value: '₹2,42,00,000', trend: '+12%', up: true },
    { label: 'Active Loan Accounts',     value: '23',            trend: '+3',   up: true },
    { label: 'Total Disbursed (FY25)',   value: '₹85,00,000',    trend: '+18%', up: true },
    { label: 'Total Repaid (FY25)',      value: '₹48,00,000',    trend: '+22%', up: true },
    { label: 'Overdue Accounts',         value: '4',             trend: '-1',   up: false },
    { label: 'Overdue Amount',           value: '₹18,20,000',    trend: '+8%',  up: false },
    { label: 'Average Loan Size',        value: '₹4,20,000',     trend: '+5%',  up: true },
    { label: 'Section 186 Utilisation', value: '64%',            trend: '+4%',  up: false },
  ];

  const dpdBuckets = [
    { bucket: 'Current (0 DPD)',   count: 19, amount: 1820000, pct: '75.2%' },
    { bucket: '1–30 DPD',          count: 2,  amount: 210000,  pct: '8.7%'  },
    { bucket: '31–90 DPD',         count: 1,  amount: 350000,  pct: '14.5%' },
    { bucket: '91–365 DPD',        count: 1,  amount: 40000,   pct: '1.6%'  },
    { bucket: '1–2 Years',         count: 0,  amount: 0,       pct: '0%'    },
    { bucket: '> 2 Years',         count: 0,  amount: 0,       pct: '0%'    },
  ];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Reports & MIS Center</h1>
          <p className="text-sm text-slate-500 mt-1">Portfolio analytics, compliance reporting, DPD analysis and CFO MIS.</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={reportPeriod}
            onChange={e => setReportPeriod(e.target.value)}
            className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
          >
            <option>Q1 FY 2025–26</option>
            <option>FY 2024–25 Full Year</option>
            <option>Q4 FY 2024–25</option>
            <option>Q3 FY 2024–25</option>
          </select>
          <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Download size={15} />
            Export
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
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

      {activeTab === 'portfolio' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {portfolioMetrics.map(m => (
              <div key={m.label} className="bg-white border border-slate-200 rounded-xl p-4">
                <div className="text-xs text-slate-500 mb-1">{m.label}</div>
                <div className="text-xl font-bold text-slate-900">{m.value}</div>
                <div className={`flex items-center gap-1 text-xs mt-1 font-medium ${m.up ? 'text-green-600' : 'text-red-500'}`}>
                  {m.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  {m.trend} vs prior quarter
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Portfolio by Member Type</h3>
            <div className="space-y-3">
              {[
                { type: 'Individual Farmer',     count: 18, amount: 7200000, pct: 63 },
                { type: 'FPC (Farmer Producer Company)', count: 4, amount: 3600000, pct: 28 },
                { type: 'Producer Institution',  count: 1, amount: 1150000, pct: 9 },
              ].map(row => (
                <div key={row.type}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-700 font-medium">{row.type}</span>
                    <span className="text-slate-500">{row.count} loans · ₹{(row.amount / 100000).toFixed(1)}L · {row.pct}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: `${row.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Monthly Disbursement Trend (FY 2025–26)</h3>
            <div className="space-y-2">
              {[
                { month: 'Apr 2025', amount: 1500000 },
                { month: 'May 2025', amount: 2200000 },
                { month: 'Jun 2025', amount: 1800000 },
              ].map(row => (
                <div key={row.month} className="flex items-center gap-4">
                  <span className="text-sm text-slate-600 w-24 flex-shrink-0">{row.month}</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-6 relative overflow-hidden">
                    <div
                      className="bg-green-400 h-6 rounded-full flex items-center"
                      style={{ width: `${(row.amount / 2500000) * 100}%` }}
                    >
                      <span className="text-xs text-white font-medium pl-3">₹{(row.amount / 100000).toFixed(1)}L</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'dpd' && (
        <div className="space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900">DPD Bucket Analysis — {reportPeriod}</h3>
              <p className="text-xs text-slate-500 mt-0.5">Days Past Due analysis as per RBI asset classification methodology</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">DPD Bucket</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Account Count</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Outstanding (₹)</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">% of Portfolio</th>
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Bar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {dpdBuckets.map(row => (
                    <tr key={row.bucket} className={`hover:bg-slate-50 ${row.count > 0 && row.bucket !== 'Current (0 DPD)' ? 'bg-amber-50/30' : ''}`}>
                      <td className="px-6 py-3 font-medium text-slate-800">{row.bucket}</td>
                      <td className="px-4 py-3 text-right text-slate-700">{row.count}</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">
                        {row.amount > 0 ? `₹${(row.amount / 100000).toFixed(2)}L` : '—'}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-600">{row.pct}</td>
                      <td className="px-4 py-3 w-32">
                        <div className="w-full bg-slate-100 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${row.bucket === 'Current (0 DPD)' ? 'bg-green-500' : 'bg-red-400'}`}
                            style={{ width: row.pct }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">CFO Quarterly MIS Summary</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {[
                ['Portfolio at Risk (DPD > 0)', '24.8%'],
                ['Non-Performing Assets (DPD > 90)', '1.6%'],
                ['Provision Coverage Ratio', 'N/A — pending board approval'],
                ['Loan Loss Reserve', '₹0 (not yet provisioned)'],
                ['Recovery Rate',     '0% — recovery action initiated'],
                ['Write-Off Loans',   '0'],
              ].map(([k, v]) => (
                <div key={k}>
                  <div className="text-slate-500">{k}</div>
                  <div className="font-semibold text-slate-900 mt-0.5">{v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'compliance' && (
        <div className="space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Section 186 Compliance Summary</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-slate-700">Portfolio Outstanding vs Estimated 186 Cap</span>
                  <span className="font-semibold text-amber-700">64% utilised</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-4">
                  <div className="bg-amber-400 h-4 rounded-full" style={{ width: '64%' }} />
                </div>
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>₹0</span>
                  <span className="text-amber-600 font-medium">₹2.42Cr outstanding</span>
                  <span>Est. cap ₹3.78Cr</span>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                {[
                  ['FY 2024-25 Loans Issued', '₹1.85 Cr'],
                  ['NBFC Test Status',         'PASS'],
                  ['Annual Review Due',         'March 2026'],
                ].map(([k, v]) => (
                  <div key={k} className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500">{k}</div>
                    <div className="font-semibold text-slate-900 mt-0.5">{v}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">KYC Status Summary</h3>
            <div className="grid grid-cols-4 gap-3">
              {[
                { label: 'KYC Verified',  count: 128, color: 'text-green-600 bg-green-50' },
                { label: 'Re-KYC Due',    count: 12,  color: 'text-amber-600 bg-amber-50' },
                { label: 'KYC Expired',   count: 5,   color: 'text-red-600 bg-red-50' },
                { label: 'KYC Pending',   count: 2,   color: 'text-slate-600 bg-slate-50' },
              ].map(stat => (
                <div key={stat.label} className={`${stat.color} rounded-xl p-4 text-center`}>
                  <div className="text-2xl font-bold">{stat.count}</div>
                  <div className="text-xs mt-1 font-medium">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'member' && (
        <div className="space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
              <h3 className="font-semibold text-slate-900">Member Exposure Report</h3>
              <button className="flex items-center gap-2 text-sm text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">
                <Download size={14} />
                Export CSV
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Member</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Type</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Shares</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Eligible Limit</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Current Exposure</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Headroom</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {[
                    { name: 'Ganesh Thorat',    type: 'Individual', shares: 5, limit: 150000, exposure: 350000, risk: 'high' },
                    { name: 'Sunita Kamble',    type: 'Individual', shares: 3, limit: 90000,  exposure: 200000, risk: 'high' },
                    { name: 'Kisan FPC Ltd',    type: 'FPC',        shares: 50, limit: 1500000, exposure: 890000, risk: 'medium' },
                    { name: 'Vijay Patil',      type: 'Individual', shares: 8, limit: 240000, exposure: 350000, risk: 'high' },
                    { name: 'Radha Kisan Org',  type: 'FPC',        shares: 20, limit: 600000, exposure: 0,      risk: 'low' },
                  ].map(row => {
                    const headroom = row.limit - row.exposure;
                    return (
                      <tr key={row.name} className={`hover:bg-slate-50 ${row.risk === 'high' ? 'bg-red-50/20' : ''}`}>
                        <td className="px-6 py-3 font-medium text-slate-800">{row.name}</td>
                        <td className="px-4 py-3 text-slate-600">{row.type}</td>
                        <td className="px-4 py-3 text-right text-slate-700">{row.shares}</td>
                        <td className="px-4 py-3 text-right text-slate-700">₹{(row.limit/1000).toFixed(0)}K</td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{(row.exposure/1000).toFixed(0)}K</td>
                        <td className={`px-4 py-3 text-right font-semibold ${headroom < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {headroom < 0 ? `-₹${(Math.abs(headroom)/1000).toFixed(0)}K` : `₹${(headroom/1000).toFixed(0)}K`}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            row.risk === 'high' ? 'bg-red-100 text-red-700' :
                            row.risk === 'medium' ? 'bg-amber-100 text-amber-700' :
                            'bg-green-100 text-green-700'
                          }`}>{row.risk.charAt(0).toUpperCase() + row.risk.slice(1)}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'custom' && (
        <div className="max-w-2xl">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Filter size={16} className="text-green-600" />
              Custom Report Builder
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Report Type</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  <option>Loan Disbursement Summary</option>
                  <option>Repayment Collection Report</option>
                  <option>Overdue Loan Aging Report</option>
                  <option>Member KYC Status Report</option>
                  <option>Security Register Extract</option>
                  <option>Exception Register</option>
                  <option>Audit Trail Export</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">From Date</label>
                  <input type="date" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">To Date</label>
                  <input type="date" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Format</label>
                <div className="flex gap-3">
                  {['PDF', 'Excel', 'CSV'].map(fmt => (
                    <label key={fmt} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                      <input type="radio" name="format" defaultChecked={fmt === 'Excel'} className="accent-green-600" />
                      {fmt}
                    </label>
                  ))}
                </div>
              </div>
              <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                <BarChart2 size={16} />
                Generate Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsMIS;
