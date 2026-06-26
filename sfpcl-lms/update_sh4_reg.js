const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 10: SH-4 Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileSymlink size={14} className="text-green-600" /> SH-4 Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Physical share transfer forms held for security</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">SH-4 ID</th>
                  <th className="table-header text-left">Application</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Shares</th>
                  <th className="table-header text-left">Execution Date</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { id: 'SH4-2024-042', app: 'LO00000042', borrower: 'Ganesh Thorat', shares: 100, executed: '2024-09-15', custodian: 'Company Secretary', status: 'held' },
                  { id: 'SH4-2023-021', app: 'LO00000019', borrower: 'Prakash Kale', shares: 50, executed: '2022-09-14', custodian: 'Company Secretary', status: 'returned' },
                ].map(s => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{s.id}</td>
                    <td className="table-cell font-mono text-slate-600">{s.app}</td>
                    <td className="table-cell font-medium text-slate-900">{s.borrower}</td>
                    <td className="table-cell text-right num">{s.shares}</td>
                    <td className="table-cell text-slate-600">{s.executed}</td>
                    <td className="table-cell text-slate-600">{s.custodian}</td>
                    <td className="table-cell"><StatusBadge label={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 10: SH-4 Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <FileSymlink size={14} className="text-green-600" /> SH-4 register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Physical share transfer forms held as security</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">SH-4 ID</th>
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Shares</th>
                  <th className="table-header text-left">Executed On</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Return / Custody Ref</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { id: 'SH4-2026-042', appId: 'app001', shares: 100, executed: '2026-06-15', custodian: 'Company Secretary', status: 'held_in_custody', ref: 'SEC-CAB-01' },
                  { id: 'SH4-2026-021', appId: 'app007', shares: 50, executed: '2026-06-20', custodian: 'Company Secretary', status: 'returned', ref: 'ACK-2026-089' },
                ].map(s => {
                  const matchedApp = loanApplications.find(a => a.id === s.appId);
                  const displayAppNo = matchedApp ? matchedApp.applicationNumber : s.appId;
                  const displayBorrower = matchedApp ? matchedApp.memberName : 'Unknown';
                  
                  let displayId = s.id.replace('SH4-', 'SH-4-');
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const dateText = dtFormat.format(new Date(s.executed));
                  
                  const statusMap: Record<string, string> = {
                    held_in_custody: 'Held in custody',
                    returned: 'Returned',
                    invoked: 'Invoked',
                    released: 'Released',
                    not_required: 'Not required'
                  };
                  let statusText = statusMap[s.status] || s.status;
                  
                  const statusColor = statusText === 'Held in custody' ? 'bg-green-100 text-green-700' :
                                      statusText === 'Returned' || statusText === 'Released' ? 'bg-slate-100 text-slate-700' :
                                      statusText === 'Invoked' ? 'bg-red-100 text-red-700' :
                                      'bg-slate-100 text-slate-700';

                  return (
                    <tr key={s.id} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{displayId}</td>
                      <td className="table-cell font-mono text-slate-600">{displayAppNo}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell text-right num font-semibold">{s.shares}</td>
                      <td className="table-cell text-slate-600">{dateText}</td>
                      <td className="table-cell text-slate-600">{s.custodian}</td>
                      <td className="table-cell text-xs text-slate-500 font-mono">{s.ref}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                          {statusText}
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
