const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 11: CDSL Pledge Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Link size={14} className="text-green-600" /> CDSL Pledge Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Demat pledge creation, invocation and unpledge tracking</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">PSN</th>
                  <th className="table-header text-left">Application</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">BO ID</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Unpledge Date</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { psn: '19042400012', app: 'LO00000035', borrower: 'Kisan FPC Ltd', boId: 'xxxxxxxx12345678', custodian: 'Company Secretary', status: 'pledged', unpledgedDate: null },
                  { psn: '18051200045', app: 'LO00000028', borrower: 'Green Valley FPC', boId: 'xxxxxxxx87654321', custodian: 'Company Secretary', status: 'unpledged', unpledgedDate: '2025-05-14' },
                ].map(p => (
                  <tr key={p.psn} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{p.psn}</td>
                    <td className="table-cell font-mono text-slate-600">{p.app}</td>
                    <td className="table-cell font-medium text-slate-900">{p.borrower}</td>
                    <td className="table-cell font-mono text-slate-500 text-xs">{p.boId}</td>
                    <td className="table-cell text-slate-600">{p.custodian}</td>
                    <td className="table-cell text-slate-500">{p.unpledgedDate || '—'}</td>
                    <td className="table-cell"><StatusBadge label={p.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 11: CDSL Pledge Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Link size={14} className="text-green-600" /> CDSL pledge register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Demat pledge, invocation and unpledge records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">PSN</th>
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">BO ID</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Pledge / Release Ref</th>
                  <th className="table-header text-left">Unpledged On</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { psn: '19042400012', appId: 'app005', boId: 'xxxxxxxx12345678', custodian: 'Company Secretary', status: 'pledged', unpledgedDate: null, ref: 'PLG-2026-001' },
                  { psn: '18051200045', appId: 'app006', boId: 'xxxxxxxx87654321', custodian: 'Company Secretary', status: 'unpledged', unpledgedDate: '2025-05-14', ref: 'UNP-2025-088' },
                ].map(p => {
                  const matchedApp = loanApplications.find(a => a.id === p.appId);
                  const displayAppNo = matchedApp ? matchedApp.applicationNumber : p.appId;
                  const displayBorrower = matchedApp ? matchedApp.memberName : 'Unknown';
                  
                  const statusMap: Record<string, string> = {
                    pending: 'Pending',
                    pledged: 'Pledged',
                    invocation_pending: 'Invocation pending',
                    invoked: 'Invoked',
                    unpledge_pending: 'Unpledge pending',
                    unpledged: 'Unpledged',
                    rejected: 'Rejected',
                    not_required: 'Not required'
                  };
                  let statusText = statusMap[p.status] || p.status;
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  let displayUnpledge = 'Pending';
                  if (statusText === 'Unpledged' && p.unpledgedDate) {
                    displayUnpledge = dtFormat.format(new Date(p.unpledgedDate));
                  }
                  
                  const statusColor = statusText === 'Pledged' ? 'bg-green-100 text-green-700' :
                                      statusText === 'Unpledged' ? 'bg-slate-100 text-slate-700' :
                                      statusText === 'Invoked' ? 'bg-red-100 text-red-700' :
                                      'bg-amber-100 text-amber-700';

                  return (
                    <tr key={p.psn} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{p.psn}</td>
                      <td className="table-cell font-mono text-slate-600">{displayAppNo}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell font-mono text-slate-500 text-xs">{p.boId}</td>
                      <td className="table-cell text-slate-600">{p.custodian}</td>
                      <td className="table-cell font-mono text-slate-500 text-xs">{p.ref}</td>
                      <td className="table-cell text-slate-500 font-medium">{displayUnpledge}</td>
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
