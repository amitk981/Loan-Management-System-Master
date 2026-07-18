import React, { useEffect, useState } from 'react';
import { AlertCircle, Banknote, CheckCircle2, Clock, Download, Landmark } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import {
  downloadPortalDisbursementAdvice,
  fetchPortalApplications,
  fetchPortalDisbursementStatus,
  PortalDisbursementStatus,
} from '../../../../services/portalApi';

const FINANCE_APPLICATION_STATUSES = new Set([
  'approved_by_sanction_committee',
  'documentation_pending',
  'disbursement_processing',
  'disbursed',
]);

const MP14_DisbursementStatus: React.FC = () => {
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [projection, setProjection] = useState<PortalDisbursementStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let current = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const applications = await fetchPortalApplications();
        const eligible = applications.items.find(item => FINANCE_APPLICATION_STATUSES.has(item.application_status));
        if (!current) return;
        if (!eligible) {
          setApplicationId(null);
          setProjection(null);
          return;
        }
        setApplicationId(eligible.loan_application_id);
        const status = await fetchPortalDisbursementStatus(eligible.loan_application_id);
        if (current) setProjection(status);
      } catch (requestError) {
        if (current) setError(disbursementErrorMessage(requestError));
      } finally {
        if (current) setLoading(false);
      }
    };
    void load();
    return () => { current = false; };
  }, []);

  const download = async () => {
    if (!applicationId || !projection?.advice_available) return;
    setDownloading(true);
    setError(null);
    try {
      await downloadPortalDisbursementAdvice(applicationId);
    } catch (requestError) {
      setError(disbursementErrorMessage(requestError, 'Disbursement advice could not be downloaded.'));
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Disbursement Status</h2>
        <p className="text-sm text-slate-500 mt-1">Track SAP setup, bank authorisation, and final payment advice.</p>
      </div>

      {loading && <PortalMessage message="Loading disbursement status…" />}
      {!loading && error && <PortalMessage message={error} error />}
      {!loading && !error && !projection && (
        <PortalMessage message="No approved application is in finance processing yet." />
      )}
      {!loading && projection && <DisbursementStatusView projection={projection} downloading={downloading} onDownload={() => { void download(); }} />}
    </div>
  );
};

export const DisbursementStatusView: React.FC<{
  projection: PortalDisbursementStatus;
  downloading: boolean;
  onDownload: () => void;
}> = ({ projection, downloading, onDownload }) => {
  const disbursed = projection.status_code === 'disbursed';
  const factRows = [
    ['Sanctioned Amount', formatMoney(projection.sanctioned_amount)],
    ['Bank Reference / UTR', maskLast4(projection.bank_reference_last4)],
    ['Credited Account', maskLast4(projection.destination_account_last4)],
  ];
  return (
    <>
      <div className="bg-white rounded-xl border border-green-200 overflow-hidden">
        <div className="bg-green-50 px-6 py-5 border-b border-green-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-11 h-11 rounded-xl bg-green-100 flex items-center justify-center flex-shrink-0">
              <Banknote size={22} className="text-green-700" />
            </div>
            <div>
              <h3 className="font-bold text-green-950">{projection.status_label}</h3>
              <p className="text-sm text-green-700 mt-1">
                {disbursed && projection.disbursement_amount && projection.disbursed_at
                  ? `${formatMoney(projection.disbursement_amount)} transferred on ${formatDate(projection.disbursed_at)}.`
                  : 'Your application remains with SFPCL for finance processing.'}
              </p>
            </div>
          </div>
          <StatusBadge label={disbursed ? 'completed' : projection.status_code} size="sm" />
        </div>
        <div className="p-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {factRows.map(([label, value]) => (
            <div key={label} className="bg-slate-50 rounded-lg p-3">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-100 p-5">
        <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <Clock size={16} className="text-green-600" />
          Processing Timeline
        </h3>
        <div className="space-y-3">
          {projection.timeline.map(item => (
            <div key={item.code} className="flex items-center gap-3">
              {item.status === 'complete'
                ? <CheckCircle2 size={17} className="text-green-600" />
                : item.status === 'blocked'
                  ? <AlertCircle size={17} className="text-amber-500" />
                  : <Clock size={17} className="text-slate-300" />}
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-800">{item.label}</p>
                <p className="text-xs text-slate-400">
                  {item.completed_at ? formatDate(item.completed_at) : item.status === 'blocked' ? 'SFPCL review needed' : 'Pending'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-100 p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-start gap-3">
          <Landmark size={18} className="text-slate-500 mt-0.5" />
          <div>
            <p className="font-semibold text-slate-900">Disbursement Advice</p>
            <p className="text-sm text-slate-500 mt-0.5">Official borrower copy with amount, date, masked bank reference, and credited account.</p>
          </div>
        </div>
        <button
          type="button"
          disabled={!projection.advice_available || downloading}
          onClick={onDownload}
          className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-200 disabled:text-slate-500 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
        >
          <Download size={16} />
          {downloading ? 'Preparing Advice…' : projection.advice_available ? 'Download Advice' : 'Advice unavailable'}
        </button>
      </div>
    </>
  );
};

const PortalMessage: React.FC<{ message: string; error?: boolean }> = ({ message, error = false }) => (
  <div className={`rounded-xl border p-5 text-sm ${error ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white border-slate-100 text-slate-500'}`}>
    {message}
  </div>
);

const formatMoney = (value: string | null) => value
  ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(value))
  : 'Not available';

const maskLast4 = (value: string | null) => value ? `••••${value}` : 'Not available';

const formatDate = (value: string) => new Intl.DateTimeFormat('en-IN', {
  day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC',
}).format(new Date(value));

const disbursementErrorMessage = (error: unknown, fallback = 'Disbursement status could not be loaded. Please try again.') => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) return 'Your member portal session has expired. Please sign in again.';
    if (error.status === 403) return 'You are not authorised to view this disbursement status.';
    return error.message || fallback;
  }
  return fallback;
};

export default MP14_DisbursementStatus;
