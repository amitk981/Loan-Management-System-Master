import {
  fetchApplicationDeficiencies,
  fetchApplicationDetail,
  fetchApplicationDocumentChecklist,
  type ApplicationDeficiency,
  type ApplicationDocumentChecklistItem,
  type StaffApplication,
} from '../../services/applicationIntakeApi';

export interface ApplicationDetailData {
  application: StaffApplication;
  checklistItems: ApplicationDocumentChecklistItem[];
  deficiencies: ApplicationDeficiency[];
}

export const loadApplicationDetail = async (applicationId: string): Promise<ApplicationDetailData> => {
  const [application, checklist, deficiencies] = await Promise.all([
    fetchApplicationDetail(applicationId),
    fetchApplicationDocumentChecklist(applicationId),
    fetchApplicationDeficiencies(applicationId),
  ]);
  return {
    application,
    checklistItems: checklist.items,
    deficiencies: deficiencies.items,
  };
};
