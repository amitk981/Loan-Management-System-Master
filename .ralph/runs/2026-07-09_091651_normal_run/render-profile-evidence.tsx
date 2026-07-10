import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { mkdirSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { MemberProfileView } from '../../../sfpcl-lms/src/pages/members/MemberProfile';
import type { MemberProfileDetail } from '../../../sfpcl-lms/src/services/memberProfileApi';

const output = fileURLToPath(new URL('./evidence/screenshots/profile-details', import.meta.url));
mkdirSync(output, { recursive: true });

const individual: MemberProfileDetail = {
  member_id: 'member-1',
  member_number: 'MEM-00125',
  member_type: 'individual_farmer',
  legal_name: 'Ramesh Patil',
  display_name: 'Ramesh Patil',
  folio_number: 'FOL-456',
  membership_start_date: '2021-04-01',
  membership_status: 'active',
  kyc_status: 'verified',
  rekyc_due_date: null,
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
    first_name: 'Ramesh',
    middle_name: null,
    last_name: 'Patil',
    gender: 'male',
    date_of_birth: '1980-01-15',
    occupation: 'Farmer',
    land_area_under_cultivation_acres: '5.00',
    primary_crop: 'grapes',
    services_availed_flag: true,
    employment_or_service_years: '12.50',
  },
  producer_institution_profile: null,
  available_actions: [],
};

const producer: MemberProfileDetail = {
  ...individual,
  member_id: 'member-2',
  member_number: 'MEM-00126',
  member_type: 'fpc',
  legal_name: 'ABC Farmer Producer Company Limited',
  display_name: 'ABC FPC',
  folio_number: 'FOL-789',
  individual_profile: null,
  producer_institution_profile: {
    institution_type: 'farmer_producer_company',
    registration_number: 'U00000MH2021PTC000000',
    authorised_signatory_name: 'Authorised Person',
    board_resolution_required_flag: true,
    services_availed_flag: true,
    produce_supply_years: '2.00',
  },
};

for (const [name, profile] of [['individual', individual], ['producer', producer]] as const) {
  const body = renderToStaticMarkup(
    <MemberProfileView
      status="success"
      profile={profile}
      activeTab={0}
      onTabChange={() => undefined}
      onBack={() => undefined}
    />,
  );
  writeFileSync(`${output}/${name}.html`, `<!doctype html>
<html><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width" />
<link rel="stylesheet" href="./index.css" /><title>${name} profile</title></head>
<body><div id="root">${body}</div></body></html>`);
}
