import React, { useState } from 'react';
import { FileSignature, Upload, Download, Landmark, Shield } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { PortalDocumentationAction } from '../../../../services/portalApi';
import { usePortalDocumentationActions } from './usePortalDocumentationActions';

const MP13_DocumentationActions: React.FC = () => {
  const { projection, loading, error, uploading, success, upload, download } = usePortalDocumentationActions();
  const [selectedAction, setSelectedAction] = useState<PortalDocumentationAction | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const actions = projection?.actions ?? [];
  const pendingCount = actions.filter(action => action.status === 'pending_borrower').length;
  const submittedCount = actions.filter(action => action.status === 'submitted').length;

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
      <div>
        <h2 className="text-xl font-bold text-slate-900">Documentation Actions</h2>
        <p className="text-sm text-slate-500 mt-1">Complete borrower-side signatures, uploads, and acknowledgements.</p>
      </div>

      {loading && <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">Loading documentation actions…</div>}
      {!loading && error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>}
      {!loading && !error && !projection && <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">No sanctioned application has documentation actions yet.</div>}
      {!loading && projection?.availability === 'blocked' && <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">{projection.unavailable_reason}</div>}
      {success && <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-700">{success}</div>}

      {!loading && projection && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {[
              ['Pending borrower actions', String(pendingCount)],
              ['Submitted for review', String(submittedCount)],
              ['Final approvals by SFPCL', 'Internal only'],
            ].map(([label, value]) => (
              <div key={label} className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                <FileSignature size={17} className="text-green-600" />
                Legal Document Checklist
              </h3>
            </div>
            <div className="divide-y divide-slate-50">
              {actions.map(item => (
                <div key={item.action_code} className="px-6 py-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center flex-shrink-0">
                      {item.section === 'Bank' ? <Landmark size={18} className="text-slate-500" /> : item.section === 'Security' ? <Shield size={18} className="text-slate-500" /> : <FileSignature size={18} className="text-slate-500" />}
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-semibold text-slate-900">{item.label}</p>
                        <StatusBadge
                          label={item.status === 'submitted' ? 'submitted_for_review' : item.status}
                          size="sm"
                        />
                      </div>
                      <p className="text-xs text-slate-500 mt-1">{item.instruction}</p>
                      {item.note && <p className="text-xs text-amber-700 mt-1">{item.note}</p>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.download && (
                      <button onClick={() => void download(item)} className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-200 text-slate-700 hover:bg-slate-50" aria-label={`Download ${item.label}`}>
                        <Download size={15} /> Download
                      </button>
                    )}
                    {(item.upload_allowed || item.reupload_allowed) && (
                      <button onClick={() => setSelectedAction(item)} className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-green-600 hover:bg-green-700 text-white" aria-label={`${item.reupload_allowed ? 'Re-upload' : 'Upload'} ${item.label}`}>
                        <Upload size={15} /> {item.reupload_allowed ? 'Re-upload' : 'Upload'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <p className="text-sm font-semibold text-amber-900">Internal verification required</p>
            <p className="text-xs text-amber-800 mt-1">You can submit or view borrower-side documents here. Only authorised SFPCL users can mark legal documents accepted or complete the final documentation approval.</p>
          </div>
        </>
      )}

      {selectedAction && (
        <div className="fixed inset-0 bg-slate-900/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Upload {selectedAction.label}</h3>
            <div className="space-y-4">
              <label className="block border-2 border-dashed border-slate-200 rounded-xl p-8 text-center cursor-pointer">
                <Upload size={24} className="mx-auto text-slate-300 mb-2" />
                <span className="block text-sm text-slate-500">Click to select file or drag and drop</span>
                <span className="block text-xs text-slate-400 mt-1">PDF, JPG, PNG · Max 5 MB</span>
                <input aria-label="Document file" type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={event => setFile(event.target.files?.[0] ?? null)} className="sr-only" />
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

export default MP13_DocumentationActions;
