const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 18: NOC / Closure Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <ShieldCheck size={14} className="text-emerald-600" /> NOC / Closure Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Closure readiness, NOC issue and security return tracking</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">NOC ID</th>
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Balance</th>
                  <th className="table-header text-left">NOC Status</th>
                  <th className="table-header text-left">Security Return</th>
                  <th className="table-header text-left">Archive</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { noc: 'NOC-2025-042', loan: 'LO00000031', borrower: 'Asha Bhosale', bal: 0, nocStatus: 'ready', secStatus: 'pending', arcStatus: 'pending' },
                  { noc: 'NOC-2024-089', loan: 'LO00000025', borrower: 'Radha Kisan Org', bal: 0, nocStatus: 'issued', secStatus: 'complete', arcStatus: 'complete' },
                ].map(n => (
                  <tr key={n.noc} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{n.noc}</td>
                    <td className="table-cell font-mono text-slate-600">{n.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{n.borrower}</td>
                    <td className="table-cell num text-right text-emerald-700 font-semibold">₹{n.bal.toLocaleString('en-IN')}</td>
                    <td className="table-cell"><StatusBadge label={n.nocStatus} size="sm" /></td>
                    <td className="table-cell text-slate-600">{n.secStatus}</td>
                    <td className="table-cell text-slate-600">{n.arcStatus}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 18: NOC / Closure Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <ShieldCheck size={14} className="text-emerald-600" /> NOC / closure register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">NOC, security return and archive status for fully repaid loans</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">NOC ID</th>
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Outstanding Balance</th>
                  <th className="table-header text-left">Closure Status</th>
                  <th className="table-header text-left">NOC Status</th>
                  <th className="table-header text-left">NOC Issued On</th>
                  <th className="table-header text-left">Security Return</th>
                  <th className="table-header text-left">Archive</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { lnId: 'ln003', bal: 0, nocStatus: 'ready', secStatus: 'pending', arcStatus: 'pending', nocIssuedOn: null },
                  { lnId: 'ln001', bal: 0, nocStatus: 'issued', secStatus: 'complete', arcStatus: 'complete', nocIssuedOn: '2026-05-10' },
                ].map(n => {
                  const matchedLoan = loanAccounts.find(l => l.id === n.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : n.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  let closureStatus = 'Closure in progress';
                  let displayNocId = 'Pending issue';
                  
                  if (n.nocStatus === 'issued' && n.secStatus === 'complete' && n.arcStatus === 'complete' && n.bal === 0) {
                     closureStatus = 'Closure complete';
                     displayNocId = \`NOC-\${n.nocIssuedOn ? n.nocIssuedOn.split('-')[0] : '2026'}-\${displayLoan.slice(-3)}\`;
                  } else if (n.nocStatus === 'issued') {
                     displayNocId = \`NOC-\${n.nocIssuedOn ? n.nocIssuedOn.split('-')[0] : '2026'}-\${displayLoan.slice(-3)}\`;
                  }

                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const displayNocDate = n.nocIssuedOn ? dtFormat.format(new Date(n.nocIssuedOn)) : '—';
                  
                  const nocMap: Record<string, string> = {
                    ready: 'Ready for NOC issue',
                    issued: 'NOC issued',
                    pending: 'Pending'
                  };
                  const displayNocStatus = nocMap[n.nocStatus] || n.nocStatus;
                  
                  const secMap: Record<string, string> = {
                    pending: 'Security return pending',
                    complete: 'Security returned',
                    unpledged: 'Unpledged'
                  };
                  const displaySec = secMap[n.secStatus] || n.secStatus;
                  
                  const arcMap: Record<string, string> = {
                    pending: 'Archive pending',
                    complete: 'Archived'
                  };
                  const displayArc = arcMap[n.arcStatus] || n.arcStatus;

                  const closureColor = closureStatus === 'Closure complete' ? 'text-green-700 bg-green-100' : 'text-amber-700 bg-amber-100';

                  return (
                    <tr key={n.lnId} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{displayNocId}</td>
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell num text-right text-emerald-700 font-semibold">{fmt(n.bal)}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${closureColor}\`}>
                          {closureStatus}
                        </span>
                      </td>
                      <td className="table-cell text-slate-600">{displayNocStatus}</td>
                      <td className="table-cell text-slate-600">{displayNocDate}</td>
                      <td className="table-cell text-slate-600">{displaySec}</td>
                      <td className="table-cell text-slate-600">{displayArc}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>`;

code = code.replace(oldTab, newTab);
fs.writeFileSync(file, code);

console.log("update complete");
