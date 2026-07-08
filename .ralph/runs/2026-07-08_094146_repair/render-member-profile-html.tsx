import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { mkdirSync, writeFileSync } from 'fs';
import { MemberProfileView } from '../../../sfpcl-lms/src/pages/members/MemberProfile';
import type { MemberProfileDetail } from '../../../sfpcl-lms/src/services/memberProfileApi';

const outDir = '.ralph/runs/2026-07-08_094146_repair/evidence/screenshots/member-profile-html';
mkdirSync(outDir, { recursive: true });

const member: MemberProfileDetail = {
  member_id: 'member-1',
  member_number: 'MEM-00125',
  member_type: 'individual_farmer',
  legal_name: 'Ramesh Patil',
  display_name: 'Ramesh Patil',
  folio_number: 'FOL-456',
  membership_start_date: '2021-04-01',
  membership_status: 'active',
  kyc_status: 'verified',
  rekyc_due_date: '2027-06-22',
  default_status: 'no_default',
  mobile_number: '******7890',
  email: 'ramesh@example.com',
  pan: { masked: '******234F', can_view_full: false },
  aadhaar: { masked: '********9012', can_view_full: false },
  registered_address: {
    line1: 'Village Road',
    line2: 'Near Market',
    village_city: 'Nashik',
    district: 'Nashik',
    state: 'Maharashtra',
    pincode: '422001',
  },
  share_summary: { number_of_shares: 100, holding_mode: 'physical', available_share_count: 100 },
  active_member_status: { status: 'active', verified_at: '2026-06-22T10:30:00Z' },
  individual_profile: {
    land_area_under_cultivation_acres: '5.00',
    primary_crop: 'grapes',
    services_availed_flag: true,
  },
  producer_institution_profile: null,
  available_actions: [{
    action_code: 'create_loan_application',
    label: 'Start Application',
    enabled: true,
    disabled_reason: null,
    required_permission: 'applications.loan_application.create',
  }],
};

const writeState = (
  name: string,
  status: React.ComponentProps<typeof MemberProfileView>['status'],
  profile: MemberProfileDetail | null,
  activeTab: number,
  message = '',
) => {
  const body = renderToStaticMarkup(
    <MemberProfileView
      status={status}
      message={message}
      profile={profile}
      activeTab={activeTab}
      onTabChange={() => undefined}
      onBack={() => undefined}
    />,
  );
  writeFileSync(`${outDir}/${name}.html`, `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="./index.css" />
  <title>${name}</title>
</head>
<body><div id="root">${body}</div></body>
</html>
`);
};

writeState('overview-success', 'success', member, 0);
writeState('deferred-loans-tab', 'success', member, 6);
writeState('unauthorized', 'unauthorized', null, 0, 'Please sign in to continue.');
writeState('error', 'error', null, 0, 'Member could not be loaded.');
