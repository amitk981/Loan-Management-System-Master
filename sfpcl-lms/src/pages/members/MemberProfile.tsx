import React, { useState } from 'react';
import {
  ChevronLeft, User, Building2, AlertTriangle, CheckCircle2,
  FileText, Shield, CreditCard, Phone, Mail, MapPin, Eye,
  EyeOff, Calendar, Banknote, TrendingDown, Clock,
  RefreshCw, Download, MessageSquare, ArrowRight, Leaf,
  ClipboardList, BookOpen, History, UserCheck, Lock
} from 'lucide-react';
import Tabs from '../../components/ui/Tabs';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { members, loanApplications, loanAccounts } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');
const mask = (v: string) => v; // already masked in mockData

interface MemberProfileProps {
  memberId: string;
  onBack: () => void;
}

// ─── Produce Supply History ───────────────────────────────────────────────────
const supplyHistory = [
  { fy: 'FY 2024-25', crop: 'Grapes', qty: '12 MT', entity: 'SFPCL', countsToward: true, ref: 'INV-2025-042' },
  { fy: 'FY 2023-24', crop: 'Tomatoes', qty: '8 MT', entity: 'Sahyadri Farms PHC', countsToward: true, ref: 'INV-2024-018' },
  { fy: 'FY 2022-23', crop: 'Grapes', qty: '14 MT', entity: 'SFPCL', countsToward: true, ref: 'INV-2023-055' },
  { fy: 'FY 2021-22', crop: 'Sweetcorn', qty: '5 MT', entity: 'SFPCL', countsToward: true, ref: 'INV-2022-031' },
  { fy: 'FY 2020-21', crop: 'Grapes', qty: '10 MT', entity: 'SFPCL', countsToward: true, ref: 'INV-2021-077' },
];

// ─── Services Availed ─────────────────────────────────────────────────────────
const servicesAvailed = [
  { service: 'Crop Production Support', date: '2024-04-10', entity: 'SFPCL', type: 'Agronomy' },
  { service: 'Procurement (Grapes)', date: '2024-06-22', entity: 'SFPCL', type: 'Procurement' },
  { service: 'Agricultural Input Purchase', date: '2024-02-15', entity: 'Sahyadri Farms PHC', type: 'Input Purchase' },
];

// ─── Communications Log ───────────────────────────────────────────────────────
const communicationsLog = [
  { date: '2026-06-20', type: 'SMS', direction: 'Outbound', message: 'Overdue repayment reminder: ₹1,05,000 was due on 17 Jun 2026. Please pay immediately to avoid penalty.', sentBy: 'System' },
  { date: '2026-06-01', type: 'Email', direction: 'Outbound', message: 'Loan sanction approval notification with sanction letter attached.', sentBy: 'Priya Kulkarni' },
  { date: '2026-05-22', type: 'Call', direction: 'Inbound', message: 'Borrower called to query about interest calculation. Clarified principal-first allocation.', sentBy: 'Priya Kulkarni' },
  { date: '2026-04-10', type: 'Letter', direction: 'Outbound', message: 'Hard copy of Loan Agreement dispatched by registered post. Tracking: RM123456789IN.', sentBy: 'Aarti Desai' },
];

// ─── Land & Crop Evidence ─────────────────────────────────────────────────────
const landCropEvidence = [
  { doc: '7/12 Extract', land: '4.5 acres', crop: 'Grapes', season: 'Kharif 2024', uploaded: true, date: '2026-06-10' },
  { doc: 'Crop Plan', land: '4.5 acres', crop: 'Grapes', season: 'Kharif 2024', uploaded: true, date: '2026-06-10' },
];

// ─── Nominees ─────────────────────────────────────────────────────────────────
const nomineeData = [
  {
    name: 'Sudha Patil', age: 45, dob: '1980-03-15', gender: 'Female',
    relationship: 'Spouse', pan: 'BCDEF2345G', aadhaar: '****-****-8812',
    signature: 'obtained', panUploaded: true, aadhaarUploaded: true,
  },
];

