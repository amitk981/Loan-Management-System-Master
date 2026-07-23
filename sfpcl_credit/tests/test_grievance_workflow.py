import json
from datetime import timedelta
from django.test import Client, TestCase
from django.utils import timezone
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, MemberScopeAssignment

class GrievanceWorkflowApiTests(TestCase):
    password = 'GrievancePass123!'

    def setUp(self):
        self.client = Client()
        self.field_role = Role.objects.create(role_code='field_officer', role_name='Field Officer')
        self.cs_role = Role.objects.create(role_code='company_secretary', role_name='Company Secretary')
        self.field_officer = self._user(self.field_role, 'grievance-field@example.test')
        self.company_secretary = self._user(self.cs_role, 'grievance-cs@example.test')
        self._grant(self.field_role, 'compliance.grievance.create')
        self._grant(self.cs_role, 'compliance.grievance.create', 'compliance.grievance.read', 'compliance.grievance.assign', 'compliance.grievance.resolve')
        self.member = self._member('GRV-001')
        for user, permission in ((self.field_officer, 'compliance.grievance.create'), (self.company_secretary, 'compliance.grievance.create'), (self.company_secretary, 'compliance.grievance.read'), (self.company_secretary, 'compliance.grievance.assign'), (self.company_secretary, 'compliance.grievance.resolve')):
            MemberScopeAssignment.objects.create(user=user, permission_code=permission, scope_type='assigned', member=self.member)
        self.application = LoanApplication.objects.create(member=self.member, borrower_type=self.member.member_type, received_by_user=self.field_officer, created_by_user=self.field_officer)
        self.document = DocumentFile.objects.create(file_name='grievance-form.pdf', storage_provider='local', storage_key=f'governed/grievances/{self.member.pk}/grievance-form.pdf', uploaded_by_user=self.field_officer, sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED)
        self._govern_document(self.document, self.member)
        self.field_auth = self._auth(self.field_officer)

    def test_authorised_create_generates_one_scoped_reference_and_initial_evidence(self):
        today = timezone.localdate()
        payload = {'member_id': str(self.member.pk), 'loan_application_id': str(self.application.pk), 'grievance_category': 'application_issue', 'description': 'The member needs an application status correction.', 'received_date': today.isoformat(), 'received_channel': 'form', 'assigned_to_user_id': str(self.company_secretary.pk), 'resolution_due_date': (today + timedelta(days=7)).isoformat(), 'supporting_document_ids': [str(self.document.pk)]}
        headers = {**self.field_auth, 'HTTP_IDEMPOTENCY_KEY': 'grievance-create-001'}
        created = self.client.post('/api/v1/grievances/', data=json.dumps(payload), content_type='application/json', **headers)
        replay = self.client.post('/api/v1/grievances/', data=json.dumps(payload), content_type='application/json', **headers)
        self.assertEqual(created.status_code, 200, created.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        data = created.json()['data']
        self.assertRegex(data['grievance_reference'], '^GRV-\\d{4}-[A-F0-9]{12}$')
        self.assertEqual(replay.json()['data']['grievance_id'], data['grievance_id'])
        self.assertEqual(data['member_id'], str(self.member.pk))
        self.assertEqual(data['loan_application_id'], str(self.application.pk))
        self.assertEqual(data['status'], 'open')
        self.assertEqual(data['tat_days'], 7)
        self.assertFalse(data['is_overdue'])
        self.assertEqual(data['supporting_document_ids'], [str(self.document.pk)])
        self.assertEqual(data['history'][0]['new_status'], 'open')
        from sfpcl_credit.compliance.models import Grievance
        self.assertEqual(Grievance.objects.count(), 1)
        grievance = Grievance.objects.get()
        self.assertEqual(grievance.supporting_documents.count(), 1)
        self.assertTrue(AuditLog.objects.filter(action='compliance.grievance.created', entity_id=grievance.pk).exists())

    def test_staff_reads_are_member_scoped_and_borrower_projection_is_safe(self):
        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
        from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceDenied
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        today = timezone.localdate()
        own = self._grievance('GRV-2026-OWN000000001', loan_application=self.application, grievance_category='application_issue', description='Own complaint', received_channel='form', internal_notes='Internal investigation note')
        own.history.update(note='Internal history note')
        foreign_member = self._member('GRV-FOREIGN')
        self._grievance('GRV-2026-FOR000000001', member=foreign_member, description='Foreign complaint', internal_notes='Foreign confidential note')
        cs_auth = self._auth(self.company_secretary)
        listed = self.client.get('/api/v1/grievances/', {'status': 'open', 'member_id': str(self.member.pk)}, **cs_auth)
        detail = self.client.get(f'/api/v1/grievances/{own.pk}/', **cs_auth)
        borrower_portal = self._portal(self.member, 'read-borrower@example.test')
        borrower = GrievanceWorkflow.retrieve_for_borrower(portal_account=borrower_portal, grievance_id=own.pk)
        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(listed.json()['pagination']['total_count'], 1)
        self.assertEqual(listed.json()['data'][0]['grievance_id'], str(own.pk))
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()['data']['internal_notes'], 'Internal investigation note')
        self.assertEqual(borrower['grievance_id'], str(own.pk))
        self.assertEqual(borrower['status'], 'open')
        self.assertNotIn('internal_notes', borrower)
        self.assertNotIn('assigned_to_user_id', borrower)
        self.assertNotIn('history', borrower)
        self.assertNotIn('supporting_document_ids', borrower)
        with self.assertRaises(ComplianceDenied):
            GrievanceWorkflow.retrieve_for_borrower(portal_account=self._portal(foreign_member, 'foreign-borrower@example.test'), grievance_id=own.pk)

    def test_active_portal_primitive_creates_only_for_its_own_member(self):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceInvalid
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        from sfpcl_credit.identity.models import PortalAccount
        borrower_role = Role.objects.create(role_code='borrower', role_name='Borrower')
        borrower = self._user(borrower_role, 'grievance-borrower@example.test')
        portal = PortalAccount.objects.create(member=self.member, user=borrower, status=PortalAccount.STATUS_ACTIVE, activated_at=timezone.now())
        payload = {'grievance_category': 'other', 'description': 'Portal complaint.', 'received_date': timezone.localdate().isoformat(), 'received_channel': 'portal', 'assigned_to_user_id': str(self.company_secretary.pk), 'resolution_due_date': (timezone.localdate() + timedelta(days=7)).isoformat(), 'supporting_document_ids': []}
        created = GrievanceWorkflow.create_for_borrower(portal_account=portal, payload=payload, idempotency_key='portal-grievance-001')
        self.assertEqual(created['status'], 'open')
        self.assertNotIn('member_id', created)
        with self.assertRaises(ComplianceInvalid):
            GrievanceWorkflow.create_for_borrower(portal_account=portal, payload={**payload, 'member_id': str(self._member('GRV-PORTAL-FOREIGN').pk)}, idempotency_key='portal-grievance-002')

    def test_cs_assignment_and_owner_investigation_are_monotonic_and_historic(self):
        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
        owner_role = Role.objects.create(role_code='credit_manager', role_name='Credit Manager')
        owner = self._user(owner_role, 'grievance-owner@example.test')
        self._grant(owner_role, 'compliance.grievance.read', 'compliance.grievance.update', 'compliance.grievance.resolve')
        for permission in ('compliance.grievance.read', 'compliance.grievance.update', 'compliance.grievance.resolve'):
            MemberScopeAssignment.objects.create(user=owner, permission_code=permission, scope_type='assigned', member=self.member)
        grievance = self._grievance('GRV-2026-ASSIGN000001', grievance_category='interest_charge_dispute', description='Interest charge needs review.')
        url = f'/api/v1/grievances/{grievance.pk}/'
        assigned = self.client.patch(url, data=json.dumps({'assigned_to_user_id': str(owner.pk)}), content_type='application/json', **self._auth(self.company_secretary))
        investigated = self.client.patch(url, data=json.dumps({'status': 'investigating', 'internal_notes': 'Invoice calculation is being reconciled.'}), content_type='application/json', **self._auth(owner))
        backward = self.client.patch(url, data=json.dumps({'status': 'open'}), content_type='application/json', **self._auth(owner))
        self.assertEqual(assigned.status_code, 200, assigned.content)
        self.assertEqual(assigned.json()['data']['assigned_to_user_id'], str(owner.pk))
        self.assertEqual(investigated.status_code, 200, investigated.content)
        self.assertEqual(investigated.json()['data']['status'], 'investigating')
        self.assertEqual(backward.status_code, 409, backward.content)
        grievance.refresh_from_db()
        self.assertEqual(grievance.status, Grievance.STATUS_INVESTIGATING)
        self.assertEqual(list(grievance.history.order_by('sequence').values_list('event_type', 'previous_status', 'new_status')), [('created', '', 'open'), ('assigned', 'open', 'open'), ('updated', 'open', 'investigating')])
        self.assertEqual(AuditLog.objects.filter(entity_id=grievance.pk, action__in=('compliance.grievance.assigned', 'compliance.grievance.updated')).count(), 2)

    def test_resolution_requires_summary_is_retry_safe_and_queues_honest_notice(self):
        from sfpcl_credit.communications.models import Communication, CommunicationDeliveryJob, ContentTemplate
        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
        today = timezone.localdate()
        ContentTemplate.objects.create(template_code='grievance_resolution_email', template_name='Grievance resolution', template_type='email', language_code='en', audience='borrower', subject_template='Grievance {{grievance_reference}} resolved', body_template='Dear {{member_name}}, grievance {{grievance_reference}} was resolved: {{resolution_summary}}', variables_json=['grievance_reference', 'member_name', 'resolution_summary'], approval_status=ContentTemplate.STATUS_APPROVED, template_version='1.0', effective_from=today)
        resolution_document = DocumentFile.objects.create(file_name='grievance-resolution.pdf', storage_provider='local', storage_key=f'governed/grievances/{self.member.pk}/resolution.pdf', uploaded_by_user=self.company_secretary, sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED)
        self._govern_document(resolution_document, self.member)
        grievance = self._grievance('GRV-2026-RESOLVE00001', grievance_category='document_issue', description='Document status requires clarification.', received_channel='form')
        url = f'/api/v1/grievances/{grievance.pk}/resolve/'
        auth = self._auth(self.company_secretary)
        missing = self.client.post(url, data=json.dumps({'resolution_summary': '   '}), content_type='application/json', **auth, HTTP_IDEMPOTENCY_KEY='grievance-resolution-001')
        payload = {'resolution_summary': 'The document status was corrected and confirmed.', 'resolution_document_id': str(resolution_document.pk), 'borrower_acknowledgement': 'Member confirmed receipt of the explanation.'}
        resolved = self.client.post(url, data=json.dumps(payload), content_type='application/json', **auth, HTTP_IDEMPOTENCY_KEY='grievance-resolution-001')
        replay = self.client.post(url, data=json.dumps(payload), content_type='application/json', **auth, HTTP_IDEMPOTENCY_KEY='grievance-resolution-001')
        post_close_edit = self.client.patch(f'/api/v1/grievances/{grievance.pk}/', data=json.dumps({'internal_notes': 'Late edit'}), content_type='application/json', **auth)
        self.assertEqual(missing.status_code, 400, missing.content)
        self.assertEqual(resolved.status_code, 200, resolved.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        data = resolved.json()['data']
        self.assertEqual(data['status'], 'resolved')
        self.assertEqual(data['resolution_document_id'], str(resolution_document.pk))
        self.assertEqual(data['notice_delivery_status'], 'queued')
        self.assertFalse(data['borrower_informed'])
        self.assertTrue(data['borrower_acknowledged'])
        self.assertEqual(data['borrower_acknowledgement'], 'Member confirmed receipt of the explanation.')
        self.assertEqual(replay.json()['data']['notice_communication_id'], data['notice_communication_id'])
        self.assertEqual(post_close_edit.status_code, 409, post_close_edit.content)
        grievance.refresh_from_db()
        self.assertIsNotNone(grievance.closed_at)
        self.assertEqual(grievance.history.filter(event_type='resolved').count(), 1)
        self.assertEqual(Communication.objects.filter(related_entity_type='grievance', related_entity_id=grievance.pk).count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)
        communication = Communication.objects.get(related_entity_id=grievance.pk)
        communication.sent_at = timezone.now()
        communication.delivery_status = 'sent'
        communication.save(update_fields=['sent_at', 'delivery_status'])
        CommunicationDeliveryJob.objects.update(status=CommunicationDeliveryJob.STATUS_SENT)
        informed = self.client.get(f'/api/v1/grievances/{grievance.pk}/', **auth)
        self.assertTrue(informed.json()['data']['borrower_informed'])

    def test_service_resolution_without_http_request_retains_blank_transport_audit(self):
        from sfpcl_credit.communications.models import ContentTemplate
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        today = timezone.localdate()
        ContentTemplate.objects.create(template_code='grievance_resolution_email', template_name='Grievance resolution', template_type='email', language_code='en', audience='borrower', subject_template='Grievance {{grievance_reference}} resolved', body_template='Dear {{member_name}}, grievance {{grievance_reference}} was resolved: {{resolution_summary}}', variables_json=['grievance_reference', 'member_name', 'resolution_summary'], approval_status=ContentTemplate.STATUS_APPROVED, template_version='1.0', effective_from=today)
        grievance = self._grievance('GRV-2026-SERVICE00001')

        resolved = GrievanceWorkflow.resolve(
            actor=self.company_secretary,
            grievance_id=grievance.pk,
            payload={'resolution_summary': 'The service-owned resolution was retained.'},
            idempotency_key='grievance-service-resolution-001',
        )

        self.assertEqual(resolved['status'], 'resolved')
        communication_audit = AuditLog.objects.get(
            action='communications.communication.created',
            entity_id=resolved['notice_communication_id'],
        )
        self.assertEqual(communication_audit.ip_address, '')
        self.assertEqual(communication_audit.user_agent, '')

    def test_scheduler_escalates_overdue_and_recovery_cases_once_without_resolving(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        from sfpcl_credit.tests.test_loan_schedule_ledger_api import LoanScheduleLedgerApiTests
        today = timezone.localdate()
        overdue = self._grievance('GRV-2026-OVERDUE0001', description='Overdue complaint.', received_date=today - timedelta(days=10), resolution_due_date=today - timedelta(days=1))
        account_fixture = LoanScheduleLedgerApiTests('test_authorised_reader_gets_ordered_decimal_schedule_truth')
        account_fixture.setUp()
        account = account_fixture.account
        recovery = self._grievance('GRV-2026-RECOVERY001', member=account.member, loan_account=account, grievance_category='recovery_conduct_issue', description='Recovery interaction conduct complaint.', received_channel='form', status=Grievance.STATUS_INVESTIGATING, internal_notes='Restricted recovery investigation.')
        first = GrievanceWorkflow.process_escalations(as_of_date=today)
        replay = GrievanceWorkflow.process_escalations(as_of_date=today)
        overdue.refresh_from_db()
        recovery.refresh_from_db()
        self.assertEqual(first.escalated_count, 2)
        self.assertEqual(replay.escalated_count, 0)
        self.assertEqual(overdue.status, Grievance.STATUS_ESCALATED)
        self.assertEqual(recovery.status, Grievance.STATUS_ESCALATED)
        self.assertIsNone(overdue.closed_at)
        self.assertIsNone(recovery.closed_at)
        self.assertEqual(overdue.escalation_count, 1)
        self.assertEqual(recovery.escalation_count, 1)
        recovery_event = recovery.history.get(event_type='escalated')
        self.assertTrue(recovery_event.evidence_json['fair_practice_attention'])
        self.assertEqual(recovery_event.evidence_json['loan_account_id'], str(account.pk))
        self.assertNotIn('Restricted recovery investigation.', json.dumps(GrievanceWorkflow.retrieve_for_borrower(portal_account=self._portal(account.member, 'recovery-borrower@example.test'), grievance_id=recovery.pk)))
        self.assertEqual(Notification.objects.filter(notification_type='grievance_escalated').count(), 2)
        self.assertEqual(AuditLog.objects.filter(action='compliance.grievance.escalated').count(), 2)

    def test_011k_compliance_job_invokes_grievance_escalation_owner(self):
        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
        from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
        today = timezone.localdate()
        grievance = self._grievance('GRV-2026-011K0000001', description='Complaint awaiting the 011K escalation job.', received_date=today - timedelta(days=5), resolution_due_date=today - timedelta(days=1))
        ComplianceTaskEngine.generate_due_tasks(as_of_date=today)
        grievance.refresh_from_db()
        self.assertEqual(grievance.status, Grievance.STATUS_ESCALATED)
        self.assertEqual(grievance.history.filter(event_type='escalated').count(), 1)

    def test_create_failures_reject_changed_replay_foreign_sources_and_audit_scope_denial(self):
        from sfpcl_credit.compliance.models import Grievance, GrievanceDocument
        today = timezone.localdate()
        payload = {'member_id': str(self.member.pk), 'loan_application_id': str(self.application.pk), 'grievance_category': 'application_issue', 'description': 'Original complaint facts.', 'received_date': today.isoformat(), 'received_channel': 'form', 'assigned_to_user_id': str(self.company_secretary.pk), 'resolution_due_date': (today + timedelta(days=7)).isoformat(), 'supporting_document_ids': [str(self.document.pk)]}
        created = self.client.post('/api/v1/grievances/', data=json.dumps(payload), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='negative-create-001')
        changed = self.client.post('/api/v1/grievances/', data=json.dumps({**payload, 'description': 'Changed complaint facts.'}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='negative-create-001')
        foreign_member = self._member('GRV-DENIED')
        denied = self.client.post('/api/v1/grievances/', data=json.dumps({**payload, 'member_id': str(foreign_member.pk)}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='negative-create-002')
        foreign_document = DocumentFile.objects.create(file_name='foreign-grievance.pdf', storage_provider='local', storage_key=f'governed/grievances/{foreign_member.pk}/foreign.pdf', uploaded_by_user=self.field_officer, sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED)
        self._govern_document(foreign_document, foreign_member)
        foreign_grievance = self._grievance('GRV-2026-FOREIGNDOC01', member=foreign_member, description='Foreign grievance document owner.', received_channel='form')
        GrievanceDocument.objects.create(grievance=foreign_grievance, document=foreign_document, member=foreign_member, purpose=GrievanceDocument.PURPOSE_SUPPORTING, linked_by_user=self.field_officer)
        foreign_evidence = self.client.post('/api/v1/grievances/', data=json.dumps({**payload, 'supporting_document_ids': [str(foreign_document.pk)]}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='negative-create-003')
        self.assertEqual(created.status_code, 200, created.content)
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(foreign_evidence.status_code, 403, foreign_evidence.content)
        self.assertEqual(Grievance.objects.exclude(pk=foreign_grievance.pk).count(), 1)
        self.assertTrue(AuditLog.objects.filter(action='compliance.grievance.access_denied', actor_user=self.field_officer, new_value_json__path='/api/v1/grievances/').exists())
        self.assertEqual(AuditLog.objects.filter(action='compliance.grievance.access_denied', actor_user=self.field_officer, new_value_json__path='/api/v1/grievances/').count(), 2)

    def test_governed_grievance_document_download_is_scoped_and_audited(self):
        today = timezone.localdate()
        created = self.client.post('/api/v1/grievances/', data=json.dumps({'member_id': str(self.member.pk), 'grievance_category': 'document_issue', 'description': 'Document evidence requires review.', 'received_date': today.isoformat(), 'received_channel': 'form', 'assigned_to_user_id': str(self.company_secretary.pk), 'resolution_due_date': (today + timedelta(days=7)).isoformat(), 'supporting_document_ids': [str(self.document.pk)]}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='download-fixture')
        grievance_id = created.json()['data']['grievance_id']
        url = f'/api/v1/grievances/{grievance_id}/documents/{self.document.pk}/download/'
        downloaded = self.client.get(url, **self._auth(self.company_secretary))
        unscoped_cs = self._user(self.cs_role, 'unscoped-grievance-cs@example.test')
        denied = self.client.get(url, **self._auth(unscoped_cs))
        self.assertEqual(downloaded.status_code, 200, downloaded.content)
        self.assertIn('download_url', downloaded.json()['data'])
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertTrue(AuditLog.objects.filter(action='compliance.grievance.document_downloaded', actor_user=self.company_secretary, entity_id=grievance_id, new_value_json__document_id=str(self.document.pk)).exists())
        self.assertTrue(AuditLog.objects.filter(action='compliance.grievance.access_denied', actor_user=unscoped_cs).exists())

    def test_borrower_scope_is_derived_and_safe_for_create_and_retrieve(self):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceDenied
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        from sfpcl_credit.identity.models import PortalAccount
        borrower_role = Role.objects.create(role_code='borrower', role_name='Borrower')
        borrower = self._user(borrower_role, 'safe-borrower@example.test')
        portal = PortalAccount.objects.create(member=self.member, user=borrower, status=PortalAccount.STATUS_ACTIVE, activated_at=timezone.now())
        payload = {'grievance_category': 'other', 'description': 'Safe portal complaint.', 'received_date': timezone.localdate().isoformat(), 'received_channel': 'portal', 'assigned_to_user_id': str(self.company_secretary.pk), 'resolution_due_date': (timezone.localdate() + timedelta(days=7)).isoformat(), 'supporting_document_ids': []}
        created = GrievanceWorkflow.create_for_borrower(portal_account=portal, payload=payload, idempotency_key='safe-portal-create')
        retrieved = GrievanceWorkflow.retrieve_for_borrower(portal_account=portal, grievance_id=created['grievance_id'])
        for projection in (created, retrieved):
            self.assertNotIn('assigned_to_user_id', projection)
            self.assertNotIn('history', projection)
            self.assertNotIn('supporting_document_ids', projection)
            self.assertNotIn('available_actions', projection)
        portal.status = PortalAccount.STATUS_SUSPENDED
        portal.save(update_fields=['status'])
        with self.assertRaises(ComplianceDenied):
            GrievanceWorkflow.retrieve_for_borrower(portal_account=portal, grievance_id=created['grievance_id'])

    def test_unproven_document_and_inconsistent_notice_truth_are_rejected(self):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceDenied
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        unproven = DocumentFile.objects.create(file_name='unproven.pdf', storage_provider='local', storage_key='unproven.pdf', uploaded_by_user=self.field_officer, sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED)
        with self.assertRaises(ComplianceDenied):
            GrievanceWorkflow._documents([str(unproven.pk)], member=self.member)
        grievance = self._grievance('GRV-2026-NOTICETRUTH')
        communication = Communication.objects.create(related_entity_type='grievance', related_entity_id=grievance.pk, recipient_party_type='member', recipient_party_id=self.member.pk, recipient_address=self.member.email, channel='email', body_snapshot='failed', sent_at=timezone.now(), delivery_status='failed')
        grievance.notice_communication = communication
        grievance.save(update_fields=['notice_communication'])
        self.assertFalse(GrievanceWorkflow._borrower_informed(grievance))

    def test_category_and_required_field_contracts_and_wrong_role_fail_closed(self):
        from types import SimpleNamespace
        from sfpcl_credit.compliance.models import Grievance
        from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceInvalid
        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
        today = timezone.localdate()
        base = {'member_id': str(self.member.pk), 'grievance_category': 'other', 'description': 'Complete complaint.', 'received_date': today.isoformat(), 'received_channel': 'form', 'assigned_to_user_id': str(self.company_secretary.pk), 'resolution_due_date': (today + timedelta(days=7)).isoformat(), 'supporting_document_ids': []}
        for index, field in enumerate(('grievance_category', 'description', 'assigned_to_user_id')):
            response = self.client.post('/api/v1/grievances/', data=json.dumps({key: value for key, value in base.items() if key != field}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY=f'missing-required-{index}')
            self.assertEqual(response.status_code, 400, response.content)
        for index, category in enumerate(sorted(Grievance.CATEGORIES - {'recovery_conduct_issue'})):
            response = self.client.post('/api/v1/grievances/', data=json.dumps({**base, 'grievance_category': category}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY=f'category-{index}')
            self.assertEqual(response.status_code, 200, response.content)
        nonexistent = self.client.post('/api/v1/grievances/', data=json.dumps({**base, 'loan_application_id': '00000000-0000-0000-0000-000000000001'}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='missing-source')
        self.assertEqual(nonexistent.status_code, 400, nonexistent.content)
        with self.assertRaises(ComplianceInvalid):
            GrievanceWorkflow._validate_source_chain(member=self.member, application=None, loan_account=None, default_case=SimpleNamespace(loan_account_id='loan-a'), recovery_action=SimpleNamespace(loan_account_id='loan-b'), category='recovery_conduct_issue')
        with self.assertRaises(ComplianceInvalid):
            GrievanceWorkflow._validate_source_chain(member=self.member, application=None, loan_account=SimpleNamespace(pk='loan-a'), default_case=None, recovery_action=None, category='recovery_conduct_issue')
        grievance = self._grievance('GRV-2026-WRONGROLE001')
        wrong_role = self.client.post(f'/api/v1/grievances/{grievance.pk}/resolve/', data=json.dumps({'resolution_summary': 'Unauthorised resolution.'}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='wrong-role-resolution')
        self.assertEqual(wrong_role.status_code, 403, wrong_role.content)

    @staticmethod
    def _govern_document(document, member):
        AuditLog.objects.create(actor_user=document.uploaded_by_user, actor_type='user', action='documents.file.uploaded', entity_type='document_file', entity_id=document.pk, new_value_json={'document_id': str(document.pk), 'file_name': document.file_name, 'file_extension': document.file_extension, 'mime_type': document.mime_type, 'file_size_bytes': document.file_size_bytes, 'storage_provider': document.storage_provider, 'storage_key': document.storage_key, 'checksum_sha256': document.checksum_sha256, 'sensitivity_level': document.sensitivity_level, 'document_category': 'grievance_evidence', 'related_entity_type': 'member', 'related_entity_id': str(member.pk)})

    def _user(self, role, email):
        user = User.objects.create(full_name=role.role_name, email=email, primary_role=role, password_hash='')
        user.set_password(self.password)
        user.save(update_fields=['password_hash'])
        return user

    def _portal(self, member, email):
        from sfpcl_credit.identity.models import PortalAccount
        role, _created = Role.objects.get_or_create(role_code='borrower', defaults={'role_name': 'Borrower'})
        return PortalAccount.objects.create(member=member, user=self._user(role, email), status=PortalAccount.STATUS_ACTIVE, activated_at=timezone.now())

    @staticmethod
    def _grant(role, *codes):
        for code in codes:
            permission, _created = Permission.objects.get_or_create(permission_code=code, defaults={'permission_name': code, 'module_name': 'compliance', 'risk_level': Permission.RISK_HIGH})
            RolePermission.objects.get_or_create(role=role, permission=permission)

    def _auth(self, user):
        response = self.client.post('/api/v1/auth/login/', {'email': user.email, 'password': self.password}, content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        return {'HTTP_AUTHORIZATION': f"Bearer {response.json()['data']['access_token']}"}

    def _grievance(self, reference, *, member=None, **overrides):
        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
        today = timezone.localdate()
        values = {'grievance_reference': reference, 'idempotency_key': f'fixture-{reference}', 'request_digest': '0' * 64, 'member': member or self.member, 'grievance_category': 'other', 'description': 'Grievance fixture.', 'received_date': today, 'received_channel': 'phone', 'assigned_to_user': self.company_secretary, 'resolution_due_date': today + timedelta(days=7), 'status': Grievance.STATUS_OPEN, 'created_by_user': self.field_officer, 'created_by_role_code': self.field_role.role_code}
        values.update(overrides)
        grievance = Grievance.objects.create(**values)
        GrievanceHistory.objects.create(grievance=grievance, sequence=1, event_type='created', new_status=grievance.status, actor_user=self.field_officer, actor_role_code=self.field_role.role_code)
        return grievance

    @staticmethod
    def _member(folio):
        return Member.objects.create(member_type='individual_farmer', legal_name=f'Grievance Member {folio}', display_name=f'Grievance Member {folio}', folio_number=folio, membership_status='active', pan_encrypted=f'encrypted-{folio}', pan_hash=f'hash-{folio}', kyc_status='verified', default_status='no_default', email=f'{folio.lower()}@example.test')
