const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldFilters = `<p className="text-sm font-semibold text-slate-700">Audit Log Explorer</p>
              <span className="text-xs text-slate-400 ml-auto">{filteredAudit.length} events</span>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="relative flex-1 min-w-48">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search actor, entity ID, event type…"
                  value={auditSearch}
                  onChange={e => setAuditSearch(e.target.value)}
                  className="field-input pl-8 text-sm py-2 w-full"
                />
              </div>
              <select value={auditRoleFilter} onChange={e => setAuditRoleFilter(e.target.value)} className="field-select text-sm py-2">
                <option value="all">All Roles</option>
                <option value="deputy_manager_finance">Deputy Manager – Finance</option>
                <option value="credit_manager">Credit Manager</option>
                <option value="cfo">CFO</option>
                <option value="company_secretary">Company Secretary</option>
                <option value="director">Director</option>
                <option value="accounts">Accounts</option>
              </select>
              <select value={auditEntityFilter} onChange={e => setAuditEntityFilter(e.target.value)} className="field-select text-sm py-2">
                <option value="all">All Entity Types</option>
                <option value="application">Application</option>
                <option value="loan_account">Loan Account</option>
                <option value="member">Member</option>
                <option value="security">Security</option>
              </select>`;

const newFilters = `<p className="text-sm font-semibold text-slate-700">Audit log explorer</p>
              <span className="text-xs text-slate-400 ml-auto">{filteredAudit.length} events</span>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="relative flex-1 min-w-48">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search actor, entity ID, event type…"
                  value={auditSearch}
                  onChange={e => setAuditSearch(e.target.value)}
                  className="field-input pl-8 text-sm py-2 w-full"
                />
              </div>
              <select value={auditRoleFilter} onChange={e => setAuditRoleFilter(e.target.value)} className="field-select text-sm py-2">
                <option value="all">All roles</option>
                <option value="deputy_manager_finance">Deputy Manager – Finance</option>
                <option value="credit_manager">Credit Manager</option>
                <option value="cfo">CFO</option>
                <option value="company_secretary">Company Secretary</option>
                <option value="director">Director</option>
                <option value="accounts">Accounts</option>
              </select>
              <select value={auditEntityFilter} onChange={e => setAuditEntityFilter(e.target.value)} className="field-select text-sm py-2">
                <option value="all">All entity types</option>
                <option value="application">Application</option>
                <option value="loan_account">Loan Account</option>
                <option value="member">Member</option>
                <option value="security">Security</option>
              </select>`;

code = code.replace(oldFilters, newFilters);

const oldRowMap = `{filteredAudit.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="table-cell text-center text-slate-400 py-8">No events match the current filters.</td>
                    </tr>
                  ) : filteredAudit.map(ev => (
                    <tr key={ev.id} className="hover:bg-slate-50">
                      <td className="table-cell text-xs text-slate-500 whitespace-nowrap">{new Date(ev.timestamp).toLocaleString('en-IN')}</td>
                      <td className="table-cell font-medium text-slate-900">{ev.actorName}</td>
                      <td className="table-cell text-xs text-slate-500 capitalize">{ev.actorRole.replace(/_/g, ' ')}</td>
                      <td className="table-cell text-xs text-slate-500 capitalize">{ev.entityType.replace(/_/g, ' ')}</td>
                      <td className="table-cell font-mono text-xs text-slate-600">{ev.entityId}</td>
                      <td className="table-cell font-medium text-slate-800">{ev.eventType}</td>
                      <td className="table-cell">
                        {ev.previousState
                          ? <span className="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{ev.previousState}</span>
                          : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="table-cell">
                        {ev.newState
                          ? <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{ev.newState}</span>
                          : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="table-cell text-xs text-slate-500 max-w-xs truncate">{ev.comment || '—'}</td>
                    </tr>
                  ))}`;

