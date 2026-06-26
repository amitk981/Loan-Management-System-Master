const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 23: SOP Change Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <RotateCcw size={14} className="text-teal-600" /> SOP Change Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Policy/SOP revisions and Board approval tracking</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Change ID</th>
                  <th className="table-header text-left">Area</th>
                  <th className="table-header text-left">Requested By</th>
                  <th className="table-header text-left">Requested On</th>
                  <th className="table-header text-left">Approval</th>
                  <th className="table-header text-left">Effective Date</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { chg: 'SOP-CHG-001', area: 'Loan Threshold Matrix', reqBy: 'CFO', reqOn: '2026-05-12', approval: 'Board Pending', effective: '2026-06-01', status: 'under_review' },
                  { chg: 'SOP-CHG-002', area: 'KYC Refresh Cycle', reqBy: 'Company Secretary', reqOn: '2026-04-08', approval: 'Approved', effective: '2026-06-01', status: 'active' },
                ].map(c => (
                  <tr key={c.chg} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{c.chg}</td>
                    <td className="table-cell font-medium text-slate-900">{c.area}</td>
                    <td className="table-cell text-slate-600">{c.reqBy}</td>
                    <td className="table-cell text-slate-600">{c.reqOn}</td>
                    <td className="table-cell text-slate-600">{c.approval}</td>
                    <td className="table-cell text-slate-600">{c.effective}</td>
                    <td className="table-cell"><StatusBadge label={c.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 23: SOP Change Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <RotateCcw size={14} className="text-teal-600" /> SOP change register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Policy, workflow and approval-matrix change records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Change ID</th>
                  <th className="table-header text-left">Area</th>
                  <th className="table-header text-left">Version</th>
                  <th className="table-header text-left">Requested By</th>
                  <th className="table-header text-left">Requested On</th>
                  <th className="table-header text-left">Approval Status</th>
                  <th className="table-header text-left">Approved On</th>
                  <th className="table-header text-left">Effective Date</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { chg: 'SOP-CHG-001', area: 'Loan threshold matrix', vOld: 'v1.2', vNew: 'v1.3', reqBy: 'CFO', reqOn: '2026-05-12', approval: 'pending', approvedOn: null, effective: '2026-06-01', status: 'pending' },
                  { chg: 'SOP-CHG-002', area: 'KYC refresh cycle', vOld: 'v2.0', vNew: 'v2.1', reqBy: 'Company Secretary', reqOn: '2026-04-08', approval: 'approved', approvedOn: '2026-05-15', effective: '2026-06-01', status: 'active' },
                ].map(c => {
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const reqOnText = dtFormat.format(new Date(c.reqOn));
                  const appOnText = c.approvedOn ? dtFormat.format(new Date(c.approvedOn)) : '—';
                  
                  let displayApproval = c.approval === 'pending' ? 'Board approval pending' : 'Approved';
                  let displayEffective = 'Pending approval';
                  
                  let derivedStatus = c.status;
                  
                  if (c.approval === 'approved' && c.approvedOn) {
                    displayEffective = dtFormat.format(new Date(c.effective));
                    const effDate = new Date(c.effective);
                    const now = new Date(); // Mocking as now = 2026-06-26 so Jun 1st is in the past
                    if (now < effDate) {
                       derivedStatus = 'scheduled';
                    } else {
                       derivedStatus = 'active';
                    }
                  } else {
                    derivedStatus = 'pending_approval';
                  }

                  const statusMap: Record<string, string> = {
                    draft: 'Draft',
                    pending_approval: 'Pending approval',
                    approved: 'Approved',
                    scheduled: 'Scheduled',
                    active: 'Active',
                    rejected: 'Rejected',
                    superseded: 'Superseded'
                  };
                  const displayStatus = statusMap[derivedStatus] || derivedStatus;
                  
                  const statusColor = displayStatus === 'Active' ? 'bg-green-100 text-green-700' :
                                      displayStatus === 'Scheduled' ? 'bg-blue-100 text-blue-700' :
                                      displayStatus === 'Pending approval' ? 'bg-amber-100 text-amber-700' :
                                      'bg-slate-100 text-slate-700';

                  return (
                    <tr key={c.chg} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{c.chg}</td>
                      <td className="table-cell font-medium text-slate-900">{c.area}</td>
                      <td className="table-cell text-xs font-mono text-slate-500">{c.vOld} → {c.vNew}</td>
                      <td className="table-cell text-slate-600">{c.reqBy}</td>
                      <td className="table-cell text-slate-600">{reqOnText}</td>
                      <td className="table-cell text-slate-600">{displayApproval}</td>
                      <td className="table-cell text-slate-600">{appOnText}</td>
                      <td className="table-cell font-medium text-slate-700">{displayEffective}</td>
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
