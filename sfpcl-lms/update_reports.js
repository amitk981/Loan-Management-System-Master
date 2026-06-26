const fs = require('fs');

const file = 'src/pages/reports/ReportsMIS.tsx';
let code = fs.readFileSync(file, 'utf8');

// Imports
code = code.replace(
  `import { useRole } from '../../contexts/RoleContext';`,
  `import { useRole } from '../../contexts/RoleContext';\nimport { dashboardStats } from '../../data/mockData';\n\nconst fmt = (n: number) => '₹' + n.toLocaleString('en-IN');`
);

// Tab and report copy
code = code.replace(`label: 'DPD & Aging Analysis'`, `label: 'DPD & Ageing Analysis'`);
code = code.replace(`label: 'Portfolio b Member Type'`, `label: 'Portfolio by member type'`);
code = code.replace(`Portfolio by Member Type`, `Disbursement by member type`);
code = code.replace(`CFO Quarterly MIS Summary`, `CFO quarterly MIS summary`);

code = code.replace(
  `{ label: 'Total Disbursed (FY25)',   value: '₹85,00,000',    trend: '+18%', up: true },
    { label: 'Total Repaid (FY25)',      value: '₹48,00,000',    trend: '+22%', up: true },`,
  `{ label: \`Total disbursed — \${reportPeriod}\`,   value: '₹85,00,000',    trend: '+18%', up: true },
    { label: \`Total repaid — \${reportPeriod}\`,      value: '₹48,00,000',    trend: '+22%', up: true },`
);

// Portfolio Summary data consistency
code = code.replace(
  `{ label: 'Overdue Amount',           value: '₹18,20,000',    trend: '+8%',  up: false },
    { label: 'Average Loan Size',        value: '₹4,20,000',     trend: '+5%',  up: true },
    { label: 'Section 186 Utilisation', value: '64%',            trend: '+4%',  up: false },`,
  `{ label: 'Overdue Amount',           value: '₹60,00,000',    trend: '+8%',  up: false },
    { label: 'Average loan size',        value: fmt(Math.round(24200000 / 23)),     trend: '+5%',  up: true },
    { label: 'Section 186 Utilisation', value: \`\${dashboardStats.sectionUtilisation}%\`,            trend: '+4%',  up: false },`
);

// Portfolio by member type amounts (to equal 242L)
code = code.replace(
  `[
                { type: 'Individual Farmer',     count: 18, amount: 7200000, pct: 63 },
                { type: 'FPC (Farmer Producer Company)', count: 4, amount: 3600000, pct: 28 },
                { type: 'Producer Institution',  count: 1, amount: 1150000, pct: 9 },
              ]`,
  `[
                { type: 'Individual Farmer',     count: 18, amount: 18900000, pct: 78 },
                { type: 'FPC (Farmer Producer Company)', count: 4, amount: 4200000, pct: 17 },
                { type: 'Producer Institution',  count: 1, amount: 1100000, pct: 5 },
              ]`
);

// Monthly Disbursement Trend amounts (to equal 85L)
code = code.replace(
  `[
                { month: 'Apr 2025', amount: 1500000 },
                { month: 'May 2025', amount: 2200000 },
                { month: 'Jun 2025', amount: 1800000 },
              ]`,
  `[
                { month: 'Apr 2025', amount: 2500000 },
                { month: 'May 2025', amount: 3200000 },
                { month: 'Jun 2025', amount: 2800000 },
              ]`
);
code = code.replace(`{(row.amount / 2500000) * 100}%`, `{(row.amount / 3500000) * 100}%`);

