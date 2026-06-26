const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 22: Archive Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Archive size={14} className="text-slate-600" /> Archive Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Closed loan file archive and retention records</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Archive ID</th>
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Closed On</th>
                  <th className="table-header text-left">Location</th>
                  <th className="table-header text-left">Retention Until</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { arc: 'ARC-2025-012', loan: 'LO00000025', borrower: 'Radha Kisan Org', closedOn: '2025-03-28', loc: 'Rack B, Shelf 4', retention: '2033-03-28', status: 'archived' },
                  { arc: 'ARC-2023-104', loan: 'LO00000021', borrower: 'Ganesh Thorat', closedOn: '2023-03-20', loc: 'Rack A, Shelf 2', retention: '2031-03-20', status: 'archived' },
                ].map(a => (
                  <tr key={a.arc} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{a.arc}</td>
                    <td className="table-cell font-mono text-slate-600">{a.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{a.borrower}</td>
                    <td className="table-cell text-slate-600">{a.closedOn}</td>
                    <td className="table-cell text-slate-600">{a.loc}</td>
                    <td className="table-cell text-slate-600">{a.retention}</td>
                    <td className="table-cell"><StatusBadge label={a.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 22: Archive Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Archive size={14} className="text-slate-600" /> Archive register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Closed loan files and retention records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Archive ID</th>
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Closed On</th>
                  <th className="table-header text-left">Archived On</th>
                  <th className="table-header text-left">Physical Location</th>
                  <th className="table-header text-left">Backup Status</th>
                  <th className="table-header text-left">Retention Until</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { arc: 'ARC-2025-012', lnId: 'ln004', closedOn: '2025-03-28', archivedOn: '2025-04-05', loc: 'Rack B, Shelf 4', backup: 'complete', status: 'archived' },
                  { arc: 'ARC-2023-104', lnId: 'ln005', closedOn: '2023-03-20', archivedOn: '2023-03-30', loc: 'Rack A, Shelf 2', backup: 'complete', status: 'archived' },
                ].map(a => {
                  const matchedLoan = loanAccounts.find(l => l.id === a.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : a.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  const closedDate = new Date(a.closedOn);
                  const retentionDate = new Date(closedDate);
                  retentionDate.setFullYear(retentionDate.getFullYear() + 8);

                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const closedText = dtFormat.format(closedDate);
                  const archivedText = a.archivedOn ? dtFormat.format(new Date(a.archivedOn)) : '—';
                  const retentionText = dtFormat.format(retentionDate);

                  let derivedStatus = a.status;
                  // Gate logic for archived
                  if (derivedStatus === 'archived' && (!a.loc || a.backup !== 'complete')) {
                    derivedStatus = 'pending';
                  }

                  const statusMap: Record<string, string> = {
                    archived: 'Archived',
                    pending: 'Pending'
                  };
                  const displayStatus = statusMap[derivedStatus] || derivedStatus;
                  
                  const backupMap: Record<string, string> = {
                    complete: 'Complete',
                    pending: 'Pending'
                  };
                  const displayBackup = backupMap[a.backup] || a.backup;

                  const statusColor = displayStatus === 'Archived' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700';

                  return (
                    <tr key={a.arc} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{a.arc}</td>
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell text-slate-600">{closedText}</td>
                      <td className="table-cell text-slate-600">{archivedText}</td>
                      <td className="table-cell text-slate-600">{a.loc}</td>
                      <td className="table-cell text-slate-600">{displayBackup}</td>
                      <td className="table-cell font-medium text-slate-700">{retentionText}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                          {displayStatus}
                        </span>
                      </td>
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
