import React, { useState } from 'react';
import { HelpCircle, Bell, Search, Upload, Download, FileText, CheckCircle2, AlertTriangle, FileSignature, Landmark, CreditCard, Clock, Calendar, Check, Leaf, MapPin, IndianRupee, Printer, ArrowLeft, MoreVertical, X, Signature, Building, Briefcase, FileCheck, Phone, Shield, Eye, ShieldCheck, FileKey, UserCheck, Smartphone, Lock, Activity, BadgePercent, ArrowRight, MessageSquare, Plus, Edit, CornerDownRight, Mail, AlertCircle, ChevronDown, ListFilter, Trash2, ArrowUpRight, ArrowDownRight, User } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { Role } from '../../types';
import MP03_Dashboard from './portal/MP03_Dashboard';
import MP04_MyProfile from './portal/MP04_MyProfile';
import MP05_NewApplication from './portal/applications/MP05_NewApplication';
import MP09_MyApplications from './portal/applications/MP09_MyApplications';
import MP10_ApplicationStatus from './portal/applications/MP10_ApplicationStatus';
import MP12_SanctionOutcome from './portal/applications/MP12_SanctionOutcome';
import MP07_DocumentChecklist from './portal/documents/MP07_DocumentChecklist';
import MP13_DocumentationActions from './portal/documents/MP13_DocumentationActions';
import MP14_DisbursementStatus from './portal/disbursement/MP14_DisbursementStatus';
import MP15_MyLoans from './portal/loans/MP15_MyLoans';
import MP17_Repayments from './portal/loans/MP17_Repayments';
import MP18_DirectRepaymentInfo from './portal/loans/MP18_DirectRepaymentInfo';
import MP20_ClosureNOC from './portal/loans/MP20_ClosureNOC';
import MP19_NoticesLetters from './portal/notices/MP19_NoticesLetters';
import MP23_Notifications from './portal/notifications/MP23_Notifications';
import MP22_ProduceSupply from './portal/supply/MP22_ProduceSupply';
import MP24_SupportGrievance from './portal/support/MP24_SupportGrievance';
import MP25_SecuritySettings from './portal/auth/MP25_SecuritySettings';
import MemberPortalLayout from './portal/MemberPortalLayout';
import { useRole } from '../../contexts/RoleContext';

export type BorrowerTab =
  | 'overview' | 'myProfile'
  | 'newApplication' | 'myApplications' | 'application' | 'sanctionOutcome'
  | 'documentationActions' | 'disbursementStatus'
  | 'repayments' | 'directRepayment' | 'documents' | 'notices'
  | 'loanHistory' | 'closureNoc' | 'notifications' | 'supply'
  | 'grievance' | 'securitySettings';
type ApplicationStep = 'applicant' | 'shareholding' | 'loan' | 'nominee' | 'documents' | 'declarations' | 'review';

// Mock: check if this borrower is an FPC
const isFPCMember = false; // Set true to demo FPC view

const repaymentSchedule = [
  { due: '2024-12-31', principal: 100000, interest: 6000, total: 106000, status: 'paid', paid: '2024-12-28', utr: 'SFPCL2024120010' },
  { due: '2025-03-31', principal: 100000, interest: 5500, total: 105500, status: 'paid', paid: '2025-03-29', utr: 'SFPCL2025030022' },
  { due: '2025-06-30', principal: 100000, interest: 5000, total: 105000, status: 'overdue', paid: null, utr: null },
  { due: '2025-09-30', principal: 100000, interest: 4500, total: 104500, status: 'upcoming', paid: null, utr: null },
  { due: '2025-12-31', principal: 100000, interest: 4000, total: 104000, status: 'upcoming', paid: null, utr: null },
  { due: '2026-03-31', principal: 0,      interest: 3500, total: 3500,   status: 'upcoming', paid: null, utr: null },
];

const myDocuments = [
  { name: 'PAN Card Copy',              status: 'verified',   date: '2024-08-10', section: 'KYC', note: 'Self-attested borrower copy' },
  { name: 'Aadhaar Card Copy',          status: 'verified',   date: '2024-08-10', section: 'KYC', note: 'Masked display; full value restricted' },
  { name: 'Nominee PAN and Aadhaar',    status: 'verified',   date: '2024-08-12', section: 'Nominee', note: 'Includes signed nominee declaration' },
  { name: 'Share Certificate Copy',     status: 'verified',   date: '2024-08-12', section: 'Shareholding', note: 'Folio M-00042; 5 shares' },
  { name: '7/12 Extract',               status: 'verified',   date: '2024-08-14', section: 'Land', note: '4.5 acres under cultivation' },
  { name: 'Crop Plan',                  status: 'verified',   date: '2024-08-14', section: 'Crop', note: 'Grapes and tomato cultivation plan' },
  { name: 'Six-Month Bank Statement',   status: 'deficient',  date: '2024-08-15', section: 'Bank', note: 'February to April pages requested again' },
  { name: 'Term Sheet',                 status: 'available',  date: '2024-09-15', section: 'Sanction', note: 'Signed by CFO for amount up to ₹5,00,000' },
  { name: 'Loan Agreement',             status: 'available',  date: '2024-09-18', section: 'Legal', note: 'Stamped and notarised' },
  { name: 'Disbursement Advice',        status: 'available',  date: '2024-09-22', section: 'Disbursement', note: 'UTR retained in loan file' },
  { name: 'Repayment Schedule',         status: 'available',  date: '2024-09-22', section: 'Repayment', note: 'Principal-first allocation' },
  { name: 'FY 2025 Interest Invoice',   status: 'available',  date: '2025-04-30', section: 'Interest', note: 'Yearly interest invoice' },
  { name: 'NOC',                        status: 'pending',    date: null,         section: 'Closure', note: 'Available after full repayment and security return' },
];