// DPD amounts (to equal 2.42Cr)
code = code.replace(
  `const dpdBuckets = [
    { bucket: 'Current (0 DPD)',   count: 19, amount: 1820000, pct: '75.2%' },
    { bucket: '1–30 DPD',          count: 2,  amount: 210000,  pct: '8.7%'  },
    { bucket: '31–90 DPD',         count: 1,  amount: 350000,  pct: '14.5%' },
    { bucket: '91–365 DPD',        count: 1,  amount: 40000,   pct: '1.6%'  },
    { bucket: '1–2 Years',         count: 0,  amount: 0,       pct: '0%'    },
    { bucket: '> 2 Years',         count: 0,  amount: 0,       pct: '0%'    },
  ];`,
  `const dpdBuckets = [
    { bucket: 'Current (0 DPD)',   count: 19, amount: 18200000, pct: '75.2%' },
    { bucket: '1–30 DPD',          count: 2,  amount: 2100000,  pct: '8.7%'  },
    { bucket: '31–90 DPD',         count: 1,  amount: 3500000,  pct: '14.5%' },
    { bucket: '91–365 DPD',        count: 1,  amount: 400000,   pct: '1.6%'  },
    { bucket: '1–2 Years',         count: 0,  amount: 0,       pct: '0%'    },
    { bucket: '> 2 Years',         count: 0,  amount: 0,       pct: '0%'    },
  ];`
);

code = code.replace(
  `Days Past Due analysis as per RBI asset classification methodology`,
  `Days past due ageing by outstanding amount.`
);

// CFO MIS Summary
code = code.replace(
  `['Portfolio at Risk (DPD > 0)', '24.8%'],
                ['Non-Performing Assets (DPD > 90)', '1.6%'],
                ['Provision Coverage Ratio', 'N/A — pending board approval'],
                ['Loan Loss Reserve', '₹0 (not yet provisioned)'],
                ['Recovery Rate',     '0% — recovery action initiated'],
                ['Write-Off Loans',   '0'],`,
  `['Portfolio at Risk (DPD > 0)', '24.8%'],
                ['Non-Performing Assets (DPD > 90)', '1.6%'],
                ['Provision Coverage Ratio', 'Not configured'],
                ['Loan Loss Reserve', '₹0 — not provisioned'],
                ['Recovery Rate',     '0% — recovery initiated'],
                ['Write-off loans',   '0'],`
);

// Compliance MIS Section 186
code = code.replace(
  `<div>
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
              </div>`,
  `<div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-slate-700">Portfolio Outstanding vs Estimated 186 Cap</span>
                  <span className="font-semibold text-amber-700">{dashboardStats.sectionUtilisation}% utilised</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-4">
                  <div className="bg-amber-400 h-4 rounded-full" style={{ width: \`\${dashboardStats.sectionUtilisation}%\` }} />
                </div>
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>₹0</span>
                  <span className="text-amber-600 font-medium">₹2.42Cr outstanding</span>
                  <span>Est. cap {fmt(Math.round(24200000 / (dashboardStats.sectionUtilisation / 100)))}</span>
                </div>
              </div>`
);

