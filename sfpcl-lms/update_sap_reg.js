const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 12: SAP Customer Code Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Database size={14} className="text-blue-600" /> SAP Customer Code Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">SAP customer profile request and confirmation records</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Request ID</th>
                  <th className="table-header text-left">Application</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Requested On</th>
                  <th className="table-header text-left">SAP Code</th>
                  <th className="table-header text-left">Confirmed By</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { reqId: 'SAP-REQ-001', app: 'LO00000042', borrower: 'Ganesh Thorat', date: '2024-09-20', sapCode: '10045621', confirmedBy: 'Senior Manager Finance', status: 'created' },
                  { reqId: 'SAP-REQ-002', app: 'LO00000047', borrower: 'Vijay Deshmukh', date: '2026-06-18', sapCode: null, confirmedBy: null, status: 'pending' },
                ].map(r => (
                  <tr key={r.reqId} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{r.reqId}</td>
                    <td className="table-cell font-mono text-slate-600">{r.app}</td>
                    <td className="table-cell font-medium text-slate-900">{r.borrower}</td>
                    <td className="table-cell text-slate-600">{r.date}</td>
                    <td className="table-cell font-mono font-medium text-slate-800">{r.sapCode || '—'}</td>
                    <td className="table-cell text-slate-600">{r.confirmedBy || '—'}</td>
                    <td className="table-cell"><StatusBadge label={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 12: SAP Customer Code Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Database size={14} className="text-blue-600" /> SAP customer code register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">SAP customer profile requests and confirmations</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Request ID</th>
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Requested On</th>
                  <th className="table-header text-left">SAP Code</th>
                  <th className="table-header text-left">Confirmed By</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { reqId: 'SAP-REQ-001', appId: 'app001', date: '2024-09-20', sapCode: '10045621', confirmedBy: 'Senior Manager – Finance', status: 'created', requestedBy: 'Credit Manager' },
                  { reqId: 'SAP-REQ-002', appId: 'app008', date: '2026-06-18', sapCode: null, confirmedBy: null, status: 'pending', requestedBy: 'Credit Manager' },
                ].map(r => {
                  const matchedApp = loanApplications.find(a => a.id === r.appId);
                  const displayAppNo = matchedApp ? matchedApp.applicationNumber : r.appId;
                  const displayBorrower = matchedApp ? matchedApp.memberName : 'Unknown';

                  const statusMap: Record<string, string> = {
                    pending: 'Pending',
                    created: 'Created',
                    failed: 'Failed',
                    rework_required: 'Rework required',
                    not_required: 'Not required'
                  };
                  let statusText = statusMap[r.status] || r.status;
                  
                  let displayCode = r.sapCode;
                  let displayConfirmer = r.confirmedBy;
                  
                  if (statusText === 'Pending') {
                     displayCode = displayCode || 'Pending';
                     displayConfirmer = displayConfirmer || 'Pending';
                  } else {
                     displayCode = displayCode || '—';
                     displayConfirmer = displayConfirmer || '—';
                  }
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const dateText = dtFormat.format(new Date(r.date));
                  
                  const statusColor = statusText === 'Created' ? 'bg-green-100 text-green-700' :
                                      statusText === 'Pending' ? 'bg-amber-100 text-amber-700' :
                                      statusText === 'Failed' || statusText === 'Rework required' ? 'bg-red-100 text-red-700' :
                                      'bg-slate-100 text-slate-700';

                  return (
                    <tr key={r.reqId} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{r.reqId}</td>
                      <td className="table-cell font-mono text-slate-600">{displayAppNo}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell text-slate-600">{dateText}</td>
                      <td className="table-cell font-mono font-medium text-slate-800">{displayCode}</td>
                      <td className="table-cell text-slate-600">{displayConfirmer}</td>
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
