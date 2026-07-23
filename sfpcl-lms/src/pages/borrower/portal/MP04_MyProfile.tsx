import React, { useEffect, useState } from 'react';
import { AlertTriangle, Landmark, MapPin, Phone, Shield } from 'lucide-react';
import AlertBanner from '../../../components/ui/AlertBanner';
import StatusBadge from '../../../components/ui/StatusBadge';
import Tabs from '../../../components/ui/Tabs';
import { AuthSessionError } from '../../../services/authSession';
import {
  fetchPortalKycCorrections,
  fetchPortalProfile,
  submitPortalKycCorrection,
  type PortalKycCorrection,
  type PortalProfile,
} from '../../../services/portalApi';

const MP04_MyProfile: React.FC = () => {
  const [profile, setProfile] = useState<PortalProfile | null>(null);
  const [corrections, setCorrections] = useState<PortalKycCorrection[]>([]);
  const [correctionsLoading, setCorrectionsLoading] = useState(true);
  const [correctionsError, setCorrectionsError] = useState<string | null>(null);
  const [message, setMessage] = useState('Loading your member profile...');

  useEffect(() => {
    let mounted = true;
    Promise.all([fetchPortalProfile(), fetchPortalKycCorrections()])
      .then(([profileData, correctionData]) => {
        if (mounted) {
          setProfile(profileData);
          setCorrections(correctionData.items);
          setCorrectionsLoading(false);
        }
      })
      .catch((error: AuthSessionError) => {
        if (mounted) {
          setMessage(error.message || 'Member profile could not be loaded.');
          setCorrectionsError(error.message || 'KYC correction requests could not be loaded.');
          setCorrectionsLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (!profile) {
    return <ProfilePanel title="Member profile unavailable" message={message} />;
  }
  return (
    <>
      <MP04ProfileView profile={profile} />
      <KycCorrectionPanel
        corrections={corrections}
        loading={correctionsLoading}
        error={correctionsError}
        onSubmit={async (field, value, reason, file) => {
          const correction = await submitPortalKycCorrection(field, value, reason, file);
          setCorrections(current => [correction, ...current]);
        }}
      />
    </>
  );
};

export const MP04ProfileView: React.FC<{ profile: PortalProfile }> = ({ profile }) => {
  const { member } = profile;
  const address = member.registered_address || {};
  const tabs = [
    { id: 'member', label: 'Member Details' },
    { id: 'contact', label: 'Contact Details' },
    { id: 'nominee', label: 'Nominee Details' },
    { id: 'shareholding', label: 'Shareholding' },
    { id: 'land', label: 'Land & Crop Details' },
    { id: 'bank', label: 'Bank Details' },
    { id: 'kyc', label: 'KYC Status' },
  ];

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div className="flex gap-4 items-start">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold text-2xl flex-shrink-0">
            {member.display_name.charAt(0)}
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">{member.display_name}</h2>
            <p className="text-sm text-slate-500">Folio Number: {member.folio_number}</p>
            <div className="flex gap-2 mt-2">
              <StatusBadge label={formatLabel(member.membership_status)} size="sm" />
              <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                {formatLabel(member.member_type)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col min-h-[500px]">
        <Tabs tabs={tabs}>
          <Section title="Member Information">
            <DetailGrid rows={[
              ['Full Name', member.legal_name || member.display_name],
              ['Member Type', formatLabel(member.member_type)],
              ['Folio Number', member.folio_number],
              ['Member Number', member.member_number || 'Not recorded'],
              ['Active Status', formatLabel(member.active_member_status?.status || member.membership_status)],
              ['Shares Held', String(member.share_summary?.number_of_shares ?? 0)],
              ['PAN', member.pan?.masked || 'Not recorded'],
              ['Aadhaar', member.aadhaar?.masked || 'Not recorded'],
              ['Primary Nominee', profile.nominees[0]?.nominee_name || 'Not recorded'],
              ['Primary Bank', profile.bank_accounts[0]?.account_number.masked || 'Not recorded'],
            ]} />
          </Section>

          <Section title="Contact & Address">
            <div className="space-y-6">
              <InfoBlock icon={<Phone className="text-slate-400 mt-0.5" size={20} />} label="Mobile Number" value={member.mobile_number || 'Not recorded'} note="Verified details are managed by SFPCL." />
              <InfoBlock icon={<MapPin className="text-slate-400 mt-0.5" size={20} />} label="Registered Address" value={[address.line1, address.line2, address.village_city, address.district, address.state, address.pincode].filter(Boolean).join(', ') || 'Not recorded'} note="Subject to verification for legal documents." />
            </div>
          </Section>

          <Section title="Registered Nominee">
            {profile.nominees.length ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {profile.nominees.map(nominee => (
                  <div key={nominee.nominee_name} className="bg-slate-50 border border-slate-200 rounded-xl p-5">
                    <DetailGrid rows={[
                      ['Nominee Name', nominee.nominee_name],
                      ['Relationship', nominee.relationship_to_borrower || 'Not recorded'],
                      ['PAN', nominee.pan.masked || 'Not recorded'],
                      ['Aadhaar', nominee.aadhaar.masked || 'Not recorded'],
                      ['KYC Status', formatLabel(nominee.kyc_status)],
                    ]} />
                  </div>
                ))}
              </div>
            ) : <Empty text="No nominee details are available yet." />}
          </Section>

          <TableSection headers={['Folio', 'Quantity', 'Available', 'Status']} rows={profile.shareholdings.map(row => [
            row.folio_number,
            String(row.number_of_shares),
            String(row.available_share_count),
            formatLabel(row.status),
          ])} />

          <Section title="Land & Crop Details">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3 text-sm text-amber-800 mb-4">
              <Shield className="flex-shrink-0" size={18} />
              <p>Land and crop details are read-only here. Updates happen through the loan application workflow.</p>
            </div>
            <Table headers={['Survey', 'Village', 'Area', 'Status']} rows={profile.land_holdings.map(row => [
              row.survey_number || 'Not recorded',
              row.village || 'Not recorded',
              `${row.area_acres} acres`,
              formatLabel(row.verification_status),
            ])} emptyText="No land records are available yet." />
            <div className="mt-4">
              <Table headers={['Season', 'Crop', 'Area', 'Status']} rows={profile.crop_plans.map(row => [
                row.season || 'Not recorded',
                row.crop_type,
                `${row.planned_area_acres} acres`,
                formatLabel(row.verification_status),
              ])} emptyText="No crop plans are available yet." />
            </div>
          </Section>

          <Section title="Bank Details">
            {profile.bank_accounts.length ? profile.bank_accounts.map(account => (
              <div key={`${account.ifsc}-${account.account_number.masked}`} className="bg-slate-50 border border-slate-200 rounded-xl p-5 mb-3">
                <div className="flex items-start gap-4">
                  <Landmark size={24} className="text-slate-400 mt-1" />
                  <DetailGrid rows={[
                    ['Account Holder Name', account.account_holder_name],
                    ['Bank Name', account.bank_name || 'Not recorded'],
                    ['Account Number', account.account_number.masked || 'Not recorded'],
                    ['IFSC Code', account.ifsc],
                    ['Branch', account.branch_name || 'Not recorded'],
                    ['Verification Status', formatLabel(account.verification_status)],
                  ]} />
                </div>
              </div>
            )) : <Empty text="No bank account details are available yet." />}
          </Section>

          <TableSection headers={['Document', 'Masked Value', 'Status', 'Re-KYC Due']} rows={[
            ['PAN Card', member.pan?.masked || 'Not recorded', formatLabel(member.kyc_status), profile.kyc_profile?.rekyc_due_date || member.active_member_status?.verified_at || 'Not recorded'],
            ['Aadhaar Card', member.aadhaar?.masked || 'Not recorded', formatLabel(member.kyc_status), profile.kyc_profile?.rekyc_due_date || 'Not recorded'],
          ]} />
        </Tabs>
      </div>
    </div>
  );
};

export const KycCorrectionPanel: React.FC<{
  corrections: PortalKycCorrection[];
  loading: boolean;
  error: string | null;
  onSubmit: (
    field: 'pan' | 'aadhaar' | 'mobile_number' | 'email' | 'registered_address',
    value: string,
    reason: string,
    file: File,
  ) => Promise<void> | void;
}> = ({ corrections, loading, error, onSubmit }) => {
  const [field, setField] = useState<'pan' | 'aadhaar' | 'mobile_number' | 'email' | 'registered_address'>('pan');
  const [value, setValue] = useState('');
  const [reason, setReason] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [validation, setValidation] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!value.trim() || !reason.trim() || !file) {
      setValidation('Choose the KYC field, enter its corrected value and reason, and attach evidence.');
      return;
    }
    setSubmitting(true);
    setValidation(null);
    try {
      await onSubmit(field, value, reason, file);
      setValue('');
      setReason('');
      setFile(null);
    } catch (submitError) {
      setValidation(
        submitError instanceof Error
          ? submitError.message
          : 'The correction request could not be submitted.',
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mt-4 bg-white rounded-xl border border-slate-200 p-6 space-y-6">
      <div>
        <h3 className="font-semibold text-slate-900 text-lg">Request a KYC correction</h3>
        <p className="text-sm text-slate-500 mt-1">
          Verified details are changed only after SFPCL reviews your self-attested evidence.
        </p>
      </div>
      {loading && <AlertBanner type="info" title="Loading KYC correction requests…" />}
      {!loading && error && <AlertBanner type="error" title={error} />}
      {validation && <AlertBanner type="error" title={validation} />}
      {!loading && !error && (
        <>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={submit}>
            <label className="text-sm text-slate-600">
              KYC field
              <select
                aria-label="KYC field"
                value={field}
                onChange={event => setField(event.target.value as typeof field)}
                className="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900"
              >
                <option value="pan">PAN</option>
                <option value="aadhaar">Aadhaar</option>
                <option value="mobile_number">Mobile number</option>
                <option value="email">Email</option>
                <option value="registered_address">Registered address</option>
              </select>
            </label>
            <label className="text-sm text-slate-600">
              Correct value
              <input
                aria-label="Correct value"
                value={value}
                onChange={event => setValue(event.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900"
              />
            </label>
            <label className="text-sm text-slate-600 md:col-span-2">
              Reason for correction
              <textarea
                aria-label="Reason for correction"
                value={reason}
                onChange={event => setReason(event.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-900"
                rows={3}
              />
            </label>
            <label className="text-sm text-slate-600 md:col-span-2">
              Self-attested evidence (PDF, JPG or PNG)
              <input
                aria-label="Self-attested evidence"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={event => setFile(event.target.files?.[0] ?? null)}
                className="mt-1.5 block w-full text-sm text-slate-500"
              />
            </label>
            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={submitting}
                className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
              >
                {submitting ? 'Submitting…' : 'Submit correction request'}
              </button>
            </div>
          </form>
          <div className="border-t border-slate-100 pt-5">
            <h4 className="font-medium text-slate-900 mb-3">Request status</h4>
            {corrections.length === 0 ? (
              <p className="text-sm text-slate-500">No KYC correction requests yet.</p>
            ) : (
              <div className="space-y-3">
                {corrections.map(correction => (
                  <div
                    key={correction.kyc_correction_request_id}
                    className="bg-slate-50 border border-slate-200 rounded-xl p-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-medium text-slate-900">
                          {Object.entries(correction.changes)
                            .map(([name, masked]) => `${formatCorrectionFieldLabel(name)} ${masked}`)
                            .join(', ')}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          Submitted {new Date(correction.submitted_at).toLocaleDateString('en-IN')}
                        </p>
                        {correction.review_started_at && (
                          <p className="text-xs text-slate-500 mt-1">
                            Review started {new Date(correction.review_started_at).toLocaleDateString('en-IN')}
                          </p>
                        )}
                        {correction.decided_at && (
                          <p className="text-xs text-slate-500 mt-1">
                            Decision recorded {new Date(correction.decided_at).toLocaleDateString('en-IN')}
                          </p>
                        )}
                      </div>
                      <StatusBadge label={formatLabel(correction.status)} size="sm" />
                    </div>
                    <p className="text-sm text-slate-600 mt-3">{correction.reason}</p>
                    {correction.rejection_reason && (
                      <p className="text-sm text-red-700 mt-2">{correction.rejection_reason}</p>
                    )}
                    <p className="text-xs text-slate-500 mt-2">
                      Evidence: {correction.evidence.map(item => item.file_name).join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="p-6">
    <div className="max-w-4xl">
      <h3 className="font-semibold text-slate-900 text-lg mb-4">{title}</h3>
      {children}
    </div>
  </div>
);

const DetailGrid: React.FC<{ rows: [string, string][] }> = ({ rows }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
    {rows.map(([label, value]) => (
      <div key={label}>
        <p className="text-sm text-slate-500 mb-1">{label}</p>
        <p className="font-medium text-slate-900">{value}</p>
      </div>
    ))}
  </div>
);

const InfoBlock: React.FC<{ icon: React.ReactNode; label: string; value: string; note: string }> = ({ icon, label, value, note }) => (
  <div className="flex items-start gap-4 p-4 rounded-xl border border-slate-100 bg-slate-50">
    {icon}
    <div>
      <p className="text-sm text-slate-500 mb-1">{label}</p>
      <p className="font-medium text-slate-900 leading-relaxed">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{note}</p>
    </div>
  </div>
);

const TableSection: React.FC<{ headers: string[]; rows: string[][] }> = ({ headers, rows }) => (
  <div className="p-0"><Table headers={headers} rows={rows} emptyText="No records are available yet." /></div>
);

const Table: React.FC<{ headers: string[]; rows: string[][]; emptyText: string }> = ({ headers, rows, emptyText }) => (
  <table className="w-full text-left">
    <thead>
      <tr className="bg-slate-50 border-b border-slate-200">
        {headers.map(header => <th key={header} className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase">{header}</th>)}
      </tr>
    </thead>
    <tbody className="divide-y divide-slate-100">
      {rows.length ? rows.map((row, index) => (
        <tr key={index} className="hover:bg-slate-50">
          {row.map((cell, cellIndex) => (
            <td key={cellIndex} className="px-6 py-4 text-sm text-slate-700">
              {cellIndex === row.length - 1 ? <StatusBadge label={cell} size="sm" /> : cell}
            </td>
          ))}
        </tr>
      )) : (
        <tr><td colSpan={headers.length} className="px-6 py-6 text-sm text-slate-500">{emptyText}</td></tr>
      )}
    </tbody>
  </table>
);

const Empty: React.FC<{ text: string }> = ({ text }) => <p className="text-sm text-slate-500">{text}</p>;

const formatCorrectionFieldLabel = (value: string) => {
  if (value === 'pan') return 'PAN';
  if (value === 'aadhaar') return 'Aadhaar';
  return formatLabel(value);
};

const ProfilePanel: React.FC<{ title: string; message: string }> = ({ title, message }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-6">
    <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
      <AlertTriangle size={16} className="text-amber-600" />
      {title}
    </h3>
    <p className="text-sm text-slate-500">{message}</p>
  </div>
);

const formatLabel = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());

export default MP04_MyProfile;