// Member Exposure calculations
code = code.replace(
  `{[
                    { name: 'Ganesh Thorat',    type: 'Individual', shares: 5, limit: 150000, exposure: 350000, risk: 'high' },
                    { name: 'Sunita Kamble',    type: 'Individual', shares: 3, limit: 90000,  exposure: 200000, risk: 'high' },
                    { name: 'Kisan FPC Ltd',    type: 'FPC',        shares: 50, limit: 1500000, exposure: 890000, risk: 'medium' },
                    { name: 'Vijay Patil',      type: 'Individual', shares: 8, limit: 240000, exposure: 350000, risk: 'high' },
                    { name: 'Radha Kisan Org',  type: 'FPC',        shares: 20, limit: 600000, exposure: 0,      risk: 'low' },
                  ].map(row => {
                    const headroom = row.limit - row.exposure;
                    return (
                      <tr key={row.name} className={\`hover:bg-slate-50 \${row.risk === 'high' ? 'bg-red-50/20' : ''}\`}>
                        <td className="px-6 py-3 font-medium text-slate-800">{row.name}</td>
                        <td className="px-4 py-3 text-slate-600">{row.type}</td>
                        <td className="px-4 py-3 text-right text-slate-700">{row.shares}</td>
                        <td className="px-4 py-3 text-right text-slate-700">₹{(row.limit/1000).toFixed(0)}K</td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{(row.exposure/1000).toFixed(0)}K</td>
                        <td className={\`px-4 py-3 text-right font-semibold \${headroom < 0 ? 'text-red-600' : 'text-green-600'}\`}>
                          {headroom < 0 ? \`-₹\${(Math.abs(headroom)/1000).toFixed(0)}K\` : \`₹\${(headroom/1000).toFixed(0)}K\`}
                        </td>
                        <td className="px-4 py-3">
                          <span className={\`text-xs px-2 py-1 rounded-full font-medium \${
                            row.risk === 'high' ? 'bg-red-100 text-red-700' :
                            row.risk === 'medium' ? 'bg-amber-100 text-amber-700' :
                            'bg-green-100 text-green-700'
                          }\`}>{row.risk.charAt(0).toUpperCase() + row.risk.slice(1)}</span>
                        </td>
                      </tr>
                    );
                  })}`,
  `{[
                    { name: 'Ganesh Thorat',    type: 'Individual', shares: 5, limit: 150000, exposure: 350000 },
                    { name: 'Sunita Kamble',    type: 'Individual', shares: 3, limit: 90000,  exposure: 200000 },
                    { name: 'Kisan FPC Ltd',    type: 'FPC',        shares: 50, limit: 1500000, exposure: 890000 },
                    { name: 'Vijay Patil',      type: 'Individual', shares: 8, limit: 240000, exposure: 350000 },
                    { name: 'Radha Kisan Org',  type: 'FPC',        shares: 20, limit: 600000, exposure: 0 },
                  ].map(row => {
                    const headroom = row.limit - row.exposure;
                    const risk = headroom < 0 ? 'high' : headroom < 100000 ? 'medium' : 'low';
                    return (
                      <tr key={row.name} className={\`hover:bg-slate-50 \${risk === 'high' ? 'bg-red-50/20' : ''}\`}>
                        <td className="px-6 py-3 font-medium text-slate-800">{row.name}</td>
                        <td className="px-4 py-3 text-slate-600">{row.type}</td>
                        <td className="px-4 py-3 text-right text-slate-700">{row.shares}</td>
                        <td className="px-4 py-3 text-right text-slate-700">{fmt(row.limit)}</td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">{fmt(row.exposure)}</td>
                        <td className={\`px-4 py-3 text-right font-semibold \${headroom < 0 ? 'text-red-600' : 'text-green-600'}\`}>
                          {fmt(headroom)}
                        </td>
                        <td className="px-4 py-3">
                          <span className={\`text-xs px-2 py-1 rounded-full font-medium \${
                            risk === 'high' ? 'bg-red-100 text-red-700' :
                            risk === 'medium' ? 'bg-amber-100 text-amber-700' :
                            'bg-green-100 text-green-700'
                          }\`}>{risk.charAt(0).toUpperCase() + risk.slice(1)}</span>
                        </td>
                      </tr>
                    );
                  })}`
);


// Export permissions
code = code.replace(
  `const [reportPeriod, setReportPeriod] = useState('Q1 FY 2025–26');`,
  `const [reportPeriod, setReportPeriod] = useState('Q1 FY 2025–26');
  const canExport = can('export_reports');`
);

code = code.replace(
  `<button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Download size={15} />
            Export
          </button>`,
  `<button disabled={!canExport} className="disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Download size={15} />
            Export
          </button>`
);

code = code.replace(
  `<button className="flex items-center gap-2 text-sm text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">
                <Download size={14} />
                Export CSV
              </button>`,
  `<button disabled={!canExport} className="disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">
                <Download size={14} />
                Export CSV
              </button>`
);

code = code.replace(
  `<button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                <BarChart2 size={16} />
                Generate Report
              </button>`,
  `<button disabled={!canExport} className="disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                <BarChart2 size={16} />
                Generate Report
              </button>`
);

fs.writeFileSync(file, code);
console.log("update complete");
