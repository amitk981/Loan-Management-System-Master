import React from 'react';
import { AlertTriangle, Eye, Upload } from 'lucide-react';
import StatusBadge from '../ui/StatusBadge';
import type { DocumentRecord, SecurityInstrument, ShareMode } from '../../types';
import { documents, securities } from '../../data/mockData';

type Requirement = 'mandatory' | 'conditional' | 'not_required';
type CompactState = 'not_required' | 'pending' | 'uploaded' | 'signed' | 'complete' | 'verified' | 'blocked';

interface ChecklistRow {
  id: string;
  name: string;
  required: Requirement;
  owner: string;
  status: CompactState;
  signatureStatus: CompactState;
  stampStatus: CompactState;
  notaryStatus: CompactState;
  verificationStatus: CompactState;
  evidence: string;
  deficiency: string;
  nextAction: string;
  prerequisitesComplete: boolean;
}

interface DocumentChecklistProps {
  applicationId: string;
  shareMode: ShareMode;
  subsidiaryRepayment?: boolean;
  signatureMismatch?: boolean;
  readOnly?: boolean;
  canVerify?: boolean;
  sensitiveVisible?: boolean;
  finalSignoffsComplete?: boolean;
  finalSignoffProgress?: number;
}

const docByType = (docs: DocumentRecord[], type: string) => docs.find(d => d.documentType === type);

const compactStatus = (doc?: DocumentRecord): CompactState => {
  if (!doc) return 'pending';
  if (doc.status === 'rejected') return 'blocked';
  if (['verified', 'complete', 'notarised'].includes(doc.status)) return 'verified';
  if (doc.status === 'signed') return 'signed';
  if (['uploaded', 'under_review'].includes(doc.status)) return 'uploaded';
  return 'pending';
};

const mask = (value: string, visible?: boolean) => visible ? value : value.replace(/[A-Z0-9]/g, '•');
const isDocVerified = (doc?: DocumentRecord) => !!doc && ['verified', 'complete', 'notarised'].includes(doc.status);
const verifiedTrail = (doc?: DocumentRecord) =>
  doc?.verifiedBy && doc.verifiedAt ? `${doc.verifiedBy} · ${new Date(doc.verifiedAt).toLocaleDateString('en-IN')}` : '';
const securityByType = (items: SecurityInstrument[], type: string) => items.find(item => item.securityType === type);
const shortStatus = (status: CompactState) => status.replace(/_/g, ' ');
const executionSummary = (row: ChecklistRow) => [
  row.signatureStatus !== 'not_required' ? `Sig ${shortStatus(row.signatureStatus)}` : null,
  row.stampStatus !== 'not_required' ? `Stamp ${shortStatus(row.stampStatus)}` : null,
  row.notaryStatus !== 'not_required' ? `Notary ${shortStatus(row.notaryStatus)}` : null,
  row.verificationStatus !== 'not_required' ? `Verify ${shortStatus(row.verificationStatus)}` : null,
].filter(Boolean);

