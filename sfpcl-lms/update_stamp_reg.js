const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// Title check
code = code.replace(
  `All statutory and internal registers · 8-year tention`,
  `All statutory and internal registers · 8-year retention`
);
code = code.replace(
  `All statutory and internal registers · 8 -year retention`,
  `All statutory and internal registers · 8-year retention`
);

// Stamp Duty Array replacement
const oldData = `const stampDutyRecords = [
    { doc: 'Power of Attorney (PoA)', appNo: 'LO00000042', borrower: 'Ganesh Thorat', stampDutyAmt: 500, paidOn: '2024-09-18', status: 'paid', notarised: true, custodian: 'Company Secretary', challanNo: 'MSFM2024082100012' },
    { doc: 'SH-4 Transfer Form', appNo: 'LO00000042', borrower: 'Ganesh Thorat', stampDutyAmt: 200, paidOn: '2024-09-15', status: 'paid', notarised: false, custodian: 'Company Secretary', challanNo: 'MSFM2024082100013' },
    { doc: 'Power of Attorney (PoA)', appNo: 'LO00000035', borrower: 'Sunita Bhosale', stampDutyAmt: 500, paidOn: '2026-04-22', status: 'paid', notarised: true, custodian: 'Company Secretary', challanNo: 'MSFM2026042200001' },
    { doc: 'Loan Agreement', appNo: 'LO00000047', borrower: 'Vijay Deshmukh', stampDutyAmt: 300, paidOn: null, status: 'pending', notarised: false, custodian: null, challanNo: null },
  ];`;

const newData = `const stampDutyRecords = [
    { doc: 'Power of Attorney (PoA)', appNo: 'LO00000042', borrower: 'Ganesh Thorat', stampDutyAmt: 500, paidOn: '2024-09-18', status: 'paid', notarised: true, custodian: 'Company Secretary', challanNo: 'MSFM2024082100012' },
    { doc: 'SH-4 transfer form', appNo: 'LO00000042', borrower: 'Ganesh Thorat', stampDutyAmt: 'Not required', paidOn: '2024-09-15', status: 'paid', notarised: 'not_required', custodian: 'Company Secretary', challanNo: 'MSFM2024082100013' },
    { doc: 'Power of Attorney (PoA)', appNo: 'LO00000035', borrower: 'Kisan FPC Ltd', stampDutyAmt: 500, paidOn: '2026-04-22', status: 'paid', notarised: true, custodian: 'Company Secretary', challanNo: 'MSFM2026042200001' },
    { doc: 'Loan Agreement', appNo: 'LO00000047', borrower: 'Vijay Deshmukh', stampDutyAmt: 500, paidOn: 'pending', status: 'pending', notarised: 'pending', custodian: 'not_assigned', challanNo: 'pending' },
  ];`;

code = code.replace(oldData, newData);

// Tab UI
const oldTab = `{/* Tab 5: Stamp Duty Register (S66) */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Stamp duty register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Stamp duty and notarisation records for all security documents</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  {['Document Type', 'Application No.', 'Borrower', 'Stamp Duty Amt', 'Paid On', 'Challan No.', 'Notarised', 'Custodian', 'Status'].map(h => (
                    <th key={h} className="table-header text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stampDutyRecords.map((row, i) => (
                  <tr key={i} className={\`hover:bg-slate-50 \${row.status === 'pending' ? 'bg-amber-50/30' : ''}\`}>
                    <td className="table-cell font-medium text-slate-800">{row.doc}</td>
                    <td className="table-cell num text-slate-600">{row.appNo}</td>
                    <td className="table-cell text-slate-700">{row.borrower}</td>
                    <td className="table-cell num text-slate-900 font-semibold">₹{row.stampDutyAmt}</td>
                    <td className="table-cell text-slate-600">{row.paidOn || '—'}</td>
                    <td className="table-cell font-mono text-xs text-slate-500">{row.challanNo || '—'}</td>
                    <td className="table-cell">
                      {row.notarised
                        ? <span className="text-xs text-green-700 font-semibold">Yes ✓</span>
                        : <span className="text-xs text-amber-600">No</span>}
                    </td>
                    <td className="table-cell text-slate-600">{row.custodian || '—'}</td>
                    <td className="table-cell"><StatusBadge label={row.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 7: Stamp Duty Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <FileText size={14} className="text-green-600" /> Stamp duty register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Stamp duty and notarisation records for security documents</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Document Type</th>
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Stamp Duty Amount</th>
                  <th className="table-header text-left">Paid On</th>
                  <th className="table-header text-left">Challan No.</th>
                  <th className="table-header text-left">Notarised</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stampDutyRecords.map((row, i) => {
                  
                  let amtDisplay = typeof row.stampDutyAmt === 'number' ? fmt(row.stampDutyAmt) : row.stampDutyAmt;
                  
                  let dateDisplay = '—';
                  if (row.paidOn === 'pending') {
                    dateDisplay = 'Pending';
                  } else if (row.paidOn) {
                    dateDisplay = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(row.paidOn));
                  }
                  
                  let challanDisplay = row.challanNo === 'pending' ? 'Pending' : (row.challanNo || '—');
                  let custodianDisplay = row.custodian === 'not_assigned' ? 'Not assigned' : (row.custodian || '—');
                  
                  let notDisplay = null;
                  if (row.notarised === 'not_required') {
                    notDisplay = <span className="text-xs text-slate-500 font-medium">Not required</span>;
                  } else if (row.notarised === 'pending') {
                    notDisplay = <span className="text-xs text-amber-600 font-medium">Pending notarisation</span>;
                  } else if (row.notarised === true) {
                    notDisplay = <span className="text-xs text-green-700 font-semibold">Yes ✓</span>;
                  } else {
                    notDisplay = <span className="text-xs text-amber-600 font-medium">Pending notarisation</span>;
                  }

                  let statusDisplay = row.status === 'paid' && row.notarised === false ? 'pending_notarisation' : row.status;

                  return (
                    <tr key={i} className={\`hover:bg-slate-50 \${row.status === 'pending' ? 'bg-amber-50/30' : ''}\`}>
                      <td className="table-cell font-medium text-slate-800">{row.doc}</td>
                      <td className="table-cell num text-slate-600">{row.appNo}</td>
                      <td className="table-cell text-slate-700">{row.borrower}</td>
                      <td className="table-cell num text-slate-900 font-semibold">{amtDisplay}</td>
                      <td className="table-cell text-slate-600">{dateDisplay}</td>
                      <td className="table-cell font-mono text-xs text-slate-500">{challanDisplay}</td>
                      <td className="table-cell">{notDisplay}</td>
                      <td className="table-cell text-slate-600">{custodianDisplay}</td>
                      <td className="table-cell"><StatusBadge label={statusDisplay} size="sm" /></td>
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
