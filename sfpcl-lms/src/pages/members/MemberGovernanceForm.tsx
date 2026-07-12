import React, { useState } from 'react';
import AlertBanner from '../../components/ui/AlertBanner';
import { AuthSessionError } from '../../services/authSession';
import { createMember, reverifyMemberIdentity, updateMember, type MemberProfileDetail } from '../../services/memberProfileApi';

interface Props {
  profile?: MemberProfileDetail;
  canReverify?: boolean;
  onSaved: (member: MemberProfileDetail) => void | Promise<void>;
  onCancel?: () => void;
}

const MemberGovernanceForm: React.FC<Props> = ({ profile, canReverify = false, onSaved, onCancel }) => {
  const [memberType, setMemberType] = useState(profile?.member_type ?? 'individual_farmer');
  const [mode, setMode] = useState<'ordinary' | 'reverification'>('ordinary');
  const [values, setValues] = useState<Record<string, string>>({
    legal_name: profile?.legal_name ?? '', display_name: profile?.display_name ?? '', folio_number: profile?.folio_number ?? '',
    membership_start_date: profile?.membership_start_date ?? '', mobile_number: profile?.mobile_number ?? '', email: profile?.email ?? '',
    pan: profile?.kyc_status === 'verified' ? profile.pan.masked ?? '' : '',
    aadhaar: profile?.kyc_status === 'verified' ? profile.aadhaar.masked ?? '' : '',
    reason: '', line1: profile?.registered_address.line1 ?? '', line2: profile?.registered_address.line2 ?? '',
    village_city: profile?.registered_address.village_city ?? '', district: profile?.registered_address.district ?? '',
    state: profile?.registered_address.state ?? '', pincode: profile?.registered_address.pincode ?? '',
    first_name: profile?.individual_profile?.first_name ?? '', middle_name: profile?.individual_profile?.middle_name ?? '', last_name: profile?.individual_profile?.last_name ?? '',
    gender: profile?.individual_profile?.gender ?? '', date_of_birth: profile?.individual_profile?.date_of_birth ?? '', occupation: profile?.individual_profile?.occupation ?? '',
    land_area_under_cultivation_acres: profile?.individual_profile?.land_area_under_cultivation_acres ?? '', primary_crop: profile?.individual_profile?.primary_crop ?? '',
    individual_services_availed_flag: String(profile?.individual_profile?.services_availed_flag ?? false), employment_or_service_years: profile?.individual_profile?.employment_or_service_years ?? '',
    institution_type: profile?.producer_institution_profile?.institution_type ?? 'farmer_producer_company',
    authorised_signatory_name: profile?.producer_institution_profile?.authorised_signatory_name ?? '',
    registration_number: profile?.producer_institution_profile?.registration_number ?? '', authorised_signatory_pan: '', authorised_signatory_aadhaar: '',
    board_resolution_required_flag: String(profile?.producer_institution_profile?.board_resolution_required_flag ?? false),
    institution_services_availed_flag: String(profile?.producer_institution_profile?.services_availed_flag ?? false), produce_supply_years: profile?.producer_institution_profile?.produce_supply_years ?? '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const identityLocked = Boolean(profile?.kyc_status === 'verified' && mode === 'ordinary');
  const set = (key: string, value: string) => setValues(current => ({ ...current, [key]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setSubmitting(true); setErrors({}); setMessage('');
    const address = { line1: values.line1, line2: values.line2, village_city: values.village_city, district: values.district, state: values.state, pincode: values.pincode };
    const payload: Record<string, unknown> = profile
      ? { version: profile.version ?? 0, legal_name: values.legal_name, display_name: values.display_name, membership_start_date: values.membership_start_date, registered_address: address, mobile_number: values.mobile_number, email: values.email }
      : { member_type: memberType, legal_name: values.legal_name, display_name: values.display_name, folio_number: values.folio_number,
          membership_start_date: values.membership_start_date, pan: values.pan, ...(memberType === 'individual_farmer' ? { aadhaar: values.aadhaar } : {}),
          registered_address: address, mobile_number: values.mobile_number, email: values.email,
          ...(memberType === 'individual_farmer' ? { individual_profile: { first_name: values.first_name, middle_name: values.middle_name || null, last_name: values.last_name,
            gender: values.gender || null, date_of_birth: values.date_of_birth || null, occupation: values.occupation || null,
            land_area_under_cultivation_acres: values.land_area_under_cultivation_acres || null, primary_crop: values.primary_crop,
            services_availed_flag: values.individual_services_availed_flag === 'true', employment_or_service_years: values.employment_or_service_years || null } } :
            { producer_institution_profile: { institution_type: values.institution_type, registration_number: values.registration_number,
              authorised_signatory_name: values.authorised_signatory_name, authorised_signatory_pan: values.authorised_signatory_pan,
              authorised_signatory_aadhaar: values.authorised_signatory_aadhaar, board_resolution_required_flag: values.board_resolution_required_flag === 'true',
              services_availed_flag: values.institution_services_availed_flag === 'true', produce_supply_years: values.produce_supply_years || null } }) };
    if (profile && mode === 'ordinary' && !identityLocked) {
      if (values.pan) payload.pan = values.pan;
      if (values.aadhaar && memberType === 'individual_farmer') payload.aadhaar = values.aadhaar;
    }
    if (profile && mode === 'reverification') Object.assign(payload, {
      ...(values.pan ? { pan: values.pan } : {}), ...(values.aadhaar && memberType === 'individual_farmer' ? { aadhaar: values.aadhaar } : {}), reason: values.reason,
    });
    try {
      if (profile && mode === 'reverification') {
        await reverifyMemberIdentity(profile.member_id, payload);
        await onSaved(profile);
      } else {
        const saved = profile ? await updateMember(profile.member_id, payload) : await createMember(payload);
        await onSaved(saved);
      }
    } catch (error) {
      if (error instanceof AuthSessionError) { setErrors(error.fieldErrors ?? {}); setMessage(error.code === 'STALE_WRITE' ? 'Member changed on the server. Refresh and retry.' : error.message); }
      else setMessage('Unable to save member.');
    } finally { setSubmitting(false); }
  };

  const field = (name: string, label: string, type = 'text', readOnly = false) => <label className="space-y-1 text-sm"><span className="text-slate-600">{label}</span><input aria-label={label} className="field-input" type={type} value={values[name]} readOnly={readOnly} onChange={event => set(name, event.target.value)} />{errors[name] && <span className="text-xs text-red-600">{errors[name]}</span>}</label>;
  return <form onSubmit={submit} className="card space-y-4">
    <div className="flex items-center justify-between"><h3 className="font-semibold text-slate-800">{profile ? 'Edit Member' : 'Register Member'}</h3>{onCancel && <button type="button" className="btn-secondary text-sm" onClick={onCancel}>Cancel</button>}</div>
    {message && <AlertBanner type="warning" title="Member could not be saved" message={message} />}
    {!profile && <label className="space-y-1 text-sm"><span className="text-slate-600">Member Type</span><select aria-label="Member Type" className="field-select" value={memberType} onChange={event => setMemberType(event.target.value)}><option value="individual_farmer">Individual farmer</option><option value="fpc">FPC</option><option value="producer_institution">Producer institution</option></select></label>}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">{field('legal_name', 'Legal Name')}{field('display_name', 'Display Name')}{!profile && field('folio_number', 'Folio Number')}{field('membership_start_date', 'Membership Start Date', 'date')}{field('mobile_number', 'Mobile Number')}{field('email', 'Email', 'email')}{field('line1', 'Address Line 1')}{field('line2', 'Address Line 2')}{field('village_city', 'Village / City')}{field('district', 'District')}{field('state', 'State')}{field('pincode', 'Pincode')}{!profile && (memberType === 'individual_farmer' ? <>{field('first_name', 'First Name')}{field('middle_name', 'Middle Name')}{field('last_name', 'Last Name')}{field('gender', 'Gender')}{field('date_of_birth', 'Date of Birth', 'date')}{field('occupation', 'Occupation')}{field('land_area_under_cultivation_acres', 'Cultivation Area (acres)', 'number')}{field('primary_crop', 'Primary Crop')}{field('individual_services_availed_flag', 'Services Availed')}{field('employment_or_service_years', 'Employment / Service Years', 'number')}</> : <>{field('institution_type', 'Institution Type')}{field('registration_number', 'Registration Number')}{field('authorised_signatory_name', 'Authorised Signatory')}{field('authorised_signatory_pan', 'Signatory PAN')}{field('authorised_signatory_aadhaar', 'Signatory Aadhaar')}{field('board_resolution_required_flag', 'Board Resolution Required')}{field('institution_services_availed_flag', 'Services Availed')}{field('produce_supply_years', 'Produce Supply Years', 'number')}</>)}</div>
    {identityLocked && <AlertBanner type="info" title="Verified identity locked" message="PAN and Aadhaar are read-only. Use the reasoned reverification action to correct them." />}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">{field('pan', 'PAN', 'text', identityLocked)}{memberType === 'individual_farmer' && field('aadhaar', 'Aadhaar', 'text', identityLocked)}{profile && mode === 'reverification' && field('reason', 'Reverification Reason')}</div>
    {profile && canReverify && <button type="button" className="btn-secondary text-sm" onClick={() => { setMode(current => current === 'ordinary' ? 'reverification' : 'ordinary'); set('pan', ''); set('aadhaar', ''); set('reason', ''); }}>{mode === 'ordinary' ? 'Correct verified identity' : 'Cancel reverification'}</button>}
    <button className="btn-primary text-sm" disabled={submitting || (mode === 'reverification' && (!values.reason.trim() || (!values.pan && !values.aadhaar)))}>{submitting ? 'Saving…' : mode === 'reverification' ? 'Request identity change' : 'Save member'}</button>
  </form>;
};

export default MemberGovernanceForm;