const DocumentChecklist: React.FC<DocumentChecklistProps> = ({
  applicationId,
  shareMode,
  subsidiaryRepayment = true,
  signatureMismatch = true,
  readOnly = false,
  canVerify = false,
  sensitiveVisible = false,
  finalSignoffsComplete = false,
  finalSignoffProgress = 0,
}) => {
  const docs = documents.filter(d => d.applicationId === applicationId);
  const appSecurities = securities.filter(s => s.applicationId === applicationId);
  const pan = docByType(docs, 'pan');
  const aadhaar = docByType(docs, 'aadhaar');
  const nomineePan = docByType(docs, 'nominee_pan');
  const nomineeAadhaar = docByType(docs, 'nominee_aadhaar');
  const witnessPan = docByType(docs, 'witness_pan');
  const witnessAadhaar = docByType(docs, 'witness_aadhaar');
  const poa = docByType(docs, 'poa');
  const triParty = docByType(docs, 'tri_party');
  const sh4 = docByType(docs, 'sh4');
  const termSheet = docByType(docs, 'term_sheet');
  const loanAgreement = docByType(docs, 'loan_agreement');
  const cancelledCheque = docByType(docs, 'cancelled_cheque');
  const blankCheque = docByType(docs, 'blank_cheque');
  const bankVerification = docByType(docs, 'bank_verification_letter');
  const sh4Security = securityByType(appSecurities, 'sh4');
  const cdslSecurity = securityByType(appSecurities, 'cdsl_pledge');
  const sh4Ready = shareMode !== 'physical' || (isDocVerified(sh4) && sh4Security?.status === 'held');
  const cdslReady = shareMode !== 'demat' || cdslSecurity?.status === 'pledged';

  const rows: ChecklistRow[] = [
    {
      id: 'borrower-kyc',
      name: 'Borrower PAN / Aadhaar',
      required: 'mandatory',
      owner: 'Credit / Compliance',
      status: isDocVerified(pan) && isDocVerified(aadhaar) ? 'verified' : 'pending',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: isDocVerified(pan) && isDocVerified(aadhaar) ? 'verified' : 'pending',
      evidence: `${mask('ABCDE1234F', sensitiveVisible)} / Aadhaar ${mask('4521', sensitiveVisible)}`,
      deficiency: pan && aadhaar ? verifiedTrail(pan) || '-' : 'Borrower KYC pending',
      nextAction: pan && aadhaar ? 'View' : 'Upload',
      prerequisitesComplete: isDocVerified(pan) && isDocVerified(aadhaar),
    },
    {
      id: 'nominee-kyc',
      name: 'Nominee PAN / Aadhaar',
      required: 'mandatory',
      owner: 'Credit / Compliance',
      status: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar) ? 'verified' : 'pending',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar) ? 'verified' : 'pending',
      evidence: `${mask('FGHIJ5678K', sensitiveVisible)} / Aadhaar ${mask('7789', sensitiveVisible)}`,
      deficiency: nomineePan && nomineeAadhaar ? verifiedTrail(nomineePan) || '-' : 'Nominee KYC pending',
      nextAction: nomineePan && nomineeAadhaar ? 'View' : 'Upload',
      prerequisitesComplete: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar),
    },
    {
      id: 'witness-kyc',
      name: 'Witness PAN / Aadhaar',
      required: 'mandatory',
      owner: 'Compliance',
      status: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? 'verified' : 'uploaded',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? 'verified' : 'pending',
      evidence: `${mask('WITNS1234Q', sensitiveVisible)} / shareholder check`,
      deficiency: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? verifiedTrail(witnessPan) || '-' : 'Witness shareholder validation pending',
      nextAction: 'Verify',
      prerequisitesComplete: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar),
    },
    {
      id: 'cancelled-cheque',
      name: 'Cancelled cheque',
      required: 'mandatory',
      owner: 'Compliance / Finance',
      status: compactStatus(cancelledCheque),
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: compactStatus(cancelledCheque),
      evidence: `Acct ${mask('1234', sensitiveVisible)} / IFSC RATN••••001`,
      deficiency: compactStatus(cancelledCheque) === 'verified' ? verifiedTrail(cancelledCheque) || '-' : 'Bank proof pending',
      nextAction: compactStatus(cancelledCheque) === 'verified' ? 'View' : 'Upload',
      prerequisitesComplete: compactStatus(cancelledCheque) === 'verified',
    },
    {
      id: 'blank-cheque',
      name: 'Blank-dated cheque custody',
      required: 'mandatory',
      owner: 'Company Secretary',
      status: compactStatus(blankCheque),
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: compactStatus(blankCheque),
      evidence: `Custody ref ${mask('BCHQ-0042', sensitiveVisible)}`,
      deficiency: compactStatus(blankCheque) === 'verified' ? verifiedTrail(blankCheque) || '-' : 'Custody not logged',
      nextAction: compactStatus(blankCheque) === 'verified' ? 'View' : 'Log custody',
      prerequisitesComplete: compactStatus(blankCheque) === 'verified',
    },
    {
      id: 'poa',
      name: 'Power of Attorney',
      required: 'mandatory',
      owner: 'Compliance / CS',
      status: compactStatus(poa),
      signatureStatus: poa?.status === 'signed' || compactStatus(poa) === 'verified' ? 'signed' : 'pending',
      stampStatus: poa?.stampStatus === 'complete' ? 'complete' : 'pending',
      notaryStatus: poa?.notarisationStatus === 'complete' ? 'complete' : 'pending',
      verificationStatus: compactStatus(poa) === 'verified' ? 'verified' : 'pending',
      evidence: 'PoA draft / custody CS cabinet A',
      deficiency: poa?.stampStatus === 'complete' && poa?.notarisationStatus === 'complete' ? verifiedTrail(poa) || '-' : 'Stamp or notary pending',
      nextAction: poa?.stampStatus !== 'complete' ? 'Mark stamped' : 'Mark notarised',
      prerequisitesComplete: compactStatus(poa) === 'verified' && poa?.stampStatus === 'complete' && poa?.notarisationStatus === 'complete',
    },
    {
      id: 'tri-party',
      name: 'Tri-party Agreement',
      required: subsidiaryRepayment ? 'conditional' : 'not_required',
      owner: 'Compliance / CS',
      status: subsidiaryRepayment ? compactStatus(triParty) : 'not_required',
      signatureStatus: subsidiaryRepayment ? (compactStatus(triParty) === 'verified' ? 'signed' : 'pending') : 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: subsidiaryRepayment ? compactStatus(triParty) : 'not_required',
      evidence: subsidiaryRepayment ? 'Subsidiary deduction agreement' : '-',
      deficiency: subsidiaryRepayment && compactStatus(triParty) !== 'verified' ? 'All party signatures pending' : verifiedTrail(triParty) || '-',
      nextAction: subsidiaryRepayment ? 'Upload signed' : 'None',
      prerequisitesComplete: !subsidiaryRepayment || compactStatus(triParty) === 'verified',
    },
    {
      id: 'sh4',
      name: 'SH-4 Physical Share Security',
      required: shareMode === 'physical' ? 'conditional' : 'not_required',
      owner: 'Company Secretary',
      status: shareMode === 'physical' ? (sh4Ready ? 'verified' : compactStatus(sh4)) : 'not_required',
      signatureStatus: shareMode === 'physical' ? (isDocVerified(sh4) ? 'signed' : 'pending') : 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: shareMode === 'physical' ? compactStatus(sh4) : 'not_required',
      evidence: shareMode === 'physical' ? `Folio ${mask('FO-0334', sensitiveVisible)} / cert ${mask('SC-7781', sensitiveVisible)}` : '-',
      deficiency: shareMode === 'physical' && !sh4Ready ? 'Witness signature or custody pending' : verifiedTrail(sh4) || '-',
      nextAction: shareMode === 'physical' ? 'Assign custody' : 'None',
      prerequisitesComplete: sh4Ready,
    },
    {
      id: 'cdsl',
      name: 'CDSL pledge',
      required: shareMode === 'demat' ? 'conditional' : 'not_required',
      owner: 'Company Secretary',
      status: shareMode === 'demat' ? (cdslReady ? 'verified' : 'pending') : 'not_required',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: shareMode === 'demat' ? (cdslReady ? 'verified' : 'pending') : 'not_required',
      evidence: shareMode === 'demat' ? `BO ${mask('120816000042', sensitiveVisible)} / PSN ${cdslSecurity?.psnNumber ? mask(cdslSecurity.psnNumber, sensitiveVisible) : 'pending'}` : '-',
      deficiency: shareMode === 'demat' && !cdslReady ? 'DP acceptance pending' : '-',
      nextAction: shareMode === 'demat' && !cdslReady ? 'Enter PSN' : 'View',
      prerequisitesComplete: cdslReady,
    },
    {
      id: 'term-sheet',
      name: 'Term Sheet',
      required: 'mandatory',
      owner: 'Compliance',
      status: compactStatus(termSheet),
      signatureStatus: compactStatus(termSheet) === 'verified' ? 'signed' : 'pending',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: compactStatus(termSheet),
      evidence: 'Borrower, nominee, CFO/director route',
      deficiency: compactStatus(termSheet) === 'verified' ? verifiedTrail(termSheet) || '-' : 'Signature route pending',
      nextAction: 'Route signatures',
      prerequisitesComplete: compactStatus(termSheet) === 'verified',
    },
    {
      id: 'loan-agreement',
      name: 'Loan Agreement',
      required: 'mandatory',
      owner: 'Compliance / CS',
      status: compactStatus(loanAgreement),
      signatureStatus: compactStatus(loanAgreement) === 'verified' ? 'signed' : 'pending',
      stampStatus: loanAgreement?.stampStatus === 'complete' ? 'complete' : 'pending',
      notaryStatus: loanAgreement?.notarisationStatus === 'complete' ? 'complete' : 'pending',
      verificationStatus: compactStatus(loanAgreement),
      evidence: `Stamp ${mask('E-STAMP-2026-0043', sensitiveVisible)}`,
      deficiency: compactStatus(loanAgreement) === 'verified' ? verifiedTrail(loanAgreement) || '-' : 'Borrower/witness signature, stamp and notary required',
      nextAction: loanAgreement?.stampStatus === 'complete' ? 'Mark notarised' : 'Upload signed',
      prerequisitesComplete: compactStatus(loanAgreement) === 'verified' && loanAgreement?.stampStatus === 'complete' && loanAgreement?.notarisationStatus === 'complete',
    },
    {
      id: 'bank-verification',
      name: 'Bank Verification Letter / declaration',
      required: signatureMismatch ? 'conditional' : 'not_required',
      owner: 'Credit / Compliance',
      status: signatureMismatch ? compactStatus(bankVerification) : 'not_required',
      signatureStatus: signatureMismatch ? 'pending' : 'not_required',
      stampStatus: signatureMismatch ? 'pending' : 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: signatureMismatch ? compactStatus(bankVerification) : 'not_required',
      evidence: signatureMismatch ? `Mismatch: cheque vs PAN / acct ${mask('1234', sensitiveVisible)}` : '-',
      deficiency: signatureMismatch && compactStatus(bankVerification) !== 'verified' ? 'Resolution document pending' : verifiedTrail(bankVerification) || '-',
      nextAction: signatureMismatch ? 'Upload resolution' : 'None',
      prerequisitesComplete: !signatureMismatch || compactStatus(bankVerification) === 'verified',
    },
    {
      id: 'final-signatures',
      name: 'Final checklist signatures',
      required: 'mandatory',
      owner: 'CS / Credit / Sanction / Finance',
      status: finalSignoffsComplete ? 'verified' : 'pending',
      signatureStatus: finalSignoffsComplete ? 'signed' : 'pending',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: finalSignoffsComplete ? 'verified' : 'pending',
      evidence: `${finalSignoffProgress}/4 sign-offs`,
      deficiency: finalSignoffsComplete ? '-' : 'Final sign-offs incomplete',
      nextAction: finalSignoffProgress === 0 ? 'Submit to CS' : 'Submit next',
      prerequisitesComplete: finalSignoffsComplete,
    },
  ];

  const blockingRows = rows.filter(row => row.required !== 'not_required' && !row.prerequisitesComplete);

  const markVerifiedDisabled = (row: ChecklistRow) =>
    readOnly || !canVerify || !row.prerequisitesComplete || row.verificationStatus === 'verified';

  return (
    <div className="space-y-3">
      {blockingRows.length > 0 && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <AlertTriangle size={16} className="text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-800 font-medium">
            Disbursement blocked: {blockingRows[0].name} pending{blockingRows.length > 1 ? ` +${blockingRows.length - 1}` : ''}.
          </p>
        </div>
      )}

      <div className="border border-slate-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm table-fixed">
          <thead className="bg-slate-50">
            <tr>
              <th className="table-header text-left w-[24%]">Document</th>
              <th className="table-header text-left w-[17%]">Requirement</th>
              <th className="table-header text-left w-[19%]">Readiness</th>
              <th className="table-header text-left w-[28%]">Evidence / Deficiency</th>
              <th className="table-header text-left w-[12%]">Next</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map(row => {
              const details = executionSummary(row);
              const canMarkVerified = !markVerifiedDisabled(row);

              return (
                <tr key={row.id} className="hover:bg-slate-50 align-top">
                  <td className="table-cell">
                    <div className="font-medium text-slate-900">{row.name}</div>
                    {row.prerequisitesComplete && (
                      <div className="text-xs text-green-700 mt-1">Ready for gate</div>
                    )}
                  </td>
                  <td className="table-cell">
                    <StatusBadge label={row.required} size="sm" />
                    <div className="text-xs text-slate-500 mt-1">{row.owner}</div>
                  </td>
                  <td className="table-cell">
                    <StatusBadge label={row.status} size="sm" />
                    <div className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {details.length > 0 ? details.join(' · ') : 'No execution controls'}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="text-xs text-slate-600 truncate" title={row.evidence}>{row.evidence}</div>
                    {row.deficiency !== '-' && (
                      <div className={row.prerequisitesComplete ? 'text-xs text-slate-400 mt-1 truncate' : 'text-xs text-amber-700 mt-1 truncate'} title={row.deficiency}>
                        {row.deficiency}
                      </div>
                    )}
                  </td>
                  <td className="table-cell">
                    <div className="flex flex-col items-start gap-1">
                      {row.nextAction !== 'None' && (
                        <button
                          className="text-xs px-2 py-1 border border-slate-200 rounded text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                          disabled={readOnly}
                          title={readOnly ? 'Read-only role' : row.nextAction}
                        >
                          {row.nextAction === 'View' ? <span className="inline-flex items-center gap-1"><Eye size={12} /> View</span> : row.nextAction.includes('Upload') ? <span className="inline-flex items-center gap-1"><Upload size={12} /> Upload</span> : row.nextAction}
                        </button>
                      )}
                      {canMarkVerified && (
                        <button
                          className="text-xs px-2 py-1 bg-blue-50 border border-blue-200 rounded text-blue-700 hover:bg-blue-100"
                          title="Mark verified"
                        >
                          Verify
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DocumentChecklist;
