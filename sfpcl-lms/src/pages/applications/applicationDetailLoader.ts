import {
  fetchApplicationDeficiencies,
  fetchApplicationDetail,
  fetchApplicationDocumentChecklist,
  type ApplicationDeficiency,
  type ApplicationDocumentChecklistItem,
  type StaffApplication,
} from '../../services/applicationIntakeApi';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchAppraisal,
  fetchEligibilityAssessment,
  fetchLoanLimitAssessment,
  type AppraisalNote,
  type EligibilityAssessment,
  type LoanLimitAssessment,
} from '../../services/creditAssessmentApi';

export interface ApplicationDetailData {
  application: StaffApplication;
  checklistItems: ApplicationDocumentChecklistItem[];
  deficiencies: ApplicationDeficiency[];
  eligibility: EligibilityAssessment | null;
  loanLimit: LoanLimitAssessment | null;
  appraisal: AppraisalNote | null;
}

export const loadApplicationDetail = async (applicationId: string): Promise<ApplicationDetailData> => {
  const [application, checklist, deficiencies] = await Promise.all([
    fetchApplicationDetail(applicationId),
    fetchApplicationDocumentChecklist(applicationId),
    fetchApplicationDeficiencies(applicationId),
  ]);
  const credit = application.current_stage === 'credit_assessment'
    ? await Promise.allSettled([
      fetchEligibilityAssessment(applicationId),
      fetchLoanLimitAssessment(applicationId),
      fetchAppraisal(applicationId),
    ])
    : [];
  const failed = credit.find(result => result.status === 'rejected' && !(result.reason instanceof AuthSessionError && result.reason.status === 404));
  if (failed?.status === 'rejected') throw failed.reason;
  return {
    application,
    checklistItems: checklist.items,
    deficiencies: deficiencies.items,
    eligibility: credit[0]?.status === 'fulfilled' ? credit[0].value : null,
    loanLimit: credit[1]?.status === 'fulfilled' ? credit[1].value : null,
    appraisal: credit[2]?.status === 'fulfilled' ? credit[2].value : null,
  };
};
