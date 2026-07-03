import {
  API_BASE_URL,
  AuthSessionError,
  loadStoredAuthSession,
} from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: Record<string, unknown>;
  };
}

export interface TracerRecord {
  label: string;
  reference: string;
  status: string;
  amount?: string;
}

interface MemberResponse {
  member_id: string;
  reference: string;
  display_name: string;
  status: string;
}

interface ApplicationResponse {
  loan_application_id: string;
  reference: string;
  status: string;
  amount: string;
}

interface AccountResponse {
  loan_account_id: string;
  reference: string;
  status: string;
  amount: string;
}

interface RepaymentResponse {
  repayment_id: string;
  reference: string;
  status: string;
  amount: string;
}

interface ActionResponse {
  new_status: string;
}

export const runTracerLifecycle = async (): Promise<TracerRecord[]> => {
  const member = await tracerRequest<MemberResponse>('/api/v1/tracer/members/', {
    display_name: 'Tracer Member',
  });
  const application = await tracerRequest<ApplicationResponse>(
    `/api/v1/tracer/members/${member.member_id}/loan-applications/`,
    { amount: '400000.00' },
  );
  await tracerRequest<ActionResponse>(
    `/api/v1/tracer/loan-applications/${application.loan_application_id}/sanction/`,
  );
  const account = await tracerRequest<AccountResponse>(
    `/api/v1/tracer/loan-applications/${application.loan_application_id}/loan-account/`,
  );
  const disbursement = await tracerRequest<ActionResponse>(
    `/api/v1/tracer/loan-accounts/${account.loan_account_id}/disburse/`,
  );
  const repayment = await tracerRequest<RepaymentResponse>(
    `/api/v1/tracer/loan-accounts/${account.loan_account_id}/repayments/`,
    { amount: '400000.00' },
  );
  const closure = await tracerRequest<ActionResponse>(
    `/api/v1/tracer/loan-accounts/${account.loan_account_id}/close/`,
  );

  return [
    { label: 'Member', reference: member.reference, status: member.status },
    {
      label: 'Application',
      reference: application.reference,
      status: 'sanctioned',
      amount: application.amount,
    },
    {
      label: 'Sanction',
      reference: application.reference,
      status: disbursement ? 'recorded' : 'pending',
    },
    {
      label: 'Loan account',
      reference: account.reference,
      status: closure.new_status,
      amount: account.amount,
    },
    {
      label: 'Repayment',
      reference: repayment.reference,
      status: repayment.status,
      amount: repayment.amount,
    },
  ];
};

const tracerRequest = async <T>(path: string, body?: Record<string, unknown>): Promise<T> => {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
    },
    body: JSON.stringify(body || {}),
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }
  return envelope.data;
};