const BorrowerPortal: React.FC<{ onLogout?: () => void }> = ({ onLogout }) => {
  const { currentUser } = useRole();
  const [activeTab, setActiveTab] = useState<BorrowerTab>('overview');
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const tabs: { id: BorrowerTab; label: string; }[] = [
    { id: 'overview',     label: 'Overview' },
    { id: 'myProfile',    label: 'My Profile' },
    { id: 'newApplication', label: 'New Application' },
    { id: 'myApplications', label: 'My Applications' },
    { id: 'application',  label: 'Application Status' },
    { id: 'sanctionOutcome', label: 'Sanction Terms' },
    { id: 'documentationActions', label: 'Documentation Actions' },
    { id: 'disbursementStatus', label: 'Disbursement Status' },
    { id: 'loanHistory',  label: 'My Loans' },
    { id: 'repayments',   label: 'Repayments' },
    { id: 'directRepayment', label: 'Direct Repayment' },
    { id: 'documents',    label: 'My Documents' },
    { id: 'notices',      label: 'Notices & Letters' },
    { id: 'closureNoc',   label: 'Closure & NOC' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'supply',       label: 'Produce Supply' },
    { id: 'grievance',    label: 'Raise Grievance' },
    { id: 'securitySettings', label: 'Security Settings' },
  ];
  const activeSectionLabel = tabs.find(tab => tab.id === activeTab)?.label || 'My Loan';

  return (
    <>
      <MemberPortalLayout
        activeTab={activeTab}
        activeSectionLabel={activeSectionLabel}
        onNavigate={(page) => setActiveTab(page as BorrowerTab)}
        onLogout={onLogout}
      >

        {/* Tab content */}
        {activeTab === 'newApplication' && (
          <MP05_NewApplication
            onNavigateToApplication={(id) => {
              setSelectedApplicationId(id);
              setActiveTab('application');
            }}
          />
        )}

        {activeTab === 'myApplications' && (
          <MP09_MyApplications
            onNavigateToApplication={(id) => {
              setSelectedApplicationId(id);
              setActiveTab('application');
            }}
            onNavigateToNew={() => setActiveTab('newApplication')}
          />
        )}

        {activeTab === 'overview' && (
          <MP03_Dashboard onNavigate={(page) => setActiveTab(page as BorrowerTab)} />
        )}
        
        {activeTab === 'myProfile' && (
          <MP04_MyProfile />
        )}

        {activeTab === 'application' && (
          <MP10_ApplicationStatus 
            applicationId={selectedApplicationId}
            onBack={() => setActiveTab('myApplications')}
          />
        )}

        {activeTab === 'sanctionOutcome' && <MP12_SanctionOutcome />}
        {activeTab === 'documentationActions' && <MP13_DocumentationActions />}
        {activeTab === 'disbursementStatus' && <MP14_DisbursementStatus />}
        {activeTab === 'repayments' && <MP17_Repayments />}
        {activeTab === 'directRepayment' && <MP18_DirectRepaymentInfo />}
        {activeTab === 'documents' && <MP07_DocumentChecklist />}
        {activeTab === 'notices' && <MP19_NoticesLetters />}
        {activeTab === 'closureNoc' && <MP20_ClosureNOC />}
        {activeTab === 'notifications' && <MP23_Notifications />}
        {activeTab === 'grievance' && <MP24_SupportGrievance />}
        {activeTab === 'supply' && <MP22_ProduceSupply />}
        {activeTab === 'loanHistory' && <MP15_MyLoans />}
        {activeTab === 'securitySettings' && <MP25_SecuritySettings />}
      </MemberPortalLayout>

      {/* Upload modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Upload Document</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Document Type</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  <option>PAN Card</option>
                  <option>Aadhaar Card</option>
                  <option>Nominee PAN/Aadhaar</option>
                  <option>Share Certificate Copy</option>
                  <option>7/12 Extract</option>
                  <option>Bank Statement</option>
                  <option>Crop Plan</option>
                  <option>Borrower/Nominee Signature Page</option>
                  <option>Other</option>
                </select>
              </div>
              <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center">
                <Upload size={24} className="mx-auto text-slate-300 mb-2" />
                <p className="text-sm text-slate-500">Click to select file or drag and drop</p>
                <p className="text-xs text-slate-400 mt-1">PDF, JPG, PNG · Max 5 MB</p>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowUploadModal(false)}
                className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowUploadModal(false)}
                className="flex-1 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BorrowerPortal;
