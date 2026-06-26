const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 9: Blank-dated Cheque Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileCheck2 size={14} className="text-green-600" /> Blank-Dated Cheque Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Cheque custody, return and invocation records</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Application</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Bank</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">Return / Invocation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { app: 'LO00000042', borrower: 'Ganesh Thorat', bank: 'HDFC Bank', custodian: 'Company Secretary', status: 'held', info: '—' },
                  { app: 'LO00000035', borrower: 'Kisan FPC Ltd', bank: 'State Bank of India', custodian: 'Company Secretary', status: 'held', info: 'Pending Closure' },
                  { app: 'LO00000047', borrower: 'Vijay Deshmukh', bank: 'ICICI Bank', custodian: 'Company Secretary', status: 'invocation_pending', info: 'Recovery Approved' },
                ].map(c => (
                  <tr key={c.app} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{c.app}</td>
                    <td className="table-cell font-medium text-slate-900">{c.borrower}</td>
                    <td className="table-cell text-slate-700">{c.bank}</td>
                    <td className="table-cell text-slate-600">{c.custodian}</td>
                    <td className="table-cell"><StatusBadge label={c.status} size="sm" /></td>
                    <td className="table-cell text-xs text-slate-500">{c.info}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 9: Blank-dated Cheque Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <FileCheck2 size={14} className="text-green-600" /> Blank-dated cheque register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Cheque custody, return and invocation records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Bank</th>
                  <th className="table-header text-left">Custody Date</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">Return / Invocation Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { appId: 'app001', bank: 'HDFC Bank', custodyDate: '2026-06-12', custodian: 'Company Secretary', status: 'held_in_custody', info: '—' },
                  { appId: 'app005', bank: 'State Bank of India', custodyDate: '2026-04-18', custodian: 'Company Secretary', status: 'return_pending', info: 'return_pending' },
                  { appId: 'app008', bank: 'ICICI Bank', custodyDate: '2026-06-20', custodian: 'Company Secretary', status: 'invocation_pending', info: 'recovery_approved' },
                ].map(c => {
                  const matchedApp = loanApplications.find(a => a.id === c.appId);
                  const displayAppNo = matchedApp ? matchedApp.applicationNumber : c.appId;
                  const displayBorrower = matchedApp ? matchedApp.memberName : 'Unknown';
                  
                  const statusMap: Record<string, string> = {
                    held_in_custody: 'Held in custody',
                    return_pending: 'Return pending',
                    returned: 'Returned',
                    recovery_approved: 'Recovery approved',
                    invocation_pending: 'Invocation pending',
                    invoked: 'Invoked',
                    closed: 'Closed',
                    not_required: 'Not required'
                  };
                  let statusText = statusMap[c.status] || c.status;
                  
                  let infoText = c.info;
                  if (c.info === 'return_pending') infoText = 'Return pending at closure';
                  if (c.info === 'recovery_approved') infoText = 'Recovery approved; invocation pending';
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const custodyDateText = c.custodyDate ? dtFormat.format(new Date(c.custodyDate)) : '—';
                  
                  const statusColor = statusText === 'Held in custody' || statusText === 'Returned' || statusText === 'Closed' ? 'bg-green-100 text-green-700' :
                                      statusText === 'Return pending' || statusText === 'Invocation pending' ? 'bg-amber-100 text-amber-700' :
                                      statusText === 'Recovery approved' || statusText === 'Invoked' ? 'bg-red-100 text-red-700' :
                                      'bg-slate-100 text-slate-700';
                                      
                  return (
                    <tr key={c.appId} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{displayAppNo}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell text-slate-700">{c.bank}</td>
                      <td className="table-cell text-slate-600">{custodyDateText}</td>
                      <td className="table-cell text-slate-600">{c.custodian}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                          {statusText}
                        </span>
                      </td>
                      <td className="table-cell text-xs text-slate-500 font-medium">{infoText}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>`;

code = code.replace(oldTab, newTab);
fs.writeFileSync(file, code);
console.log("update complete");
