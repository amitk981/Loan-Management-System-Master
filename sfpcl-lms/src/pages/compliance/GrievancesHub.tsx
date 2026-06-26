import React, { useState } from 'react';
import { useRole } from '../../contexts/RoleContext';
import { MessageSquareWarning, Search, Filter, Download, AlertOctagon, Plus, X as XIcon, ChevronRight } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { grievances } from '../../data/mockData';

const TABS = ['Open', 'Overdue', 'Recovery-related', 'Escalated', 'Resolved', 'Closed'];

const GrievancesHub: React.FC = () => {
  const { currentUser, can } = useRole();
  const [activeTab, setActiveTab] = useState('Open');
  const [selectedGrievance, setSelectedGrievance] = useState<any>(null);
  
  const canManageGrievance = ['company_secretary', 'credit_manager', 'credit_head', 'field_officer'].includes(currentUser.role);
  const isAuditor = currentUser.role === 'auditor';
  const isAdmin = currentUser.role === 'admin';
  const canExport = ['admin', 'company_secretary', 'cfo', 'compliance_team'].includes(currentUser.role) || (isAuditor && can('export'));

  const overdueCount = grievances.filter(g => g.status === 'overdue').length;
  const recoveryCount = grievances.filter(g => g.category.toLowerCase().includes('recovery')).length;
  const showAlert = overdueCount > 0 || recoveryCount > 0;

  const filteredGrievances = grievances.filter(g => {
    if (activeTab === 'Open') return ['new', 'under_review', 'assigned', 'waiting_info', 'acknowledged'].includes(g.status);
    if (activeTab === 'Overdue') return g.status === 'overdue';
    if (activeTab === 'Recovery-related') return g.category.toLowerCase().includes('recovery');
    if (activeTab === 'Escalated') return g.status === 'escalated';
    if (activeTab === 'Resolved') return g.status === 'resolved';
    if (activeTab === 'Closed') return g.status === 'closed';
    return true;
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <MessageSquareWarning size={20} className="text-amber-600" />
            Grievances
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Track borrower complaints, TAT, assignment, resolution and closure.
          </p>
        </div>
        {!isAuditor && !isAdmin && canManageGrievance && (
          <button className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={16} />
            New Grievance
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Open Grievances</div>
          <div className="text-2xl font-bold text-slate-900">{grievances.filter(g => !['resolved', 'closed'].includes(g.status)).length}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Overdue TAT</div>
          <div className="text-2xl font-bold text-red-600">{overdueCount}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Recovery-related</div>
          <div className="text-2xl font-bold text-amber-600">{recoveryCount}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-sm font-medium text-slate-500 mb-1">Resolved in 30d</div>
          <div className="text-2xl font-bold text-green-600">{grievances.filter(g => g.status === 'resolved' || g.status === 'closed').length}</div>
        </div>
      </div>

      {showAlert && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg flex items-start gap-3">
          <AlertOctagon size={18} className="text-red-600 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-900">Attention Required</p>
            <p className="text-sm text-red-700 mt-0.5">
              {overdueCount} {overdueCount === 1 ? 'grievance' : 'grievances'} overdue. {recoveryCount > 0 ? 'Recovery-related complaints require CS review.' : ''}
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col">
        <div className="border-b border-slate-200">
          <div className="flex gap-2 p-2 overflow-x-auto">
            {TABS.map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
                  activeTab === tab
                    ? 'bg-amber-50 text-amber-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search grievances..."
                className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 w-64"
              />
            </div>
            <button className="btn-secondary flex items-center gap-2 text-sm px-3 py-2">
              <Filter size={14} /> Filter
            </button>
          </div>
          <button 
            className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg border font-medium transition-colors ${canExport ? 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50' : 'bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed'}`}
            title={!canExport ? "Export requires permission." : undefined}
            disabled={!canExport}
          >
            <Download size={14} /> Export
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="table-header text-left">Grievance ID</th>
                <th className="table-header text-left">Borrower / Loan</th>
                <th className="table-header text-left">Category / Mode</th>
                <th className="table-header text-left">Received</th>
                <th className="table-header text-left">Owner</th>
                <th className="table-header text-left">TAT</th>
                <th className="table-header text-left">Status</th>
                <th className="table-header text-left">Last update</th>
                <th className="table-header text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredGrievances.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center text-slate-500">
                    No grievances found in this view.
                  </td>
                </tr>
              ) : (
                filteredGrievances.map(g => (
                  <tr key={g.id} className="hover:bg-slate-50">
                    <td className="table-cell font-semibold text-slate-900 num">{g.id}</td>
                    <td className="table-cell">
                      <div className="font-medium text-slate-900">{g.borrower}</div>
                      <div className="text-xs text-slate-500 num">{g.loanRef}</div>
                    </td>
                    <td className="table-cell">
                      <div className="font-medium text-slate-800">{g.category}</div>
                      <div className="text-xs text-slate-500">{g.receivedChannel}</div>
                    </td>
                    <td className="table-cell text-slate-600">{new Date(g.receivedDate).toLocaleDateString('en-GB')}</td>
                    <td className="table-cell text-slate-600">{g.owner}</td>
                    <td className="table-cell">
                      <span className={`font-medium ${g.status === 'overdue' ? 'text-red-600' : 'text-slate-700'}`}>
                        {g.tat}
                      </span>
                    </td>
                    <td className="table-cell">
                      <StatusBadge label={g.status === 'new' ? 'New' : g.status === 'waiting_info' ? 'Waiting Info' : g.status === 'under_review' ? 'Under Review' : g.status.charAt(0).toUpperCase() + g.status.slice(1)} size="sm" />
                    </td>
                    <td className="table-cell text-slate-600">{new Date(g.lastUpdate).toLocaleDateString('en-GB')}</td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button 
                          onClick={() => setSelectedGrievance(g)}
                          className="text-blue-600 hover:text-blue-800 font-medium text-xs px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                        >
                          View
                        </button>
                        {!isAuditor && !isAdmin && g.status !== 'closed' && (
                          <div className="relative group">
                            <button className="text-slate-600 hover:text-slate-900 font-medium text-xs px-2 py-1 rounded hover:bg-slate-100 transition-colors flex items-center gap-1">
                              Actions <ChevronRight size={12} className="rotate-90" />
                            </button>
                            <div className="absolute right-0 mt-1 w-36 bg-white border border-slate-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 flex flex-col text-left overflow-hidden">
                              {currentUser.role === 'company_secretary' && <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Assign</button>}
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Add update</button>
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Record resolution</button>
                              {currentUser.role === 'company_secretary' && <button className="px-3 py-2 text-xs text-amber-700 hover:bg-amber-50 text-left">Escalate</button>}
                              {currentUser.role === 'company_secretary' && <button className="px-3 py-2 text-xs text-green-700 hover:bg-green-50 text-left">Close</button>}
                            </div>
                          </div>
                        )}
                        {g.status === 'closed' && canExport && (
                          <button className="text-slate-600 hover:text-slate-900 font-medium text-xs px-2 py-1 rounded hover:bg-slate-100 transition-colors">
                            Download
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 text-center">
          Showing {filteredGrievances.length} of {grievances.length} grievances in this view.
        </div>
      </div>

      {selectedGrievance && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setSelectedGrievance(null)} />
          <div className="w-[500px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col transform transition-transform duration-300">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Grievance Details</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">{selectedGrievance.id}</div>
              </div>
              <button 
                onClick={() => setSelectedGrievance(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <XIcon size={20} />
              </button>
            </div>
            
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-slate-500 mb-1">Borrower</div>
                  <div className="font-medium text-slate-900">{selectedGrievance.borrower}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Linked Loan</div>
                  <div className="font-medium text-slate-900">{selectedGrievance.loanRef}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Category</div>
                  <div className="font-medium text-slate-900">{selectedGrievance.category}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Received Mode</div>
                  <div className="font-medium text-slate-900">{selectedGrievance.receivedChannel}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Date Received</div>
                  <div className="font-medium text-slate-900">{new Date(selectedGrievance.receivedDate).toLocaleDateString('en-GB')}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Assigned Owner</div>
                  <div className="font-medium text-slate-900">{selectedGrievance.owner}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Target Resolution Date</div>
                  <div className="font-medium text-slate-900">{selectedGrievance.targetResolution ? new Date(selectedGrievance.targetResolution).toLocaleDateString('en-GB') : '-'}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">TAT Status</div>
                  <div className={`font-medium ${selectedGrievance.status === 'overdue' ? 'text-red-600' : 'text-slate-900'}`}>{selectedGrievance.tat}</div>
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500 mb-2">Complaint Description</div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm text-slate-800">
                  {selectedGrievance.description}
                </div>
              </div>

              {selectedGrievance.status === 'closed' && (
                <div>
                  <div className="text-sm text-slate-500 mb-2">Resolution Details</div>
                  <div className="bg-green-50 p-3 rounded-lg border border-green-200 text-sm text-slate-800 space-y-2">
                    <p><strong>Resolved On:</strong> {selectedGrievance.resolutionDate ? new Date(selectedGrievance.resolutionDate).toLocaleDateString('en-GB') : '-'}</p>
                    <p><strong>Summary:</strong> {selectedGrievance.resolutionSummary}</p>
                    <p><strong>Borrower Informed:</strong> {selectedGrievance.borrowerInformed ? 'Yes' : 'No'}</p>
                    <p><strong>Acknowledgement:</strong> {selectedGrievance.borrowerAck}</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-slate-100 bg-slate-50">
              <div className="text-xs text-slate-500 mb-3 space-y-1">
                <p>• Grievance records cannot be deleted.</p>
                <p>• Every status update or resolution creates an audit event.</p>
              </div>
              <div className="flex justify-end gap-2">
                <button 
                  onClick={() => setSelectedGrievance(null)}
                  className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GrievancesHub;
