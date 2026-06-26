const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 17: DPD / Monitoring Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Filter size={14} className="text-slate-600" /> DPD / Monitoring Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Delinquency bucket and reminder tracking</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-center">DPD</th>
                  <th className="table-header text-left">Bucket</th>
                  <th className="table-header text-left">Last Reminder</th>
                  <th className="table-header text-left">Next Action</th>
                  <th className="table-header text-left">Owner</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { loan: 'LO00000042', borrower: 'Ganesh Thorat', dpd: 45, bucket: '31-60 DPD', lastReminder: '2025-06-10', action: 'Prepare Non-Payment Note', owner: 'Credit Manager' },
                  { loan: 'LO00000038', borrower: 'Ajit Patil', dpd: 95, bucket: '91-120 DPD', lastReminder: '2025-06-15', action: 'Recovery Initiation', owner: 'CFO' },
                ].map(d => (
                  <tr key={d.loan} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{d.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{d.borrower}</td>
                    <td className="table-cell num text-center font-bold text-red-600">{d.dpd}</td>
                    <td className="table-cell text-slate-600">{d.bucket}</td>
                    <td className="table-cell text-slate-600">{d.lastReminder}</td>
                    <td className="table-cell text-xs font-medium text-slate-700">{d.action}</td>
                    <td className="table-cell text-slate-600">{d.owner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 17: DPD / Monitoring Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Filter size={14} className="text-slate-600" /> DPD / monitoring register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">DPD buckets, reminders and next actions</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-center">DPD</th>
                  <th className="table-header text-left">DPD Bucket</th>
                  <th className="table-header text-left">Last Reminder</th>
                  <th className="table-header text-center">Reminders</th>
                  <th className="table-header text-left">Next Action Due</th>
                  <th className="table-header text-left">Next Action</th>
                  <th className="table-header text-left">Owner</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { lnId: 'ln002', dpd: 45, lastReminder: '2026-06-10', reminderCount: 2, actionDue: '2026-06-25', action: 'Grace review', owner: 'Credit Manager' },
                  { lnId: 'ln003', dpd: 95, lastReminder: '2026-06-15', reminderCount: 4, actionDue: '2026-06-20', action: 'Non-payment note submitted', owner: 'Sanction Committee' },
                ].map(d => {
                  const matchedLoan = loanAccounts.find(l => l.id === d.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : d.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  let bucket = '0 DPD';
                  if (d.dpd >= 1 && d.dpd <= 30) bucket = '1–30 DPD';
                  else if (d.dpd >= 31 && d.dpd <= 90) bucket = '31–90 DPD';
                  else if (d.dpd >= 91 && d.dpd <= 365) bucket = '91–365 DPD';
                  else if (d.dpd >= 366 && d.dpd <= 730) bucket = '1–2 years';
                  else if (d.dpd > 730) bucket = '> 2 years';

                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const dateText = d.lastReminder ? dtFormat.format(new Date(d.lastReminder)) : '—';
                  const actionDueText = d.actionDue ? dtFormat.format(new Date(d.actionDue)) : '—';

                  const dpdColor = d.dpd > 90 ? 'text-red-700' : d.dpd > 30 ? 'text-amber-600' : 'text-slate-700';

                  return (
                    <tr key={d.lnId} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className={\`table-cell num text-center font-bold \${dpdColor}\`}>{d.dpd}</td>
                      <td className="table-cell text-slate-600">{bucket}</td>
                      <td className="table-cell text-slate-600">{dateText}</td>
                      <td className="table-cell num text-center text-slate-600">{d.reminderCount}</td>
                      <td className="table-cell text-slate-600">{actionDueText}</td>
                      <td className="table-cell text-xs font-medium text-slate-700">{d.action}</td>
                      <td className="table-cell text-slate-600">{d.owner}</td>
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
