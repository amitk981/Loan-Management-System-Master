const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 8: Recovery Log */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <ShieldAlert size={14} className="text-red-600" /> Recovery Log
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All default management and recovery action records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Loan No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Outstanding</th>
                  <th className="table-header text-center">DPD</th>
                  <th className="table-header text-left">Stage</th>
                  <th className="table-header text-left">Action Taken</th>
                  <th className="table-header text-left">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { loan: 'LO00000042', borrower: 'Ganesh Thorat', out: 350000, dpd: 45, stage: 'Grace period', action: 'Reminder calls and SMS sent.', date: '2025-06-10' },
                  { loan: 'LO00000035', borrower: 'Kisan FPC Ltd', out: 180000, dpd: 95, stage: 'Non-payment note submitted', action: 'Note prepared and submitted for CFO review.', date: '2025-06-15' },
                  { loan: 'LO00000047', borrower: 'Vijay Deshmukh', out: 890000, dpd: 187, stage: 'Recovery approved', action: 'CFO approved security invocation.', date: '2025-04-28' },
                ].map(r => (
                  <tr key={r.loan} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{r.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{r.borrower}</td>
                    <td className="table-cell num text-right text-red-600 font-semibold">₹{r.out.toLocaleString('en-IN')}</td>
                    <td className="table-cell num text-center font-bold text-slate-700">{r.dpd}</td>
                    <td className="table-cell"><StatusBadge label={r.stage} size="sm" /></td>
                    <td className="table-cell text-xs text-slate-500 max-w-xs truncate">{r.action}</td>
                    <td className="table-cell text-slate-500">{r.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 8: Recovery Log */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <ShieldAlert size={14} className="text-red-600" /> Recovery log
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Default and recovery records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Outstanding Amount</th>
                  <th className="table-header text-center">DPD</th>
                  <th className="table-header text-left">Recovery Stage</th>
                  <th className="table-header text-left">Last Action</th>
                  <th className="table-header text-left">Action Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { lnId: 'ln002', out: 350000, dpd: 45, stage: 'grace_period', action: 'Reminder calls and SMS sent — Credit Manager', date: '2025-06-10' },
                  { lnId: 'ln001', out: 180000, dpd: 95, stage: 'recovery_review', action: 'Non-payment note submitted to Sanction Committee', date: '2025-06-15' },
                  { lnId: 'ln003', out: 890000, dpd: 187, stage: 'recovery_approved', action: 'Recovery decision approved — Sanction Committee', date: '2025-04-28' },
                ].map(r => {
                  
                  const matchedLoan = loanAccounts.find(l => l.id === r.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : r.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const displayDate = dtFormat.format(new Date(r.date));
                  
                  const stageMap: Record<string, string> = {
                    grace_period: 'Grace period',
                    default_review: 'Default review',
                    extension_review: 'Extension review',
                    recovery_review: 'Recovery review',
                    recovery_approved: 'Recovery approved',
                    recovery_in_progress: 'Recovery in progress',
                    recovered: 'Recovered',
                    closed: 'Closed'
                  };
                  
                  const displayStage = stageMap[r.stage] || r.stage;
                  
                  const badgeColor = displayStage === 'Recovery approved' || displayStage === 'Recovery in progress' ? 'bg-red-100 text-red-700' :
                                     displayStage === 'Recovery review' ? 'bg-amber-100 text-amber-700' :
                                     displayStage === 'Grace period' ? 'bg-amber-50 text-amber-600' :
                                     'bg-slate-100 text-slate-700';

                  return (
                  <tr key={r.lnId} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                    <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                    <td className="table-cell num text-right text-red-600 font-semibold">{fmt(r.out)}</td>
                    <td className="table-cell num text-center font-bold text-slate-700">{r.dpd}</td>
                    <td className="table-cell">
                      <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${badgeColor}\`}>
                        {displayStage}
                      </span>
                    </td>
                    <td className="table-cell text-xs text-slate-500 max-w-xs truncate" title={r.action}>{r.action}</td>
                    <td className="table-cell text-slate-500">{displayDate}</td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        </div>`;

code = code.replace(oldTab, newTab);
fs.writeFileSync(file, code);

console.log("update complete");
