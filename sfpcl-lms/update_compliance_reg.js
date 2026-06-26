const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldCode = `{/* Tab 5: Audit Log */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <RotateCcw size={14} className="text-green-600" /> Audit Log
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Compliance records — retained for 8 years per SOP</p>
          </div>
          <div className="divide-y divide-slate-100">
            {complianceRecords.map(rec => (
              <div key={rec.id} className="flex items-center gap-4 p-4">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-900">{rec.area}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {rec.owner} · {rec.frequency} · {rec.evidenceCount} evidence records
                  </p>
                </div>
                <div className="text-right">
                  <StatusBadge label={rec.status} size="sm" />
                  <p className="text-xs text-slate-400 mt-1">Due: {new Date(rec.nextDueDate).toLocaleDateString('en-IN')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>`;

const newCode = `{/* Tab 6: Compliance Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <BookOpen size={14} className="text-green-600" /> Compliance register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Compliance controls and evidence records</p>
          </div>
          <div className="divide-y divide-slate-100">
            {complianceRecords.map(rec => {
              const areaMap: Record<string, string> = {
                'Producer Company lending': 'Producer Company lending — members only',
                'Section 186 limit check': 'Section 186 loan limits',
                'NBFC principal business test': 'NBFC principal business test',
                'KYC & AML verification': 'KYC / AML verification',
                'Re-KYC cycle': 'Re-KYC cycle',
                'Stamp duty & notarisation': 'Stamp duty & notarisation',
                'Money-lending exemption': 'Money-lending law exemption review'
              };
              let displayArea = areaMap[rec.area] || rec.area;

              const ownerMap: Record<string, string> = {
                'Producer Company lending — members only': 'Company Secretary',
                'Section 186 loan limits': 'CFO',
                'NBFC principal business test': 'CFO',
                'KYC / AML verification': 'Compliance Team',
                'Re-KYC cycle': 'Compliance Team',
                'Stamp duty & notarisation': 'Company Secretary',
                'Money-lending law exemption review': 'Company Secretary'
              };
              let displayOwner = ownerMap[displayArea] || rec.owner;
              
              let isOverdue = new Date(rec.nextDueDate) < new Date();
              let displayStatus = rec.status;
              
              if (rec.status === 'compliant') displayStatus = 'Compliant';
              else if (rec.status === 'warning') displayStatus = 'Warning';
              else if (rec.status === 'pending') {
                if (isOverdue) displayStatus = 'Overdue';
                else displayStatus = 'Pending';
              } else {
                 displayStatus = rec.status;
              }
              
              let statusColor = displayStatus === 'Compliant' ? 'bg-green-100 text-green-700' :
                                displayStatus === 'Warning' ? 'bg-amber-100 text-amber-700' :
                                displayStatus === 'Overdue' ? 'bg-red-100 text-red-700' :
                                'bg-slate-100 text-slate-700';
                                
              let formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(rec.nextDueDate));
              
              let evidenceText = rec.evidenceCount === 1 ? '1 evidence record' : \`\${rec.evidenceCount} evidence records\`;
              
              return (
              <div key={rec.id} className="flex items-center gap-4 p-4 hover:bg-slate-50 transition-colors">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-900">{displayArea}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {displayOwner} · {rec.frequency} · {evidenceText}
                  </p>
                </div>
                <div className="text-right">
                  <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                    {displayStatus}
                  </span>
                  <p className="text-xs text-slate-500 font-medium mt-1.5">Due: {formattedDate}</p>
                </div>
              </div>
            )})}
          </div>
        </div>`;

code = code.replace(oldCode, newCode);

fs.writeFileSync(file, code);
console.log("update complete");
