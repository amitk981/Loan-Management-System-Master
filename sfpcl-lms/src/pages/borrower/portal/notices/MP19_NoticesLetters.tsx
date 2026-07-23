import React, { useEffect, useState } from 'react';
import { Download, FileText, MailOpen } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import {
  downloadPortalNotice,
  fetchPortalNotices,
  type PortalNotice,
} from '../../../../services/portalApi';

export const MP19NoticesView: React.FC<{
  notices: PortalNotice[];
  loading: boolean;
  error: string | null;
  downloadingId: string | null;
  onDownload: (notice: PortalNotice) => void;
}> = ({ notices, loading, error, downloadingId, onDownload }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-xl font-bold text-slate-900">Notices & Letters</h2>
      <p className="text-sm text-slate-500 mt-1">View official borrower communications and downloadable letters.</p>
    </div>
    {error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>}
    <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center gap-2">
        <MailOpen size={17} className="text-green-600" />
        <h3 className="font-semibold text-slate-900">Communication History</h3>
      </div>
      {loading ? (
        <div className="p-8 text-center text-sm text-slate-500">Loading notices and letters…</div>
      ) : notices.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-500">No borrower notices or letters are available yet.</div>
      ) : (
        <div className="divide-y divide-slate-50">
          {notices.map(notice => (
            <div key={notice.notice_id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
              <div className="flex items-start gap-3 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center flex-shrink-0">
                  <FileText size={18} className="text-slate-500" />
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold text-slate-900">{notice.notice_type.replace(/_/g, ' ')}</p>
                    <StatusBadge label={notice.status} size="sm" />
                  </div>
                  <p className="text-sm text-slate-600 mt-1">{notice.title}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {notice.issued_at ? new Date(notice.issued_at).toLocaleDateString() : 'Date pending'}
                    {notice.related_reference ? ` · ${notice.related_reference}` : ''}
                  </p>
                </div>
              </div>
              {notice.download_url && (
                <button
                  className="flex items-center justify-center gap-2 border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors disabled:opacity-40"
                  disabled={downloadingId === notice.notice_id}
                  onClick={() => onDownload(notice)}
                >
                  <Download size={15} />
                  {downloadingId === notice.notice_id ? 'Preparing…' : 'Download'}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);

const MP19_NoticesLetters: React.FC = () => {
  const [notices, setNotices] = useState<PortalNotice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetchPortalNotices()
      .then(rows => { if (active) setNotices(rows); })
      .catch(reason => {
        if (active) setError(reason instanceof AuthSessionError && reason.status === 403
          ? 'You are not authorised to view borrower notices.'
          : 'Notices and letters could not be loaded. Please try again.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const download = async (notice: PortalNotice) => {
    if (!notice.download_url) return;
    setDownloadingId(notice.notice_id);
    setError(null);
    try {
      await downloadPortalNotice(notice.download_url);
    } catch {
      setError('The issued document could not be downloaded. Please try again.');
    } finally {
      setDownloadingId(null);
    }
  };

  return <MP19NoticesView notices={notices} loading={loading} error={error} downloadingId={downloadingId} onDownload={download} />;
};

export default MP19_NoticesLetters;
