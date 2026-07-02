import React, { useState } from 'react';
import { useRole } from '../../contexts/RoleContext';
import { History, ShieldCheck, Download, ExternalLink, Filter, Archive, X as XIcon, Trash2, FileText, AlertCircle } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { auditEvents } from '../../data/mockData';

const TABS = ['Audit Log', 'Workflow Timeline', 'Archive Register', 'Evidence Packs'];

const fmt = (n?: number) => n !== undefined && n !== null ? '₹' + n.toLocaleString('en-IN') : '—';

const AuditArchiveHub: React.FC = () => {
  const { currentUser, can } = useRole();
  const [activeTab, setActiveTab] = useState('Audit Log');
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [selectedPack, setSelectedPack] = useState<any>(null);
  
  const isAuditor = currentUser.role === 'auditor';
  const isAdmin = currentUser.role === 'admin';
  const canArchive = ['company_secretary', 'admin'].includes(currentUser.role);
  const canExport = ['admin', 'company_secretary', 'cfo', 'compliance_team'].includes(currentUser.role) || (isAuditor && can('export_registers'));

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <History size={20} className="text-indigo-600" />
            Audit & Archive
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Review system events, evidence packs, closed files and retention status.
          </p>
        </div>
        {isAuditor && (
          <div className="bg-slate-100 px-4 py-2 rounded-lg flex items-center gap-2 border border-slate-200">
            <ShieldCheck size={16} className="text-indigo-600" />
            <span className="text-sm font-medium text-slate-700">Read-only access — audit logs and archived records cannot be edited.</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Audit Events — 30d</div>
          <div className="text-2xl font-bold text-slate-900">{auditEvents.length}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Restricted Downloads</div>
          <div className="text-2xl font-bold text-amber-600">3</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Open Audit Flags</div>
          <div className="text-2xl font-bold text-red-600">0</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Archive Pending</div>
          <div className="text-2xl font-bold text-slate-900">1</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Legal Hold</div>
          <div className="text-2xl font-bold text-violet-600">1</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col">
        <div className="border-b border-slate-200">
          <div className="flex gap-2 p-2 overflow-x-auto">
            {TABS.map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
                  activeTab === tab
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {activeTab === 'Audit Log' && (
          <>
            <div className="p-4 border-b border-slate-200 flex flex-wrap gap-3 bg-slate-50/50">
              <input type="date" className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Date range" />
              <select className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">All Users</option>
              </select>
              <select className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">All Roles</option>
              </select>
              <input type="text" placeholder="Application / Loan ref" className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-indigo-500" />
              <select className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">Module</option>
              </select>
              <select className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">Action Type</option>
                <option value="exceptions">Exceptions</option>
                <option value="approvals">Approvals</option>
                <option value="changes">Before / after changes</option>
              </select>
              <button 
                className={`flex items-center gap-2 text-sm px-3 py-2 ml-auto rounded-lg border font-medium transition-colors ${canExport ? 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50' : 'bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed'}`}
                title={!canExport ? "Export requires permission." : undefined}
                disabled={!canExport}
              >
                <Download size={14} /> Export audit log
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Timestamp</th>
                    <th className="table-header text-left">User</th>
                    <th className="table-header text-left">Role</th>
                    <th className="table-header text-left">Module</th>
                    <th className="table-header text-left">Action</th>
                    <th className="table-header text-left">Record</th>
                    <th className="table-header text-left">IP / Device</th>
                    <th className="table-header text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {auditEvents.slice(0, 15).map(ev => (
                    <tr key={ev.id} className="hover:bg-slate-50">
                      <td className="table-cell text-slate-600 font-mono text-xs">
                        {new Date(ev.timestamp).toLocaleString('en-GB')}
                      </td>
                      <td className="table-cell font-medium text-slate-900">{ev.actorName}</td>
                      <td className="table-cell text-slate-600 capitalize">{ev.actorRole.replace(/_/g, ' ')}</td>
                      <td className="table-cell text-slate-600 capitalize">{ev.entityType.replace(/_/g, ' ')}</td>
                      <td className="table-cell">
                        <span className="font-medium text-slate-800">{ev.eventType}</span>
                        {ev.comment && <div className="text-xs text-slate-500 truncate max-w-[200px]">{ev.comment}</div>}
                      </td>
                      <td className="table-cell font-mono text-xs text-indigo-600 num">{ev.entityId}</td>
                      <td className="table-cell font-mono text-xs text-slate-500">192.168.1.100<br/>Mac OS</td>
                      <td className="table-cell text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={() => setSelectedEvent(ev)}
                            className="text-indigo-600 hover:text-indigo-800 font-medium text-xs px-2 py-1 rounded hover:bg-indigo-50 transition-colors"
                          >
                            View event
                          </button>
                          <button 
                            className="text-slate-600 hover:text-slate-800 font-medium text-xs px-2 py-1 rounded hover:bg-slate-100 transition-colors flex items-center gap-1"
                            onClick={() => {
                              if (isAdmin && !can('view_loan_accounts')) {
                                alert('You do not have permission to open this linked record.');
                              } else {
                                // Mock navigation
                              }
                            }}
                            title={isAdmin && !can('view_loan_accounts') ? "You do not have permission to open this linked record." : undefined}
                          >
                            Open linked record <ExternalLink size={12} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === 'Workflow Timeline' && (
          <div className="p-6">
            <div className="max-w-3xl space-y-4">
              {[
                { id: 1, action: 'Sanction approved', detail: 'pending_sanction → sanctioned', user: 'Rajesh Sharma · Sanction Committee', date: '25 May 2026 at 07:30 PM', linkedRef: 'LO00000039' },
                { id: 2, action: 'Disbursement initiated', detail: 'disbursement_ready → payment_initiated', user: 'Amit Deshmukh · Senior Manager – Finance', date: '26 May 2026 at 10:15 AM', linkedRef: 'LO00000039' },
                { id: 3, action: 'Exception flagged', detail: 'limit_check_passed → exception_flagged', user: 'System · Limit check', date: '27 May 2026 at 09:00 AM', linkedRef: 'LO00000047' },
              ].map(event => (
                <div key={event.id} className="flex gap-4">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 mt-2 flex-shrink-0" />
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex-1 flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-slate-900">{event.action}</p>
                      <p className="text-sm font-mono text-slate-600 mt-1">{event.detail}</p>
                      <p className="text-xs text-slate-500 mt-2">{event.user}</p>
                      <p className="text-xs font-mono text-indigo-600 mt-1">Ref: {event.linkedRef}</p>
                    </div>
                    <div className="text-xs font-medium text-slate-500">{event.date}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'Archive Register' && (
          <div className="flex flex-col">
            <div className="p-4 bg-slate-50/50 border-b border-slate-200 flex items-center justify-between">
              <span className="text-sm text-slate-600 font-medium">Loan records must be retained for at least 8 years after closure.</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Loan account</th>
                    <th className="table-header text-left">Borrower</th>
                    <th className="table-header text-left">Closure date</th>
                    <th className="table-header text-left">Archive date</th>
                    <th className="table-header text-left">Retention period</th>
                    <th className="table-header text-left">Retention end</th>
                    <th className="table-header text-left">Archive loc.</th>
                    <th className="table-header text-left">Physical ref</th>
                    <th className="table-header text-left">Checksum</th>
                    <th className="table-header text-left">Legal hold</th>
                    <th className="table-header text-left">Status</th>
                    <th className="table-header text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { loan: 'LN-2025-0025', borrower: 'Radha Kisan Org', closed: '2025-03-28', archived: '2025-04-10', retentionPeriod: '8 years', retention: '2033-03-28', loc: 'Cabinet 3, Row 2', physicalRef: 'PF-2025-025', checksum: 'sha256: e3b0...', legalHold: 'No', status: 'Archived' },
                    { loan: 'LN-2023-0021', borrower: 'Ganesh Thorat', closed: '2023-03-20', archived: '2023-03-25', retentionPeriod: '8 years', retention: '2031-03-20', loc: 'Cabinet 1, Row 4', physicalRef: 'PF-2023-089', checksum: 'sha256: 9f86...', legalHold: 'No', status: 'Archived' },
                    { loan: 'LN-2026-0031', borrower: 'Asha Bhosale', closed: '2026-06-20', archived: '—', retentionPeriod: '8 years', retention: '2034-06-20', loc: '—', physicalRef: '—', checksum: '—', legalHold: 'No', status: 'Pending' },
                    { loan: 'LN-2019-0018', borrower: 'Sanjay Pawar', closed: '2019-01-10', archived: '2019-01-15', retentionPeriod: '8 years', retention: '2027-01-10', loc: 'Offsite Storage', physicalRef: 'PF-2019-011', checksum: 'sha256: 4a1d...', legalHold: 'Yes', status: 'Legal Hold' },
                    { loan: 'LN-2015-0045', borrower: 'Priya Desai', closed: '2015-05-15', archived: '2015-05-20', retentionPeriod: '8 years', retention: '2023-05-15', loc: 'Offsite Storage', physicalRef: 'PF-2015-045', checksum: 'sha256: 8b1a...', legalHold: 'No', status: 'Retention Due' },
                  ].map((row, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold text-slate-900 num">{row.loan}</td>
                      <td className="table-cell font-medium text-slate-800">{row.borrower}</td>
                      <td className="table-cell text-slate-600">{row.closed}</td>
                      <td className="table-cell text-slate-600">{row.archived}</td>
                      <td className="table-cell text-slate-600">{row.retentionPeriod}</td>
                      <td className="table-cell font-medium text-slate-800">{row.retention}</td>
                      <td className="table-cell text-slate-600">{row.loc}</td>
                      <td className="table-cell text-slate-600">{row.physicalRef}</td>
                      <td className="table-cell text-slate-500 font-mono text-xs">{row.checksum}</td>
                      <td className="table-cell text-slate-800 font-medium">{row.legalHold}</td>
                      <td className="table-cell">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full whitespace-nowrap ${
                          row.status === 'Archived' ? 'bg-indigo-100 text-indigo-700' :
                          row.status === 'Pending' ? 'bg-amber-100 text-amber-700' :
                          row.status === 'Legal Hold' ? 'bg-violet-100 text-violet-700' :
                          row.status === 'Retention Due' ? 'bg-red-100 text-red-700' :
                          row.status === 'Destroyed' ? 'bg-slate-100 text-slate-700' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {row.status}
                        </span>
                      </td>
                      <td className="table-cell text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button className="text-indigo-600 hover:text-indigo-800 font-medium text-xs px-2 py-1 rounded hover:bg-indigo-50 transition-colors">
                            View
                          </button>
                          {!isAuditor && canArchive && (
                            <div className="relative group">
                              <button className="text-slate-600 hover:text-slate-900 font-medium text-xs px-2 py-1 rounded hover:bg-slate-100 transition-colors">
                                Actions ▾
                              </button>
                              <div className="absolute right-0 mt-1 w-56 bg-white border border-slate-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 flex flex-col text-left overflow-hidden">
                                {row.status === 'Pending' && <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left flex items-center gap-2"><Archive size={12}/> Archive file</button>}
                                <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left flex items-center gap-2"><Download size={12}/> Download archive manifest</button>
                                <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left flex items-center gap-2"><ExternalLink size={12}/> View archived documents</button>
                                {row.status === 'Retention Due' && row.legalHold === 'No' && (
                                  <button className="px-3 py-2 text-xs text-red-600 hover:bg-red-50 text-left flex items-center gap-2 border-t border-slate-100"><Trash2 size={12}/> Record destruction</button>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'Evidence Packs' && (
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'Loan File Audit Pack', desc: 'Application, appraisal, sanction and register records.', date: 'Generated: 25 Jun 2026', count: 42, user: 'Priya Kulkarni', linkedRef: 'LO00000039' },
              { title: 'Sanction Evidence Pack', desc: 'Committee approvals, approval authority, exception notes and limit checks.', date: 'Generated: 24 Jun 2026', count: 12, user: 'Rajesh Sharma', linkedRef: 'LO00000039' },
              { title: 'Documentation Evidence Pack', desc: 'Executed agreements, stamp duty challans, PoA and security records.', date: 'Generated: 20 Jun 2026', count: 28, user: 'Anita Kulkarni', linkedRef: 'LO00000039' },
              { title: 'Disbursement Evidence Pack', desc: 'Payment package, UTR, bank reference and CFC authorisation.', date: 'Generated: 18 Jun 2026', count: 15, user: 'Deepak Rao', linkedRef: 'LO00000039' },
              { title: 'Closure / Archive Evidence Pack', desc: 'NOC, security return, unpledge evidence and archive manifest.', date: 'Generated: 15 Jun 2026', count: 8, user: 'Meera Joshi', linkedRef: 'LN-2025-0025' },
              { title: 'Compliance Evidence Pack', desc: 'Section 186, NBFC, KYC, stamp duty and access review evidence.', date: 'Generated: 10 Jun 2026', count: 35, user: 'Compliance Team', linkedRef: 'Global' },
            ].map((pack, i) => (
              <div key={i} className="bg-slate-50 border border-slate-200 p-4 rounded-xl flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                    <FileText size={16} className="text-indigo-600" /> {pack.title}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-snug max-w-sm">{pack.desc}</p>
                  <p className="text-xs text-slate-500 mt-2">Items: <span className="font-medium text-slate-700">{pack.count}</span> • Linked: <span className="font-mono text-indigo-600">{pack.linkedRef}</span></p>
                  <p className="text-xs font-mono text-slate-400 mt-1">{pack.date} by {pack.user}</p>
                </div>
                <div className="flex flex-col gap-2 shrink-0 ml-4">
                  <button onClick={() => setSelectedPack(pack)} className="btn-secondary text-xs px-3 py-1.5 flex justify-center">View</button>
                  <button 
                    className={`btn-primary text-xs px-3 py-1.5 flex justify-center items-center gap-1 ${!canExport ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title={!canExport ? "Download requires permission." : undefined}
                    disabled={!canExport}
                  ><Download size={12} /> Download</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedEvent && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setSelectedEvent(null)} />
          <div className="w-[550px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col transform transition-transform duration-300">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">View Event</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">{selectedEvent.id}</div>
              </div>
              <button 
                onClick={() => setSelectedEvent(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <XIcon size={20} />
              </button>
            </div>
            
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-x-4 gap-y-6 text-sm">
                <div>
                  <div className="text-slate-500 mb-1">Timestamp</div>
                  <div className="font-medium font-mono text-slate-900">{new Date(selectedEvent.timestamp).toLocaleString('en-GB')}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Request ID</div>
                  <div className="font-medium font-mono text-slate-900 text-xs">req_8f7d6a5b4c3d2e1</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Actor Name</div>
                  <div className="font-medium text-slate-900">{selectedEvent.actorName}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Role at time of action</div>
                  <div className="font-medium text-slate-900 capitalize">{selectedEvent.actorRole.replace(/_/g, ' ')}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Team at time of action</div>
                  <div className="font-medium text-slate-900 capitalize">{(selectedEvent.actorRole.includes('admin') ? 'IT' : 'Business Team')}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Module</div>
                  <div className="font-medium text-slate-900 capitalize">{selectedEvent.entityType.replace(/_/g, ' ')}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Action Code</div>
                  <div className="font-medium text-slate-900 uppercase">{selectedEvent.eventType.replace(/\s+/g, '_')}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Action Label</div>
                  <div className="font-medium text-slate-900">{selectedEvent.eventType}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Entity ID (Linked Record)</div>
                  <div className="font-medium text-indigo-600 font-mono text-xs">{selectedEvent.entityId}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Outcome</div>
                  <div className="font-medium text-green-600">Success</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">IP address</div>
                  <div className="font-medium font-mono text-slate-900 text-xs">192.168.1.100</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">User agent / device</div>
                  <div className="font-medium font-mono text-slate-900 text-xs">Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)</div>
                </div>
              </div>

              <div className="border-t border-slate-100 pt-6 space-y-4">
                {selectedEvent.previousState && (
                  <div>
                    <div className="text-sm text-slate-500 mb-2">Before Value</div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm font-mono text-slate-600">
                      State: {selectedEvent.previousState}
                    </div>
                  </div>
                )}
                {selectedEvent.newState && (
                  <div>
                    <div className="text-sm text-slate-500 mb-2">After Value</div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm font-mono text-slate-600">
                      State: {selectedEvent.newState}
                    </div>
                  </div>
                )}
                
                {selectedEvent.comment && (
                  <div>
                    <div className="text-sm text-slate-500 mb-2">Reason / Comment</div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm text-slate-800">
                      {selectedEvent.comment}
                    </div>
                  </div>
                )}
                
                {selectedEvent.reason && (
                  <div>
                    <div className="text-sm text-slate-500 mb-2">Reason</div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm text-slate-800">
                      {selectedEvent.reason}
                    </div>
                  </div>
                )}
                
                <div>
                  <div className="text-sm text-slate-500 mb-2">Evidence links</div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 flex flex-col gap-2">
                    <button className="text-sm text-indigo-600 hover:underline flex items-center gap-1 font-medium"><ExternalLink size={14}/> View associated document pack</button>
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 flex items-start gap-2">
                  <AlertCircle size={16} className="mt-0.5 shrink-0"/>
                  <span>Sensitive values (e.g., PAN, Aadhaar, bank details) are masked or redacted in audit logs.</span>
                </div>
              </div>
            </div>
            
            <div className="p-4 border-t border-slate-100 bg-slate-50">
              <div className="text-xs text-slate-500 mb-3 space-y-1">
                <p>• Audit logs are append-only.</p>
                <p>• System admins cannot alter audit contents.</p>
              </div>
              <div className="flex justify-end gap-2">
                <button 
                  onClick={() => setSelectedEvent(null)}
                  className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedPack && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setSelectedPack(null)} />
          <div className="w-[500px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col transform transition-transform duration-300">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Evidence Pack Detail</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">{selectedPack.title}</div>
              </div>
              <button 
                onClick={() => setSelectedPack(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <XIcon size={20} />
              </button>
            </div>
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="space-y-4">
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 flex items-start gap-2">
                  <AlertCircle size={16} className="mt-0.5 shrink-0"/>
                  <span>Sensitive pack download requires separate permission and reason. Sensitive values must be masked by default.</span>
                </div>
                <div className="text-sm text-slate-600">
                  Evidence packs are generated from immutable audit sources and cannot be edited.
                </div>
              </div>
            </div>
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
              <button 
                onClick={() => setSelectedPack(null)}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditArchiveHub;