// ─── Audit events for member ───────────────────────────────────────────────
const memberAuditEvents = [
  { ts: '2026-06-10 09:30', actor: 'Suresh Patil', role: 'Deputy Manager – Finance', action: 'KYC Verified', detail: 'PAN and Aadhaar documents verified' },
  { ts: '2026-06-01 11:00', actor: 'Priya Kulkarni', role: 'Credit Manager', action: 'Active Status Confirmed', detail: 'Active member status confirmed — 5 years supply on record' },
  { ts: '2025-11-20 14:22', actor: 'Aarti Desai', role: 'Company Secretary', action: 'SH-4 Received', detail: 'Physical share certificate SH-4 received in custody' },
  { ts: '2024-12-01 10:00', actor: 'System', role: 'System', action: 'Re-KYC Reminder Sent', detail: 'Annual KYC review reminder dispatched via SMS and email' },
];

const MemberProfile: React.FC<MemberProfileProps> = ({ memberId, onBack }) => {
  const member = members.find(m => m.id === memberId) || members[0];
  const memberApps = loanApplications.filter(a => a.memberId === member.id);
  const memberLoans = loanAccounts.filter(l => l.memberId === member.id);
  const [activeTab, setActiveTab] = useState(0);
  const [panRevealed, setPanRevealed] = useState(false);
  const [aadhaarRevealed, setAadhaarRevealed] = useState(false);
  const { can } = useRole();

  const shareholdingLimit = member.sharesHeld * 2000 * 0.30;
  const landBasedLimit = 90000; // 4.5 acres × ₹20,000 SOF
  const finalEligible = Math.min(shareholdingLimit, landBasedLimit);

  const currentExposure = memberLoans.reduce((sum, l) => sum + l.outstandingPrincipal, 0);
  const hasUnresolvedOverdue = memberLoans.some(l => l.status === 'overdue' || l.dpd > 0);
  
  const rekycDate = new Date('2026-03-31');
  const isRekycOverdue = rekycDate < new Date();

  const TABS = [
    { id: 'profile',   label: 'Overview' },
    { id: 'shareholding', label: 'Shareholding' },
    { id: 'supply',    label: 'Produce Supply' },
    { id: 'services',  label: 'Services Availed' },
    { id: 'land',      label: 'Land & Crop' },
    { id: 'kyc',       label: 'KYC' },
    { id: 'loans',     label: 'Loans', badge: memberApps.length + memberLoans.length > 0 ? memberApps.length + memberLoans.length : undefined },
    { id: 'nominee',   label: 'Nominee' },
    { id: 'comms',     label: 'Communications' },
    { id: 'exposure',  label: 'Exposure & Limits' },
    { id: 'audit',     label: 'Audit Trail' },
  ];

  const isFPC = member.memberType === 'fpc';

  return (
    <div className="p-6 space-y-4">
      {/* Back + Header */}
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700 flex-shrink-0">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${isFPC ? 'bg-blue-100' : 'bg-green-100'}`}>
              {isFPC ? <Building2 size={22} className="text-blue-700" /> : <User size={22} className="text-green-700" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-bold text-slate-900">{member.name}</h1>
                {isFPC && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">FPC</span>}
                <StatusBadge label={member.activeStatus} size="sm" />
                <StatusBadge 
                  label={member.kycStatus === 'verified' ? 'KYC verified' : member.kycStatus} 
                  family={member.kycStatus === 'verified' ? 'approved' : undefined} 
                  size="sm" 
                />
                {member.defaultStatus !== 'no_default' && <StatusBadge label={member.defaultStatus} size="sm" />}
              </div>
              <p className="text-sm text-slate-500 mt-0.5">
                Folio: <span className="font-semibold text-slate-900 num">{member.folioNumber}</span>
                {' · '}{isFPC ? 'Farmer Producer Company' : 'Individual Farmer'}
                {' · '}Member since {new Date(member.registeredOn).getFullYear()}
                {' · '}Shares: {member.sharesHeld.toLocaleString('en-IN')} ({member.shareMode})
              </p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <button 
                className="btn-secondary text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={hasUnresolvedOverdue || !can('create_application')}
                title={hasUnresolvedOverdue ? "New application blocked: existing loan overdue." : undefined}
              >
                Start Application
              </button>
              {can('manage_compliance') || can('edit_members') ? (
                <button className="btn-secondary text-xs">Update KYC</button>
              ) : (
                <button className="btn-secondary text-xs">View KYC</button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Compliance alerts */}
      {(member.kycStatus === 'rekyc_due' || member.kycStatus === 'expired') && (
        <AlertBanner type="warning" title="Re-KYC Required"
          message={`KYC status: ${member.kycStatus.replace(/_/g, ' ')}. No new loans can be processed until KYC is renewed.`} />
      )}
      {member.defaultStatus !== 'no_default' && (
        <AlertBanner type="error"
          title={member.defaultStatus === 'current_default' ? 'Current Default — Lending Blocked' : 'Past Default on Record'}
          message="Member has a default on record. Eligibility is subject to credit review before new loan can proceed." />
      )}
      {member.activeStatus !== 'active' && (
        <AlertBanner type="warning" title="Inactive Member"
          message="Member does not meet the active member criteria (4-year supply or 1-year relaxation). Loan application is blocked." />
      )}

      {/* Tabs */}
      <Tabs tabs={TABS} activeIndex={activeTab} onChange={setActiveTab}>

        {/* ── Tab 0: Overview ── */}
        <div className="card space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Member ID', value: member.id.toUpperCase() },
              { label: 'Folio Number', value: member.folioNumber },
              { label: 'Member Type', value: isFPC ? 'Farmer Producer Company' : 'Individual Farmer' },
              { label: 'Active Status', value: member.activeStatus.replace(/_/g, ' ') },
              { label: 'Active Status Reason', value: member.supplyYears >= 4 ? `${member.supplyYears} years supply (meets 4-year rule)` : `${member.supplyYears} year(s) supply — check 1-year relaxation` },
              { label: 'Registered On', value: new Date(member.registeredOn).toLocaleDateString('en-IN') },
              { label: 'Mobile', value: member.mobile },
              { label: 'Email', value: member.email },
              { label: 'Subsidiary Linkage', value: member.subsidiaryLinkage || '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
              </div>
            ))}
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-1 flex items-center gap-1"><MapPin size={12} /> Address</p>
            <p className="text-sm text-slate-800">{member.address}</p>
          </div>
          {/* Sensitive data — masked with reveal */}
          <div className="border-t border-slate-100 pt-4">
            <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide mb-3 flex items-center gap-1">
              <Lock size={12} /> Sensitive Identifiers — Masked
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                <div className="flex-1">
                  <p className="text-xs text-slate-500">PAN</p>
                  <p className="text-sm font-mono font-semibold text-slate-900">{panRevealed ? member.pan : '**********'}</p>
                </div>
                <button onClick={() => setPanRevealed(!panRevealed)} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                  {panRevealed ? <EyeOff size={12} /> : <Eye size={12} />}
                  {panRevealed ? 'Hide' : 'Reveal'}
                </button>
              </div>
              <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                <div className="flex-1">
                  <p className="text-xs text-slate-500">Aadhaar</p>
                  <p className="text-sm font-mono font-semibold text-slate-900">{aadhaarRevealed ? (can('edit_members') || can('manage_compliance') ? member.aadhaar : mask(member.aadhaar)) : '****-****-****'}</p>
                </div>
                <button onClick={() => setAadhaarRevealed(!aadhaarRevealed)} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                  {aadhaarRevealed ? <EyeOff size={12} /> : <Eye size={12} />}
                  {aadhaarRevealed ? 'Hide' : 'Reveal'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── Tab 1: Shareholding ── */}
        <div className="card space-y-4">
          <h3 className="font-semibold text-slate-800">Shareholding Details</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Total Shares Held', value: member.sharesHeld.toLocaleString('en-IN') },
              { label: 'Folio Number', value: member.folioNumber },
              { label: 'Shareholding Mode', value: member.shareMode === 'physical' ? 'Physical' : member.shareMode === 'demat' ? 'Demat' : 'Mixed' },
              { label: 'Physical Share Count', value: member.shareMode !== 'demat' ? member.sharesHeld.toLocaleString('en-IN') : '0' },
              { label: 'Demat Share Count', value: member.shareMode !== 'physical' ? member.sharesHeld.toLocaleString('en-IN') : '0' },
              { label: 'Latest Valuation / Share', value: '₹2,000' },
              { label: 'Board-Approved Loan %', value: '30%' },
              { label: 'Per-Share Loan Value', value: '₹600' },
              { label: 'Shareholding-based Limit', value: fmt(shareholdingLimit) },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
              </div>
            ))}
          </div>
          {member.shareMode !== 'physical' && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
              <p className="text-sm font-semibold text-blue-800 mb-2">Demat BO Account Details</p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-slate-500">DP ID: </span><span className="font-semibold">IN300239</span></div>
                <div><span className="text-slate-500">BO Account: </span><span className="font-semibold">10042875</span></div>
                <div><span className="text-slate-500">CDSL Pledge Status: </span><StatusBadge label={memberLoans.length > 0 ? 'pledged' : 'pending'} size="sm" /></div>
                <div><span className="text-slate-500">Future Share Pledge: </span><span className="font-semibold text-amber-700">Flagged</span></div>
              </div>
            </div>
          )}
          {member.shareMode !== 'demat' && (
            <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg p-4">
              <FileText size={18} className="text-slate-500 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-slate-800">Share Certificate Copy</p>
                <p className="text-xs text-slate-500">Physical share certificate — uploaded 2026-06-10</p>
              </div>
              <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
                <Download size={12} /> View
              </button>
            </div>
          )}
        </div>

        {/* ── Tab 2: Produce Supply History ── */}
        <div className="card overflow-hidden p-0">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="font-semibold text-slate-800">Produce Supply History</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Active member status requires: 4 consecutive years OR 1 year with relaxation.
              <span className={`ml-2 font-semibold ${member.supplyYears >= 4 ? 'text-green-700' : 'text-amber-700'}`}>
                {member.supplyYears >= 4 ? `✓ ${member.supplyYears} years — Active` : `⚠ ${member.supplyYears} year(s) — Review required`}
              </span>
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {['FY', 'Crop', 'Quantity', 'Supplied To', 'Reference', 'Counts Toward Active Status'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {supplyHistory.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-800">{row.fy}</td>
                    <td className="px-4 py-3 text-slate-700">{row.crop}</td>
                    <td className="px-4 py-3 text-slate-700">{row.qty}</td>
                    <td className="px-4 py-3 text-slate-700">{row.entity}</td>
                    <td className="px-4 py-3 text-slate-500 text-xs">{row.ref}</td>
                    <td className="px-4 py-3">
                      {row.countsToward
                        ? <span className="flex items-center gap-1 text-green-700"><CheckCircle2 size={14} /> Yes</span>
                        : <span className="flex items-center gap-1 text-slate-400"><AlertTriangle size={14} /> No</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── Tab 3: Services Availed ── */}
        <div className="card overflow-hidden p-0">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="font-semibold text-slate-800">Services Availed from SFPCL</h3>
          </div>
          <div className="divide-y divide-slate-50">
            {servicesAvailed.map((svc, i) => (
              <div key={i} className="px-6 py-4 flex items-center gap-4">
                <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center flex-shrink-0">
                  <Leaf size={14} className="text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-800">{svc.service}</p>
                  <p className="text-xs text-slate-400">{svc.entity} · {new Date(svc.date).toLocaleDateString('en-IN')}</p>
                </div>
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full">{svc.type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Tab 4: Land & Crop Evidence ── */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">Land Documents & Crop Plan</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
              {[
                { label: 'Total Land Area', value: '4.5 acres' },
                { label: 'Crop Type', value: 'Grapes (Kharif)' },
                { label: 'Season / Cycle', value: 'Kharif 2024' },
                { label: 'Scale of Finance / Acre', value: '₹20,000' },
                { label: 'Land-based Eligible Limit', value: fmt(landBasedLimit) },
                { label: 'Final eligible limit', value: fmt(finalEligible) },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
                </div>
              ))}
            </div>
          </div>
          {landCropEvidence.map((ev, i) => (
            <div key={i} className="card flex items-center gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${ev.uploaded ? 'bg-green-50' : 'bg-amber-50'}`}>
                <FileText size={18} className={ev.uploaded ? 'text-green-600' : 'text-amber-600'} />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-slate-800">{ev.doc}</p>
                <p className="text-xs text-slate-500">{ev.land} · {ev.crop} · {ev.season}</p>
                {ev.uploaded && <p className="text-xs text-slate-400">Uploaded: {new Date(ev.date).toLocaleDateString('en-IN')}</p>}
              </div>
              <StatusBadge label={ev.uploaded ? 'verified' : 'pending_upload'} size="sm" />
              {ev.uploaded && (
                <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
                  <Download size={12} /> View
                </button>
              )}
            </div>
          ))}
        </div>

        {/* ── Tab 5: KYC ── */}
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">KYC Status</h3>
            <StatusBadge 
              label={member.kycStatus === 'verified' ? 'KYC verified' : member.kycStatus} 
              family={member.kycStatus === 'verified' ? 'approved' : undefined} 
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { doc: 'PAN Card', status: 'verified', date: '2026-06-10', selfAttested: true },
              { doc: isFPC ? 'GST / CIN' : 'Aadhaar Card', status: 'verified', date: '2026-06-10', selfAttested: true },
              { doc: 'Photograph', status: 'verified', date: '2026-06-10', selfAttested: false },
              { doc: isFPC ? 'Board Resolution' : 'Address Proof', status: 'verified', date: '2026-06-10', selfAttested: true },
              { doc: 'Bank Passbook / Statement', status: 'verified', date: '2026-06-10', selfAttested: true },
              { doc: 'CKYC Reference', status: member.kycStatus === 'verified' ? 'complete' : 'pending', date: member.kycStatus === 'verified' ? '2026-06-10' : null, selfAttested: false },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${item.status === 'verified' || item.status === 'complete' ? 'bg-green-100' : 'bg-amber-100'}`}>
                  {item.status === 'verified' || item.status === 'complete'
                    ? <CheckCircle2 size={14} className="text-green-600" />
                    : <Clock size={14} className="text-amber-600" />}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-800">{item.doc}</p>
                  <p className="text-xs text-slate-400">
                    {item.date ? `Verified: ${new Date(item.date).toLocaleDateString('en-IN')}` : 'Pending'}
                    {item.selfAttested && ' · Self-attested'}
                  </p>
                </div>
                <StatusBadge label={item.status} size="sm" />
              </div>
            ))}
          </div>
          <div className="flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
            <RefreshCw size={16} className="text-amber-600 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-amber-800">{isRekycOverdue ? 'Re-KYC overdue' : 'Next Re-KYC due'}</p>
              <p className="text-xs text-amber-700">Annual KYC review required by 31 March 2026</p>
            </div>
            {(can('manage_compliance') || can('edit_members')) && (
              <button className="text-xs bg-amber-600 hover:bg-amber-700 text-white px-3 py-1.5 rounded-lg transition-colors">
                Initiate Re-KYC
              </button>
            )}
          </div>
        </div>

        {/* ── Tab 6: Loans ── */}
        <div className="space-y-4">
          {memberApps.length === 0 && memberLoans.length === 0 ? (
            <div className="card text-center py-8 text-slate-400 text-sm">No loan history.</div>
          ) : (
            <>
              {memberApps.length > 0 && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Applications ({memberApps.length})</h3>
                  <div className="space-y-2">
                    {memberApps.map(app => (
                      <div key={app.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-slate-900 num">{app.applicationNumber}</span>
                            {app.isException && <span className="text-xs bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded">Exception</span>}
                          </div>
                          <p className="text-xs text-slate-500 mt-0.5">
                            Requested: {fmt(app.requestedAmount)} · Eligible: {fmt(app.eligibleAmount ?? 0)} · Submitted: {new Date(app.submittedAt).toLocaleDateString('en-IN')}
                          </p>
                        </div>
                        <StatusBadge label={app.status} size="sm" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {memberLoans.length > 0 && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Loan Accounts ({memberLoans.length})</h3>
                  <div className="space-y-2">
                    {memberLoans.map(loan => (
                      <div key={loan.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                        <div className="flex-1">
                          <span className="font-semibold text-slate-900 num">{loan.accountNumber}</span>
                          <p className="text-xs text-slate-500 mt-0.5">
                            Disbursed: {fmt(loan.disbursedAmount)} · Outstanding: {fmt(loan.outstandingPrincipal)} · DPD: {loan.dpd}
                          </p>
                        </div>
                        <StatusBadge label={loan.status} size="sm" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* ── Tab 7: Nominee ── */}
        <div className="space-y-4">
          {nomineeData.map((nom, i) => (
            <div key={i} className="card space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-800">Nominee {i + 1}</h3>
                <StatusBadge label={nom.signature} size="sm" />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {[
                  { label: 'Full Name', value: nom.name },
                  { label: 'Age', value: `${nom.age} years` },
                  { label: 'Date of Birth', value: new Date(nom.dob).toLocaleDateString('en-IN') },
                  { label: 'Gender', value: nom.gender },
                  { label: 'Relationship', value: nom.relationship },
                  { label: 'PAN', value: can('manage_compliance') ? nom.pan : '**********' },
                  { label: 'Aadhaar', value: nom.aadhaar },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                    <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
                  </div>
                ))}
              </div>
              {/* Minor guard */}
              {nom.age < 18 && (
                <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700">
                  <AlertTriangle size={16} className="flex-shrink-0" />
                  <p className="text-sm font-semibold">Nominee is a minor — application blocked until nominee is replaced with an adult.</p>
                </div>
              )}
              <div className="flex items-center gap-3">
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${nom.panUploaded ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
                  {nom.panUploaded ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
                  PAN Copy {nom.panUploaded ? 'Uploaded' : 'Missing'}
                </div>
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${nom.aadhaarUploaded ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
                  {nom.aadhaarUploaded ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
                  Aadhaar Copy {nom.aadhaarUploaded ? 'Uploaded' : 'Missing'}
                </div>
              </div>
            </div>
          ))}
          {can('edit_members') && (
            <div className="card border-dashed text-center py-6">
              <button className="text-sm text-green-600 font-medium hover:underline">+ Add / Update Nominee</button>
            </div>
          )}
        </div>

        {/* ── Tab 8: Communications ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Communications Log</h3>
            {can('edit_members') && (
              <button className="flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition-colors">
                <MessageSquare size={12} /> Add Entry
              </button>
            )}
          </div>
          <div className="divide-y divide-slate-50">
            {communicationsLog.map((c, i) => (
              <div key={i} className="flex gap-4 px-6 py-4 hover:bg-slate-50">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${c.type === 'SMS' ? 'bg-blue-50' : c.type === 'Email' ? 'bg-green-50' : c.type === 'Call' ? 'bg-amber-50' : 'bg-slate-100'}`}>
                  <MessageSquare size={14} className="text-slate-500" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">{c.type}</span>
                    <span className="text-xs text-slate-400">{c.direction}</span>
                  </div>
                  <p className="text-sm text-slate-700 mt-1">{c.message}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{c.sentBy} · {new Date(c.date).toLocaleDateString('en-IN')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Tab 9: Exposure & Limits ── */}
        <div className="card space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Shareholding-based Limit</p>
              <p className="text-2xl font-bold text-slate-900 num mt-1">{fmt(shareholdingLimit)}</p>
              <p className="text-xs text-slate-400 mt-1">{member.sharesHeld} shares × ₹2,000 × 30%</p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Land-based Limit</p>
              <p className="text-2xl font-bold text-slate-900 num mt-1">{fmt(landBasedLimit)}</p>
              <p className="text-xs text-slate-400 mt-1">4.5 acres × ₹20,000 Scale of Finance</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-green-700 uppercase tracking-wide">Final eligible limit</p>
              <p className="text-2xl font-bold text-green-900 num mt-1">{fmt(finalEligible)}</p>
              <p className="text-xs text-green-600 mt-1">Lower of shareholding and land-based limits</p>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className={`border rounded-lg p-4 ${currentExposure > shareholdingLimit ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
              <p className={`text-xs font-semibold uppercase tracking-wide ${currentExposure > shareholdingLimit ? 'text-red-700' : 'text-green-700'}`}>
                Current Exposure (Outstanding)
              </p>
              <p className={`text-2xl font-bold num mt-1 ${currentExposure > shareholdingLimit ? 'text-red-900' : 'text-green-900'}`}>
                {fmt(currentExposure)}
              </p>
              <p className={`text-xs mt-1 ${currentExposure > shareholdingLimit ? 'text-red-600' : 'text-green-600'}`}>
                {currentExposure === 0 ? 'No current exposure' : `${((currentExposure / shareholdingLimit) * 100).toFixed(1)}% of shareholding limit used`}
              </p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Available Headroom</p>
              <p className={`text-2xl font-bold num mt-1 ${Math.max(0, finalEligible - currentExposure) === 0 ? 'text-red-900' : 'text-slate-900'}`}>
                {fmt(Math.max(0, finalEligible - currentExposure))}
              </p>
              <p className="text-xs text-slate-400 mt-1">Available for new lending</p>
            </div>
          </div>
          {currentExposure > finalEligible && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700">
              <AlertTriangle size={16} className="flex-shrink-0" />
              <p className="text-sm font-semibold">New lending blocked: exposure exceeds eligible limit and loan is overdue.</p>
            </div>
          )}
        </div>

        {/* ── Tab 10: Audit Trail ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Member Audit Trail</h3>
            <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="divide-y divide-slate-50">
            {memberAuditEvents.map((ev, i) => (
              <div key={i} className="flex gap-4 px-6 py-4 hover:bg-slate-50">
                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <History size={14} className="text-slate-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold text-slate-900">{ev.action}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{ev.detail}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {ev.actor} · {ev.role} · {ev.ts}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Tabs>
    </div>
  );
};

export default MemberProfile;
