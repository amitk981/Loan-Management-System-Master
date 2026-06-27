export type CompletenessItem = {
  id: string;
  category: string;
  label: string;
  required: true;
  deficiencyReason: string;
};

export const COMPLETENESS_ITEMS: CompletenessItem[] = [
  {
    id: 'application_form',
    category: 'Application details',
    label: 'Loan Application Form present',
    required: true,
    deficiencyReason: 'Loan Application Form is missing',
  },
  {
    id: 'applicant_signature',
    category: 'Application details',
    label: 'Applicant signature present',
    required: true,
    deficiencyReason: 'Applicant signature is missing',
  },
  {
    id: 'nominee_signature',
    category: 'Nominee validation',
    label: 'Nominee signature present',
    required: true,
    deficiencyReason: 'Nominee signature is missing',
  },
  {
    id: 'folio_number',
    category: 'Mandatory field checklist',
    label: 'Folio number present',
    required: true,
    deficiencyReason: 'Folio number is missing',
  },
  {
    id: 'shares_present',
    category: 'Mandatory field checklist',
    label: 'Number of shares present',
    required: true,
    deficiencyReason: 'Number of shares is missing',
  },
  {
    id: 'loan_amount',
    category: 'Mandatory field checklist',
    label: 'Required loan amount present',
    required: true,
    deficiencyReason: 'Required loan amount is missing',
  },
  {
    id: 'nominee_fields',
    category: 'Nominee validation',
    label: 'Nominee name, age, Aadhaar, PAN and gender present',
    required: true,
    deficiencyReason: 'Nominee name, age, Aadhaar, PAN or gender is missing',
  },
  {
    id: 'borrower_kyc',
    category: 'Mandatory document checklist',
    label: 'Borrower PAN and Aadhaar uploaded',
    required: true,
    deficiencyReason: 'Borrower PAN or Aadhaar upload is missing',
  },
  {
    id: 'nominee_kyc',
    category: 'Mandatory document checklist',
    label: 'Nominee PAN and Aadhaar uploaded',
    required: true,
    deficiencyReason: 'Nominee PAN or Aadhaar upload is missing',
  },
  {
    id: 'share_certificate',
    category: 'Mandatory document checklist',
    label: 'Share certificate uploaded if physical',
    required: true,
    deficiencyReason: 'Share certificate is required for physical shares',
  },
  {
    id: 'land_712',
    category: 'Mandatory document checklist',
    label: '7/12 extract uploaded',
    required: true,
    deficiencyReason: '7/12 extract is missing',
  },
  {
    id: 'crop_plan',
    category: 'Mandatory document checklist',
    label: 'Crop plan uploaded',
    required: true,
    deficiencyReason: 'Crop plan is missing',
  },
  {
    id: 'bank_statement',
    category: 'Mandatory document checklist',
    label: 'Six-month bank statement uploaded',
    required: true,
    deficiencyReason: 'Six-month bank statement is missing',
  },
];

export const COMPLETENESS_CATEGORIES = [
  'Application details',
  'Mandatory field checklist',
  'Mandatory document checklist',
  'Nominee validation',
] as const;

export const getNextLoanReference = (references: string[]) => {
  const next = references.reduce((max, ref) => {
    const match = ref.match(/^LO(\d{8})$/);
    return match ? Math.max(max, Number(match[1])) : max;
  }, 0) + 1;

  return `LO${String(next).padStart(8, '0')}`;
};
