import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { StaffNomineeSelectionView } from './NewApplication';
import { PortalNomineeSelectionView } from '../borrower/portal/applications/MP05_NewApplication';

const nominee = {
  nominee_id: 'api-nominee-1',
  nominee_name: 'API Selected Nominee',
  date_of_birth: '1984-05-20',
  age_at_application: 42,
  gender: 'female',
  relationship_to_borrower: 'Spouse',
  pan: { masked: '******234F', can_view_full: false },
  aadhaar: { masked: '********9012', can_view_full: false },
  kyc_status: 'verified',
  minor_flag: false,
  signature_required_flag: true,
  created_at: '2026-07-10T00:00:00Z',
};

describe('application nominee selection views', () => {
  it('renders a selected real staff API nominee without identity values', () => {
    const html = renderToStaticMarkup(
      <StaffNomineeSelectionView nominees={[nominee]} selectedNomineeId={nominee.nominee_id} status="success" onSelect={vi.fn()} />,
    );
    expect(html).toContain('API Selected Nominee');
    expect(html).toContain('Spouse');
    expect(html).toContain('42');
    expect(html).not.toContain('******234F');
    expect(html).not.toContain('********9012');
  });

  it('renders selected and empty portal API nominee states without hardcoded people', () => {
    const selected = renderToStaticMarkup(
      <PortalNomineeSelectionView nominees={[nominee]} selectedNomineeId={nominee.nominee_id} loading={false} onSelect={vi.fn()} />,
    );
    const empty = renderToStaticMarkup(
      <PortalNomineeSelectionView nominees={[]} selectedNomineeId="" loading={false} onSelect={vi.fn()} />,
    );
    expect(selected).toContain('API Selected Nominee');
    expect(selected).toContain('verified');
    expect(selected).not.toContain('******234F');
    expect(empty).toContain('No nominees are available');
    expect(selected).not.toContain('Suman Thorat');
  });

  it('renders the portal nominee API error state', () => {
    const html = renderToStaticMarkup(
      <PortalNomineeSelectionView nominees={[]} selectedNomineeId="" loading={false} error onSelect={vi.fn()} />,
    );
    expect(html).toContain('Nominees could not be loaded');
  });
});
