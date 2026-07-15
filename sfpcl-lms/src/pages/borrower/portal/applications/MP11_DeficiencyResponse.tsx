import React, { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Download, FileWarning, Send, Upload } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import { downloadPortalDeficiencyResponse, downloadPortalDeficiencyNote, fetchPortalApplicationDeficiencies, fetchPortalDocumentContent, openPortalDocumentBlob, PortalDeficiencyItem, PortalDeficiencyProjection, resubmitPortalApplicationDeficiencies, savePortalDeficiencyResponseDraft, uploadPortalDeficiencyResponse } from '../../../../services/portalApi';

interface MP11DeficiencyResponseProps { applicationId: string; onResubmitted: () => void; }

const MP11_DeficiencyResponse: React.FC<MP11DeficiencyResponseProps> = ({ applicationId, onResubmitted }) => {
  const [projection, setProjection] = useState<PortalDeficiencyProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [resubmitting, setResubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [remarks, setRemarks] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    const result = await fetchPortalApplicationDeficiencies(applicationId);
    setProjection(result);
    setRemarks(draftRemarks(result));
  }, [applicationId]);

  useEffect(() => {
    let current = true;
    setLoading(true);
    setError(null);
    fetchPortalApplicationDeficiencies(applicationId)
      .then(result => {
        if (current) {
          setProjection(result);
          setRemarks(draftRemarks(result));
        }
      })
      .catch(requestError => { if (current) setError(deficiencyErrorMessage(requestError)); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [applicationId]);

  const upload = async (item: PortalDeficiencyItem) => {
    const file = files[item.deficiency_id];
    if (!file) return;
    setBusyId(item.deficiency_id);
    setError(null);
    setSuccess(null);
    try {
      await uploadPortalDeficiencyResponse(applicationId, item, file, remarks[item.deficiency_id] ?? '');
      await load();
      setSuccess('Response uploaded for SFPCL review.');
      setFiles(current => ({ ...current, [item.deficiency_id]: null }));
    } catch (requestError) {
      setError(deficiencyErrorMessage(requestError));
    } finally {
      setBusyId(null);
    }
  };

  const resubmit = async () => {
    setResubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      await resubmitPortalApplicationDeficiencies(applicationId);
      setSuccess('Corrections resubmitted for completeness review.');
      onResubmitted();
    } catch (requestError) {
      setError(deficiencyErrorMessage(requestError));
    } finally {
      setResubmitting(false);
    }
  };

  const saveDraft = async (item: PortalDeficiencyItem) => {
    setBusyId(item.deficiency_id);
    setError(null);
    setSuccess(null);
    try {
      await savePortalDeficiencyResponseDraft(applicationId, item.deficiency_id, remarks[item.deficiency_id] ?? '');
      setSuccess('Response draft saved.');
    } catch (requestError) {
      setError(deficiencyErrorMessage(requestError));
    } finally {
      setBusyId(null);
    }
  };

  const downloadNote = async () => {
    setError(null);
    try {
      const content = await downloadPortalDeficiencyNote(applicationId);
      openPortalDocumentBlob(content);
    } catch (requestError) {
      setError(deficiencyErrorMessage(requestError));
    }
  };

  const download = async (item: PortalDeficiencyItem) => {
    if (!item.response) return;
    setError(null);
    try {
      const descriptor = await downloadPortalDeficiencyResponse(item.response.document.action_url);
      const content = await fetchPortalDocumentContent(descriptor.download_url);
      openPortalDocumentBlob(content);
    } catch (requestError) {
      setError(deficiencyErrorMessage(requestError));
    }
  };

  if (loading) return <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">Loading deficiency response…</div>;

  if (error && !projection) return <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800"><AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />{error}</div>;

  const items = projection?.items ?? [];
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
        <div className="px-5 py-4 bg-slate-50 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-slate-900 flex items-center gap-2"><FileWarning size={17} className="text-amber-600" /> Deficiency Response</h3>
            <p className="text-xs text-slate-500 mt-1">SFPCL requested {items.length} correction{items.length === 1 ? '' : 's'} for {projection?.application_reference_number ?? 'this application'}.</p>
          </div>
          <button onClick={() => void downloadNote()} className="flex items-center gap-2 text-sm font-medium text-green-700" aria-label="Download deficiency note">
            <Download size={15} />Download deficiency note
          </button>
        </div>
        {items.length === 0 ? (
          <div className="p-5 text-sm text-slate-500">No open deficiencies require a response.</div>
        ) : (
          <div className="divide-y divide-slate-100">
            {items.map(item => (
              <div key={item.deficiency_id} className="p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-medium text-slate-500">Deficiency reason</p>
                    <p className="text-sm font-semibold text-slate-900 mt-1">{item.description}</p>
                    <p className="text-xs font-medium text-slate-500 mt-3">Requested correction</p>
                    <p className="text-sm text-slate-700 mt-1">{item.item_code.replace(/_/g, ' ')}</p>
                  </div>
                  <StatusBadge label={item.response ? 'responded' : 'action needed'} size="sm" />
                </div>
                {item.response && (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-lg border border-green-100 bg-green-50 p-3 text-sm text-green-800">
                    <span className="flex items-center gap-2"><CheckCircle2 size={16} />{item.response.document.file_name}</span>
                    <button onClick={() => void download(item)} className="flex items-center gap-2 text-sm font-medium text-green-700" aria-label={`Download ${item.response.document.file_name}`}><Download size={15} />Download</button>
                  </div>
                )}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <label className="block text-sm font-medium text-slate-700">Replacement document
                    <input aria-label="Replacement document" type="file" accept={item.upload_contract.allowed_extensions.map(extension => `.${extension}`).join(',')} onChange={event => setFiles(current => ({ ...current, [item.deficiency_id]: event.target.files?.[0] ?? null }))} className="mt-1.5 block w-full text-sm text-slate-500" />
                  </label>
                  <label className="block text-sm font-medium text-slate-700">Borrower response remark
                    <textarea aria-label="Borrower response remark" value={remarks[item.deficiency_id] ?? ''} onChange={event => setRemarks(current => ({ ...current, [item.deficiency_id]: event.target.value }))} maxLength={4000} className="mt-1.5 w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                  </label>
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <button onClick={() => void saveDraft(item)} disabled={busyId !== null || resubmitting} className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border border-slate-200 text-slate-700 disabled:opacity-50 transition-colors" aria-label="Save response draft">
                    {busyId === item.deficiency_id ? 'Saving…' : 'Save response draft'}
                  </button>
                  <button onClick={() => void upload(item)} disabled={!files[item.deficiency_id] || busyId !== null || resubmitting} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white transition-colors" aria-label="Upload response">
                    <Upload size={15} />{busyId === item.deficiency_id ? 'Uploading…' : item.response ? 'Re-upload response' : 'Upload response'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {error && <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800"><AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />{error}</div>}
      {success && <div className="flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800"><CheckCircle2 size={16} className="mt-0.5 flex-shrink-0" />{success}</div>}
      {items.length > 0 && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white rounded-xl border border-slate-100 p-4">
          <p className="text-sm text-slate-500">All deficiency items need a current response document.</p>
          <button onClick={() => void resubmit()} disabled={!projection?.resubmission_allowed || busyId !== null || resubmitting} className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white transition-colors">
            <Send size={15} />{resubmitting ? 'Resubmitting…' : 'Resubmit corrections'}
          </button>
        </div>
      )}
    </div>
  );
};

const draftRemarks = (projection: PortalDeficiencyProjection) => Object.fromEntries(projection.items.map(item => [item.deficiency_id, item.draft?.response_remark ?? '']));

const deficiencyErrorMessage = (error: unknown) => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) return 'Your member portal session has expired. Please sign in again.';
    if (error.status === 403) return 'You are not authorised to respond to these deficiencies.';
    const firstFieldError = error.fieldErrors && Object.values(error.fieldErrors)[0];
    return firstFieldError || error.message || 'Deficiency response failed.';
  }
  return 'Deficiency response could not be loaded. Please try again.';
};

export default MP11_DeficiencyResponse;
