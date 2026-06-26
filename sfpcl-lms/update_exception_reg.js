const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// Title & Subtitle for Exception Tab
code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <AlertOctagon size={14} className="text-violet-600" /> Exception Register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Applications where requested amount exceeds eligible limit — {exceptions.length} records</p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <AlertOctagon size={14} className="text-violet-600" /> Exception register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Open and approved exception records — {exceptions.length} records</p>`
);

// Map Loop for Exception Register
const oldLoop = `{exceptions.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">No exception cases on record.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {exceptions.map(app => (
                <div key={app.id} className="p-4 bg-violet-50/50">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-900 num">{app.applicationNumber}</span>
                        <StatusBadge label={app.status} size="sm" />
                      </div>
                      <p className="text-sm text-slate-700 mt-1">{app.memberName} · {fmt(app.requestedAmount)} requested · {fmt(app.eligibleAmount)} eligible</p>
                      <p className="text-xs text-violet-700 mt-1 bg-violet-50 rounded px-2 py-1">{app.exceptionReason}</p>
                    </div>
                    <div className="text-xs text-slate-400 flex-shrink-0">{app.applicationDate}</div>
                  </div>
                </div>
              ))}
            </div>
          )}`;

const newLoop = `{exceptions.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">No exception cases on record.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {exceptions.map(app => {
                let excType = 'Limit breach';
                let excDesc = \`\`;
                let authority = 'CFO + 2 Directors required';
                
                if (app.requestedAmount === app.eligibleAmount && app.requestedAmount > 500000) {
                  excType = 'High-value approval';
                  excDesc = \`\${excType}: \${authority}.\`;
                } else {
                  let diff = app.requestedAmount - app.eligibleAmount;
                  if (diff > 0) {
                    excDesc = \`Limit breach: requested \${fmt(app.requestedAmount)} vs eligible \${fmt(app.eligibleAmount)}; excess \${fmt(diff)}.\`;
                  } else {
                    excDesc = \`Limit breach: requested \${fmt(app.requestedAmount)} vs eligible \${fmt(app.eligibleAmount)}.\`;
                  }
                }

                let excStatus = app.sanctionDecision === 'approved' ? 'Approved' : 'Open';
                let formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(app.applicationDate));

                return (
                  <div key={app.id} className="p-4 bg-violet-50/50 hover:bg-violet-50/80 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900 num">{app.applicationNumber}</span>
                          <StatusBadge label={app.status} size="sm" />
                          <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${excStatus === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}\`}>
                            Exception: {excStatus}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-slate-800 mt-1.5">{app.memberName}</p>
                        <p className="text-sm text-slate-600 mt-0.5">{excDesc}</p>
                        <p className="text-xs text-violet-700 mt-1.5 font-medium flex items-center gap-1.5 bg-violet-100/50 w-max px-2 py-1 rounded">
                          <AlertOctagon size={12} /> {excType} ({authority})
                        </p>
                      </div>
                      <div className="text-xs font-medium text-slate-500 flex-shrink-0">{formattedDate}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}`;

code = code.replace(oldLoop, newLoop);

fs.writeFileSync(file, code);

// Tab overflow fix in Tabs.tsx
const tabsFile = 'src/components/ui/Tabs.tsx';
let tabsCode = fs.readFileSync(tabsFile, 'utf8');
tabsCode = tabsCode.replace(
  `<div className="flex gap-0 min-w-max">`,
  `<div className="flex gap-0 min-w-max pr-6">`
);
fs.writeFileSync(tabsFile, tabsCode);

console.log("update complete");
