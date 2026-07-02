import React from 'react';
import {
  Download, Eye, CheckCircle2, AlertTriangle, FileText, Upload, Check, Stamp
} from 'lucide-react';
import Modal from '../ui/Modal';
import StatusBadge from '../ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import type { LoanApplication, DocumentRecord } from '../../types';
import { documents } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface DocumentPackModalProps {
  isOpen: boolean;
  onClose: () => void;
  app: LoanApplication;
}

const DocumentPackModal: React.FC<DocumentPackModalProps> = ({ isOpen, onClose, app }) => {
  const { currentUser, can } = useRole();
  const role = currentUser.role;

  // Find actual documents for this app from mock data
  const appDocs = documents.filter(d => d.applicationId === app.id);

  const getDoc = (type: string) => appDocs.find(d => d.documentType === type);

  // Helper to determine status and action for a row
  const evaluateRow = (
    name: string,
    docType: string | null,
    isApplicable: boolean,
    isMandatory: boolean,
    ownerRole?: string
  ) => {
    if (!isApplicable) {
      return { name, status: 'Not Required', action: null };
    }

    const doc = docType ? getDoc(docType) : null;
    let status = 'Missing';
    
    if (doc) {
      if (['verified', 'stamped', 'notarised', 'complete'].includes(doc.status)) {
        status = 'Available';
      } else if (['uploaded', 'under_review'].includes(doc.status)) {
        status = 'Pending Review';
      } else {
        status = 'Missing';
      }
    } else {
      if (!isMandatory) status = 'Not Required';
      else status = 'Missing';
    }

    // Determine action based on role permissions
    let action = null;
    const canManage = ownerRole ? role === ownerRole : false;

    if (status === 'Available') {
      action = 'View'; // Everyone can view available docs in the pack
    } else if (status === 'Pending Review' && canManage) {
      action = 'Verify';
    } else if (status === 'Missing' && canManage) {
      action = 'Upload';
    }

    // Note: The document pack must not expose approval actions or state bypasses.
    // Ensure we restrict actions if readOnly
    if (role === 'auditor') {
      action = status === 'Available' ? 'Download' : null;
    }

    return { name, status, action };
  };

  const sections = [
    {
      title: 'Application & KYC',
      rows: [
        evaluateRow('Loan Application Form', 'checklist', true, true),
        evaluateRow('Borrower PAN', 'pan', true, true),
        evaluateRow('Borrower Aadhaar', 'aadhaar', true, true),
        evaluateRow('Nominee PAN', 'nominee_pan', true, true),
        evaluateRow('Nominee Aadhaar', 'nominee_aadhaar', true, true),
        evaluateRow('7/12 Extract', 'land_712', true, true),
        evaluateRow('Crop Plan', 'crop_plan', true, true),
        evaluateRow('Six-month Bank Statement', 'bank_statement', true, true),
      ]
    },
    {
      title: 'Appraisal & Sanction',
      rows: [
        evaluateRow('Appraisal Note', 'appraisal_note', true, true),
        evaluateRow('Sanction Letter', 'sanction_letter', true, true),
        evaluateRow('Exception Note', 'exception_note', !!app.isException, !!app.isException),
      ]
    },
    {
      title: 'Legal Documents',
      rows: [
        evaluateRow('Term Sheet', 'term_sheet', true, true, 'compliance_team'),
        evaluateRow('Loan Agreement', 'loan_agreement', true, true, 'compliance_team'),
        evaluateRow('Power of Attorney', 'poa', true, true, 'compliance_team'),
        evaluateRow('Tri-party Agreement', 'tri_party', true, true, 'compliance_team'),
        evaluateRow('Bank Verification Letter', 'bank_verification_letter', !!app.sapCustomerCode, !!app.sapCustomerCode, 'compliance_team'),
      ]
    },
    {
      title: 'Security Documents',
      rows: [
        evaluateRow('SH-4 Physical Share Transfer Form', 'sh4', app.shareMode === 'physical', app.shareMode === 'physical', 'company_secretary'),
        evaluateRow('CDSL Pledge Evidence', 'cdsl_pledge', app.shareMode === 'demat', app.shareMode === 'demat', 'compliance_team'),
        evaluateRow('Blank-dated Cheque', 'blank_cheque', true, true, 'compliance_team'),
        evaluateRow('Custody Acknowledgement', 'custody_ack', app.shareMode === 'physical', app.shareMode === 'physical', 'company_secretary'),
      ]
    },
    {
      title: 'Audit',
      rows: [
        { name: 'Pack generated', status: 'Available', action: 'View' },
        { name: 'Document viewed events', status: 'Available', action: 'View' },
      ]
    }
  ];

  const allRows = sections.flatMap(s => s.rows).filter(r => r.status !== 'Not Required');
  const availableCount = allRows.filter(r => r.status === 'Available').length;
  const missingCount = allRows.filter(r => r.status === 'Missing').length;
  const pendingReviewCount = allRows.filter(r => r.status === 'Pending Review').length;

  const packStatus = (missingCount > 0 || pendingReviewCount > 0 ? 'Incomplete' : 'Ready') as 'Ready' | 'Incomplete' | 'Missing';

  // Pack generation mocked metadata
  const generatedAt = new Date().toISOString();
  const generatedBy = 'Suresh Patil';
  
  const getBadgeFamily = (status: string) => {
    switch (status) {
      case 'Available': return 'approved';
      case 'Missing': return 'rejected';
      case 'Pending Review': return 'pending';
      case 'Not Required': return 'neutral';
      case 'Not Generated': return 'neutral';
      case 'Outdated': return 'blocked';
      default: return 'neutral';
    }
  };

  const getActionIcon = (action: string | null) => {
    switch (action) {
      case 'View': return <Eye size={14} />;
      case 'Download': return <Download size={14} />;
      case 'Upload': return <Upload size={14} />;
      case 'Verify': return <Check size={14} />;
      case 'Mark stamped': return <Stamp size={14} />;
      default: return null;
    }
  };

  const isBlocked = packStatus === 'Incomplete';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Document Pack — ${app.applicationNumber}`}
      subtitle={`${app.memberName} · ${fmt(app.requestedAmount)} · ${app.status.replace(/_/g, ' ')}`}
      size="xl"
      footer={
        <div className="flex items-center justify-between w-full">
          <div className="text-sm text-slate-500">
            {isBlocked && (
              <span className="flex items-center gap-1.5 text-amber-700">
                <AlertTriangle size={14} /> Complete required application details before generating document pack.
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button onClick={onClose} className="btn-secondary">Close</button>
            {!isBlocked && (
              <button className="btn-primary flex items-center gap-2">
                <Download size={16} /> Download available docs
              </button>
            )}
          </div>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Top Summary Card */}
        <div className="card bg-slate-50 border border-slate-200">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-bold text-slate-900">Pack Status</h3>
                <StatusBadge 
                  label={packStatus} 
                  family={packStatus === 'Ready' ? 'approved' : 'pending'} 
                  size="md" 
                />
              </div>
              <p className="text-sm text-slate-600 flex items-center gap-4">
                <span className="font-medium text-green-700">{availableCount} available</span>
                <span className="font-medium text-red-600">{missingCount} missing</span>
                <span className="font-medium text-amber-600">{pendingReviewCount} pending review</span>
              </p>
            </div>
            
            {packStatus !== 'Missing' && (
              <div className="text-right">
                <p className="text-xs text-slate-500">Last generated: {new Date(generatedAt).toLocaleString('en-IN')}</p>
                <p className="text-xs text-slate-500 mt-1">Generated by: {generatedBy} · Compliance Team</p>
              </div>
            )}
          </div>
          
          {isBlocked && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 flex items-center gap-2">
              <AlertTriangle size={16} className="text-amber-600" />
              Pack incomplete: {missingCount + pendingReviewCount} required item(s) missing or pending review.
            </div>
          )}
        </div>

        {/* Document Sections */}
        <div className="space-y-5">
          {sections.map((section, idx) => (
            <div key={idx}>
              <h4 className="text-sm font-bold text-slate-900 mb-3 uppercase tracking-wide border-b border-slate-100 pb-2">
                {section.title}
              </h4>
              <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-white">
                {section.rows.map((row, rIdx) => (
                  <div key={rIdx} className="p-3 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center flex-shrink-0 text-slate-400">
                        <FileText size={14} />
                      </div>
                      <p className="text-sm font-medium text-slate-800 truncate">{row.name}</p>
                    </div>
                    
                    <div className="flex items-center gap-4 flex-shrink-0">
                      <StatusBadge label={row.status} family={getBadgeFamily(row.status)} size="sm" />
                      
                      <div className="w-28 flex justify-end">
                        {row.action && (
                          <button className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors">
                            {getActionIcon(row.action)}
                            {row.action}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Modal>
  );
};

export default DocumentPackModal;
