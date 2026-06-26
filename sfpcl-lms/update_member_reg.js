const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// Title & Subtitle for Tab
code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <BookOpen size={14} className="text-green-600" /> Member Register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All SFPCL members — {members.length} records</p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <BookOpen size={14} className="text-green-600" /> Member register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All SFPCL members — {members.length} records</p>`
);

// Table Headers
code = code.replace(
  `<th className="table-header text-left">Type</th>
                  <th className="table-header text-right">Shares</th>
                  <th className="table-header text-left">KYC</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-right">Exposure</th>
                  <th className="table-header text-left">Registered</th>`,
  `<th className="table-header text-left">Member type</th>
                  <th className="table-header text-right">Shares</th>
                  <th className="table-header text-left">KYC</th>
                  <th className="table-header text-left">Member status</th>
                  <th className="table-header text-right">Exposure</th>
                  <th className="table-header text-left">Member since</th>`
);

// Map Loop
const oldLoop = `{members.map(m => (
                  <tr key={m.id} className="hover:bg-slate-50">
                    <td className="table-cell font-semibold text-slate-900">{m.name}</td>
                    <td className="table-cell num text-slate-600">{m.folioNumber}</td>
                    <td className="table-cell capitalize text-xs">{m.memberType === 'fpc' ? 'FPC' : m.memberType}</td>
                    <td className="table-cell text-right num">{m.sharesHeld.toLocaleString('en-IN')}</td>
                    <td className="table-cell"><StatusBadge label={m.kycStatus} size="sm" /></td>
                    <td className="table-cell"><StatusBadge label={m.activeStatus} size="sm" /></td>
                    <td className="table-cell text-right num">{m.currentExposure > 0 ? fmt(m.currentExposure) : '—'}</td>
                    <td className="table-cell">{new Date(m.registeredOn).toLocaleDateString('en-IN')}</td>
                  </tr>
                ))}`;

const newLoop = `{members.map(m => {
                  let displayName = m.name;
                  if (displayName === 'Green Valley F P C') displayName = 'Green Valley FPC';

                  const typeMap: Record<string, string> = { individual: 'Individual', fpc: 'FPC', producer_institution: 'Producer Institution' };
                  let displayType = typeMap[m.memberType] || m.memberType;

                  const kycMap: Record<string, string> = {
                    verified: 'Verified',
                    re_kyc_due: 'Re-KYC due',
                    kyc_expired: 'KYC expired',
                    pending: 'Pending'
                  };
                  let displayKyc = kycMap[m.kycStatus] || m.kycStatus;

                  const statusMap: Record<string, string> = {
                    active: 'Active',
                    inactive: 'Inactive',
                    under_review: 'Under review'
                  };
                  let displayStatus = statusMap[m.activeStatus] || m.activeStatus;
                  
                  let formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(m.registeredOn));

                  return (
                    <tr key={m.id} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold text-slate-900">{displayName}</td>
                      <td className="table-cell num text-slate-600">{m.folioNumber}</td>
                      <td className="table-cell text-xs font-medium text-slate-700">{displayType}</td>
                      <td className="table-cell text-right num">{m.sharesHeld.toLocaleString('en-IN')}</td>
                      <td className="table-cell">
                        <StatusBadge label={displayKyc} size="sm" />
                      </td>
                      <td className="table-cell">
                        <StatusBadge label={displayStatus} size="sm" />
                      </td>
                      <td className="table-cell text-right num font-medium">{fmt(m.currentExposure)}</td>
                      <td className="table-cell text-slate-600">{formattedDate}</td>
                    </tr>
                  );
                })}`;

code = code.replace(oldLoop, newLoop);

fs.writeFileSync(file, code);
console.log("update complete");
