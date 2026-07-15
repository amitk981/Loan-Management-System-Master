import { useCallback, useEffect, useState } from 'react';
import { AuthSessionError } from '../../../../services/authSession';
import {
  downloadPortalDocumentationAction,
  fetchPortalDocumentContent,
  fetchPortalApplications,
  fetchPortalDocumentationActions,
  openPortalDocumentBlob,
  PortalDocumentationAction,
  PortalDocumentationProjection,
  uploadPortalDocumentationAction,
} from '../../../../services/portalApi';
const SANCTIONED_STATUS = 'approved_by_sanction_committee';
export const usePortalDocumentationActions = () => {
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [projection, setProjection] = useState<PortalDocumentationProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  useEffect(() => {
    let current = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const applications = await fetchPortalApplications();
        const sanctioned = applications.items.find(item => item.application_status === SANCTIONED_STATUS);
        if (!current) return;
        if (!sanctioned) {
          setApplicationId(null);
          setProjection(null);
          return;
        }
        setApplicationId(sanctioned.loan_application_id);
        const canonical = await fetchPortalDocumentationActions(sanctioned.loan_application_id);
        if (current) setProjection(canonical);
      } catch (requestError) {
        if (current) setError(portalErrorMessage(requestError));
      } finally {
        if (current) setLoading(false);
      }
    };
    void load();
    return () => { current = false; };
  }, []);
  const upload = useCallback(async (action: PortalDocumentationAction, file: File, notes: string) => {
    if (!applicationId) return false;
    setUploading(true);
    setError(null);
    setSuccess(null);
    try {
      await uploadPortalDocumentationAction(applicationId, action.action_code, file, notes);
      const canonical = await fetchPortalDocumentationActions(applicationId);
      setProjection(canonical);
      setSuccess('Document uploaded for SFPCL review.');
      return true;
    } catch (requestError) {
      setError(portalErrorMessage(requestError));
      return false;
    } finally {
      setUploading(false);
    }
  }, [applicationId]);
  const download = useCallback(async (action: PortalDocumentationAction) => {
    if (!action.download) return;
    setError(null);
    try {
      const descriptor = await downloadPortalDocumentationAction(action.download.action_url);
      const content = await fetchPortalDocumentContent(descriptor.download_url);
      openPortalDocumentBlob(content);
    } catch (requestError) {
      setError(portalErrorMessage(requestError));
    }
  }, []);
  return { projection, loading, error, uploading, success, upload, download };
};
const portalErrorMessage = (error: unknown) => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) return 'Your member portal session has expired. Please sign in again.';
    if (error.status === 403) return 'You are not authorised to view these documentation actions.';
    const firstFieldError = error.fieldErrors && Object.values(error.fieldErrors)[0];
    return firstFieldError || error.message || 'Documentation request failed.';
  }
  return 'Documentation actions could not be loaded. Please try again.';
};
