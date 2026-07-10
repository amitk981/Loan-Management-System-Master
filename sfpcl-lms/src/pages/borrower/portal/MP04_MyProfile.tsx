import React, { useEffect, useState } from 'react';
import { AlertTriangle, Landmark, MapPin, Phone, Shield } from 'lucide-react';
import StatusBadge from '../../../components/ui/StatusBadge';
import Tabs from '../../../components/ui/Tabs';
import { AuthSessionError } from '../../../services/authSession';
import { fetchPortalProfile, type PortalProfile } from '../../../services/portalApi';

const MP04_MyProfile: React.FC = () => {
  const [profile, setProfile] = useState<PortalProfile | null>(null);
  const [message, setMessage] = useState('Loading your member profile...');

  useEffect(() => {
    let mounted = true;
    fetchPortalProfile()
      .then(data => {
        if (mounted) setProfile(data);
      })
      .catch((error: AuthSessionError) => {
        if (mounted) setMessage(error.message || 'Member profile could not be loaded.');
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (!profile) {
    return <ProfilePanel title="Member profile unavailable" message={message} />;
  }
  return <MP04ProfileView profile={profile} />;
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
