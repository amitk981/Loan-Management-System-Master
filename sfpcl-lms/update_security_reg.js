const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// Title & Subtitle for Tab
code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Scale size={14} className="text-green-600" /> Security Register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All collateral and security instruments — {securities.length} records</p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Scale size={14} className="text-green-600" /> Security register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All security instruments — {securities.length} records</p>`
);

// Map Loop
const oldLoop = `{securities.map(sec => (
                  <tr key={sec.id} className="hover:bg-slate-50">
                    <td className="table-cell font-semibold capitalize">{sec.securityType.replace('_', ' ')}</td>
                    <td className="table-cell num text-green-700">{sec.applicationId}</td>
                    <td className="table-cell"><StatusBadge label={sec.status} size="sm" /></td>
                    <td className="table-cell">{sec.executionDate || '—'}</td>
                    <td className="table-cell">{sec.custodian || '—'}</td>
                    <td className="table-cell">
                      <span className={\`text-xs capitalize \${sec.stampDutyStatus === 'complete' ? 'text-green-600' : sec.stampDutyStatus === 'pending' ? 'text-amber-600' : 'text-slate-400'}\`}>
                        {sec.stampDutyStatus || '—'}
                      </span>
                    </td>
                    <td className="table-cell">
                      <span className={\`text-xs capitalize \${sec.notarisationStatus === 'complete' ? 'text-green-600' : sec.notarisationStatus === 'pending' ? 'text-amber-600' : 'text-slate-400'}\`}>
                        {sec.notarisationStatus || '—'}
                      </span>
                    </td>
                    <td className="table-cell num text-xs text-slate-500">{sec.psnNumber || '—'}</td>
                  </tr>
                ))}`;

const newLoop = `{securities.map(sec => {
                  const typeMap: Record<string, string> = { sh4: 'SH-4', poa: 'PoA', cdsl_pledge: 'CDSL pledge', blank_cheque: 'Blank cheque', loan_agreement: 'Loan agreement' };
                  let displayType = typeMap[sec.securityType] || sec.securityType.replace('_', ' ');

                  const appObj = loanApplications.find(a => a.id === sec.applicationId);
                  let displayApp = appObj ? appObj.applicationNumber : sec.applicationId;

                  let stampDisplay = sec.stampDutyStatus === 'complete' ? 'Complete' : sec.stampDutyStatus === 'pending' ? 'Pending' : '—';
                  let notarisedDisplay = sec.notarisationStatus === 'complete' ? 'Complete' : sec.notarisationStatus === 'pending' ? 'Pending' : '—';
                  
                  let psnDisplay = sec.psnNumber || '—';

                  if (sec.securityType === 'blank_cheque') {
                    stampDisplay = 'Not required';
                    notarisedDisplay = 'Not required';
                    psnDisplay = 'Not required';
                  } else if (sec.securityType === 'cdsl_pledge') {
                    stampDisplay = 'Not required';
                    notarisedDisplay = 'Not required';
                    psnDisplay = sec.status === 'pledged' ? (sec.psnNumber || 'CDSL-PENDING') : sec.status === 'pending' ? 'Pending' : 'Not required';
                  } else if (sec.securityType === 'sh4') {
                    psnDisplay = 'Not required';
                  }

                  let displayStatus = sec.status;
                  const statusMap: Record<string, string> = {
                    held: 'Held in custody',
                    executed: 'Executed',
                    pledged: 'Pledged',
                    pending: 'Pending',
                    invoked: 'Invoked',
                    returned: 'Returned',
                    not_required: 'Not required'
                  };
                  
                  if (sec.securityType === 'poa' && sec.status === 'executed' && (sec.stampDutyStatus === 'pending' || sec.notarisationStatus === 'pending')) {
                    displayStatus = 'Execution pending';
                  } else {
                    displayStatus = statusMap[sec.status] || sec.status;
                  }

                  let formattedDate = '—';
                  if (sec.executionDate) {
                    formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(sec.executionDate));
                  }
                  
                  const statusColor = displayStatus === 'Held in custody' || displayStatus === 'Executed' || displayStatus === 'Pledged' ? 'bg-green-100 text-green-700' : 
                                      displayStatus === 'Execution pending' || displayStatus === 'Pending' ? 'bg-amber-100 text-amber-700' :
                                      displayStatus === 'Invoked' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700';

                  return (
                    <tr key={sec.id} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold">{displayType}</td>
                      <td className="table-cell num font-medium text-slate-800">{displayApp}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                          {displayStatus}
                        </span>
                      </td>
                      <td className="table-cell text-slate-600">{formattedDate}</td>
                      <td className="table-cell text-slate-600">{sec.custodian || '—'}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-medium \${stampDisplay === 'Complete' ? 'text-green-600' : stampDisplay === 'Pending' ? 'text-amber-600' : 'text-slate-500'}\`}>
                          {stampDisplay}
                        </span>
                      </td>
                      <td className="table-cell">
                        <span className={\`text-xs font-medium \${notarisedDisplay === 'Complete' ? 'text-green-600' : notarisedDisplay === 'Pending' ? 'text-amber-600' : 'text-slate-500'}\`}>
                          {notarisedDisplay}
                        </span>
                      </td>
                      <td className="table-cell num text-xs text-slate-500">{psnDisplay}</td>
                    </tr>
                  );
                })}`;

code = code.replace(oldLoop, newLoop);

fs.writeFileSync(file, code);
console.log("update complete");
