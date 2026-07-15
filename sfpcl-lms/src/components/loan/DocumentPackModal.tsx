import React from 'react';
import {
  Download, Eye, AlertTriangle, FileText, Upload, Check, Stamp
} from 'lucide-react';
import Modal from '../ui/Modal';
import StatusBadge from '../ui/StatusBadge';
import type { DocumentationAction, DocumentationItem } from '../../services/documentationWorkspaceApi';

interface DocumentPackModalProps {
  isOpen: boolean;
  onClose: () => void;
  applicationReference: string;
  borrowerName: string;
  checklistStatus: string;
  blockerCount: number;
  summary: { status: string; available_count: number; missing_count: number; pending_review_count: number };
  items: DocumentationItem[];
  onDownload: (item: DocumentationItem) => void;
  onAction: (action: DocumentationAction) => void;
}

const DocumentPackModal: React.FC<DocumentPackModalProps> = ({
  isOpen, onClose, applicationReference, borrowerName, checklistStatus, blockerCount,
  summary, items, onDownload, onAction,
}) => {
  const sectionFor = (code: string) => ({
    witness_pan_aadhaar: 'Application & KYC', cancelled_cheque: 'Application & KYC',
    final_checklist: 'Appraisal & Sanction', term_sheet: 'Legal Documents',
    loan_agreement: 'Legal Documents', poa: 'Legal Documents',
    tri_party_agreement: 'Legal Documents', bank_verification_letter: 'Legal Documents',
    sh4: 'Security Documents', cdsl_pledge: 'Security Documents', blank_dated_cheque: 'Security Documents',
  }[code] || 'Legal Documents');
  const sections = ['Application & KYC', 'Appraisal & Sanction', 'Legal Documents', 'Security Documents']
    .map(title => ({ title, rows: items.filter(item => sectionFor(item.item_code) === title) }));
  const isBlocked = blockerCount > 0;
  const actionLabel = (action: string) => action === 'generate_document' ? 'Generate document' : action === 'complete_item' ? 'Mark complete' : 'Verify document';
  const getBadgeFamily = (status: string) => {
    switch (status) {
      case 'complete': return 'approved';
      case 'blocked': return 'rejected';
      case 'pending': return 'pending';
      case 'not_required': return 'neutral';
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

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={'Document Pack — ' + applicationReference}
      subtitle={borrowerName}
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
                  label={summary.status}
                  family={summary.status === 'ready' ? 'approved' : 'pending'}
                  size="md"
                />
              </div>
              <p className="text-sm text-slate-600 flex items-center gap-4">
                <span className="font-medium text-green-700">{summary.available_count} available</span>
                <span className="font-medium text-red-600">{summary.missing_count} missing</span>
                <span className="font-medium text-amber-600">{summary.pending_review_count} pending review</span>
              </p>
            </div>
            <StatusBadge label={checklistStatus} size="sm" />
          </div>
          
          {isBlocked && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 flex items-center gap-2">
              <AlertTriangle size={16} className="text-amber-600" />
              Pack incomplete: {blockerCount} required item(s) missing or pending review.
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
                {section.rows.map(item => {
                  const action = item.available_actions[0];
                  return (
                  <div key={item.item_code} className="p-3 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center flex-shrink-0 text-slate-400">
                        <FileText size={14} />
                      </div>
                      <p className="text-sm font-medium text-slate-800 truncate">{item.item_label}</p>
                    </div>
                    
                    <div className="flex items-center gap-4 flex-shrink-0">
                      <StatusBadge label={!item.applicable ? 'not_required' : item.status} family={getBadgeFamily(item.status)} size="sm" />
                      
                      <div className="w-28 flex justify-end">
                        {item.document?.download && (
                          <button className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors" onClick={() => onDownload(item)}>
                            {getActionIcon('Download')} Download
                          </button>
                        )}
                        {!item.document?.download && action && (
                          <button className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors" onClick={() => onAction(action)}>
                            {action.action === 'generate_document' ? <Upload size={14} /> : <Check size={14} />}
                            {actionLabel(action.action)}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );})}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Modal>
  );
};

export default DocumentPackModal;