const newRowMap = `{filteredAudit.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="table-cell text-center text-slate-400 py-8">No events match the current filters.</td>
                    </tr>
                  ) : filteredAudit.map(ev => {
                    const formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true }).format(new Date(ev.timestamp));
                    
                    let displayActor = ev.actorName;
                    if (displayActor === 'Credit Assessment Team') displayActor = 'System';
                    if (displayActor === 'System Admin' && (ev.eventType.includes('Sanction') || ev.eventType.includes('Document'))) {
                        displayActor = 'System';
                    }

                    const roleMap: Record<string, string> = {
                      deputy_manager_finance: 'Deputy Manager – Finance',
                      credit_manager: 'Credit Manager',
                      cfo: 'CFO',
                      company_secretary: 'Company Secretary',
                      director: 'Director',
                      system: 'System'
                    };
                    let displayRole = roleMap[ev.actorRole] || ev.actorRole.replace(/_/g, ' ');

                    let displayEntityId = ev.entityId;
                    const matchedApp = loanApplications.find(a => a.id === ev.entityId);
                    if (matchedApp) displayEntityId = matchedApp.applicationNumber;
                    const matchedLoan = loanAccounts.find(l => l.id === ev.entityId);
                    if (matchedLoan) displayEntityId = matchedLoan.accountNumber;

                    const eventMap: Record<string, string> = {
                      'Application Submitted': 'Application submitted',
                      'Reference Number Generated': 'Reference number generated',
                      'Appraisal Note Prepared': 'Appraisal note prepared',
                      'Submitted to Sanction Committee': 'Submitted to Sanction Committee',
                      'Sanction Approved': 'Sanction approved',
                      'Document Pack Generated': 'Document pack generated',
                      'Default Recovery Action Initiated': 'Default recovery action initiated',
                      'Repayment Posted': 'Repayment posted'
                    };
                    let displayEvent = eventMap[ev.eventType] || ev.eventType;
                    if (displayEvent.toLowerCase() === displayEvent) {
                       displayEvent = displayEvent.charAt(0).toUpperCase() + displayEvent.slice(1);
                    }

                    const stateMap: Record<string, string> = {
                      submitted: 'Submitted',
                      reference_generated: 'Reference issued',
                      appraisal_pending: 'Appraisal pending',
                      credit_review: 'Credit review',
                      pending_sanction: 'Pending sanction',
                      sanctioned: 'Sanctioned',
                      active: 'Active',
                      default_review: 'Default review',
                      recovery_in_progress: 'Recovery in progress'
                    };
                    let displayPrev = ev.previousState ? (stateMap[ev.previousState] || ev.previousState) : null;
                    let displayNew = ev.newState ? (stateMap[ev.newState] || ev.newState) : null;

                    return (
                      <tr key={ev.id} className="hover:bg-slate-50">
                        <td className="table-cell text-xs text-slate-500 whitespace-nowrap">{formattedDate}</td>
                        <td className="table-cell font-medium text-slate-900">{displayActor}</td>
                        <td className="table-cell text-xs text-slate-500 capitalize">{displayRole}</td>
                        <td className="table-cell text-xs text-slate-500 capitalize">{ev.entityType.replace(/_/g, ' ')}</td>
                        <td className="table-cell font-mono text-xs text-slate-600">{displayEntityId}</td>
                        <td className="table-cell font-medium text-slate-800">{displayEvent}</td>
                        <td className="table-cell">
                          {displayPrev
                            ? <span className="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{displayPrev}</span>
                            : <span className="text-slate-300">—</span>}
                        </td>
                        <td className="table-cell">
                          {displayNew
                            ? <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{displayNew}</span>
                            : <span className="text-slate-300">—</span>}
                        </td>
                        <td className="table-cell text-xs text-slate-500 max-w-xs truncate" title={ev.comment}>{ev.comment || '—'}</td>
                      </tr>
                    );
                  })}`;

code = code.replace(oldRowMap, newRowMap);
fs.writeFileSync(file, code);

console.log("update complete");
