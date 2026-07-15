import React, { useState } from 'react';
import { FileText, Download, Upload, Info } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { PortalDocumentationAction } from '../../../../services/portalApi';
import { usePortalDocumentationActions } from './usePortalDocumentationActions';

const MP07_DocumentChecklist: React.FC = () => {
  const { projection, loading, error, uploading, success, upload, download } = usePortalDocumentationActions();
  const [selectedAction, setSelectedAction] = useState<PortalDocumentationAction | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const actions = projection?.actions ?? [];
  const firstUpload = actions.find(action => action.upload_allowed || action.reupload_allowed);

  const closeUpload = () => {
    if (uploading) return;
    setSelectedAction(null);
    setFile(null);
    setNotes('');
  };

  const submitUpload = async () => {
    if (!selectedAction || !file) return;
    if (await upload(selectedAction, file, notes)) closeUpload();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">My Documents</h2>
          <p className="text-sm text-slate-500 mt-1">Access your post-sanction documentation requirements and borrower-safe files.</p>
        </div>
        {firstUpload && (
          <button onClick={() => setSelectedAction(firstUpload)} className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm">
            <Upload size={16} /> Upload Document
          </button>
        )}
      </div>

      {loading && <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">Loading documentation actions…</div>}
      {!loading && error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>}
      {!loading && !error && !projection && <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">No sanctioned application has documentation actions yet.</div>}
      {!loading && projection?.availability === 'blocked' && <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">{projection.unavailable_reason}</div>}
      {success && <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-700">{success}</div>}

      {!loading && projection && (
        <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Document Checklist</h3>
            <div className="flex items-center gap-1.5 text-xs text-slate-500"><Info size={14} className="text-slate-400" /><span>Uploads are reviewed internally</span></div>
          </div>
          <div className="divide-y divide-slate-50">
            {actions.length === 0 && <div className="px-6 py-6 text-sm text-slate-500">No documentation requirements are available.</div>}
            {actions.map(action => {
              const positive = action.status === 'complete' || action.status === 'submitted';
              const blocked = action.status === 'blocked';
              return (
                <div key={action.action_code} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-start sm:items-center gap-3 min-w-0">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${positive ? 'bg-green-50' : blocked ? 'bg-red-50' : 'bg-amber-50'}`}>
                      <FileText size={20} className={positive ? 'text-green-600' : blocked ? 'text-red-600' : 'text-amber-600'} />
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <div className="text-sm font-semibold text-slate-800">{action.label}</div>
                        <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 bg-slate-100 rounded px-2 py-0.5">{action.section}</span>
                      </div>
                      <div className="text-xs text-slate-500">{action.updated_date ? `Updated on ${action.updated_date}` : 'Not yet available'} • {action.instruction}</div>
                      {action.note && <div className="text-xs text-amber-700 mt-1">{action.note}</div>}
                    </div>
                  </div>
                  <div className="flex items-center sm:justify-end gap-3 w-full sm:w-auto">
                    {action.download && <button onClick={() => void download(action)} className="flex items-center justify-center flex-1 sm:flex-none gap-1.5 text-sm bg-white border border-slate-200 text-slate-700 font-medium px-4 py-2 rounded-lg hover:bg-slate-50 transition-colors" aria-label={`Download ${action.label}`}><Download size={16} className="text-slate-400" />Download</button>}
                    {(action.upload_allowed || action.reupload_allowed) && <button onClick={() => setSelectedAction(action)} className="flex items-center justify-center flex-1 sm:flex-none gap-1.5 text-sm bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-lg transition-colors" aria-label={`${action.reupload_allowed ? 'Re-upload' : 'Upload'} ${action.label}`}><Upload size={16} />{action.reupload_allowed ? 'Re-upload' : 'Upload'}</button>}
                    {(action.status === 'complete' || (!action.download && !action.upload_allowed && !action.reupload_allowed)) && <div className="flex-1 sm:flex-none flex justify-center sm:justify-end"><StatusBadge label={action.status} size="sm" /></div>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {selectedAction && (
        <div className="fixed inset-0 bg-slate-900/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Upload {selectedAction.label}</h3>
            <div className="space-y-4">
              <label className="block text-sm font-medium text-slate-700">Document file
                <input aria-label="Document file" type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={event => setFile(event.target.files?.[0] ?? null)} className="mt-1.5 block w-full text-sm text-slate-500" />
              </label>
              <label className="block text-sm font-medium text-slate-700">Notes (optional)
                <textarea aria-label="Notes (optional)" value={notes} onChange={event => setNotes(event.target.value)} maxLength={4000} className="mt-1.5 w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
              </label>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={closeUpload} disabled={uploading} className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">Cancel</button>
              <button onClick={() => void submitUpload()} disabled={!file || uploading} className="flex-1 px-4 py-2.5 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors shadow-sm">{uploading ? 'Uploading…' : 'Upload'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MP07_DocumentChecklist;
