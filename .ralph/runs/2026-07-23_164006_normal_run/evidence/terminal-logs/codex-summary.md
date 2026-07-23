# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 31895306
Lines: 648470
SHA-256: 65e7de2343839de4410eb69c30e2341e68757f55ad66403a262cc6d6e76513b0
Session ID: 019f8eab-62eb-7ba0-afca-97c5f6d6b662
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            GrievanceWorkflow._validate_source_chain(member=self.member, application=None, loan_account=None, default_case=SimpleNamespace(loan_account_id='loan-a'), recovery_action=SimpleNamespace(loan_account_id='loan-b'), category='recovery_conduct_issue')
+        with self.assertRaises(ComplianceInvalid):
+            GrievanceWorkflow._validate_source_chain(member=self.member, application=None, loan_account=SimpleNamespace(pk='loan-a'), default_case=None, recovery_action=None, category='recovery_conduct_issue')
+        grievance = self._grievance('GRV-2026-WRONGROLE001')
+        wrong_role = self.client.post(f'/api/v1/grievances/{grievance.pk}/resolve/', data=json.dumps({'resolution_summary': 'Unauthorised resolution.'}), content_type='application/json', **self.field_auth, HTTP_IDEMPOTENCY_KEY='wrong-role-resolution')
+        self.assertEqual(wrong_role.status_code, 403, wrong_role.content)
+
+    @staticmethod
+    def _govern_document(document, member):
+        AuditLog.objects.create(actor_user=document.uploaded_by_user, actor_type='user', action='documents.file.uploaded', entity_type='document_file', entity_id=document.pk, new_value_json={'document_id': str(document.pk), 'file_name': document.file_name, 'file_extension': document.file_extension, 'mime_type': document.mime_type, 'file_size_bytes': document.file_size_bytes, 'storage_provider': document.storage_provider, 'storage_key': document.storage_key, 'checksum_sha256': document.checksum_
+
+    def _user(self, role, email):
+        user = User.objects.create(full_name=role.role_name, email=email, primary_role=role, password_hash='')
+        user.set_password(self.password)
+        user.save(update_fields=['password_hash'])
+        return user
+
+    def _portal(self, member, email):
+        from sfpcl_credit.identity.models import PortalAccount
+        role, _created = Role.objects.get_or_create(role_code='borrower', defaults={'role_name': 'Borrower'})
+        return PortalAccount.objects.create(member=member, user=self._user(role, email), status=PortalAccount.STATUS_ACTIVE, activated_at=timezone.now())
+
+    @staticmethod
+    def _grant(role, *codes):
+        for code in codes:
+            permission, _created = Permission.objects.get_or_create(permission_code=code, defaults={'permission_name': code, 'module_name': 'compliance', 'risk_level': Permission.RISK_HIGH})
+            RolePermission.objects.get_or_create(role=role, permission=permission)
+
+    def _auth(self, user):
+        response = self.client.post('/api/v1/auth/login/', {'email': user.email, 'password': self.password}, content_type='application/json')
+        self.assertEqual(response.status_code, 200, response.content)
+        return {'HTTP_AUTHORIZATION': f"Bearer {response.json()['data']['access_token']}"}
+
+    def _grievance(self, reference, *, member=None, **overrides):
+        from sfpcl_credit.compliance.models import Grievance, GrievanceHistory
+        today = timezone.localdate()
+        values = {'grievance_reference': reference, 'idempotency_key': f'fixture-{reference}', 'request_digest': '0' * 64, 'member': member or self.member, 'grievance_category': 'other', 'description': 'Grievance fixture.', 'received_date': today, 'received_channel': 'phone', 'assigned_to_user': self.company_secretary, 'resolution_due_date': today + timedelta(days=7), 'status': Grievance.STATUS_OPEN, 'created_by_user': self.field_officer, 'created_by_role_code': self.field_role.role_code}
+        values.update(overrides)
+        grievance = Grievance.objects.create(**values)
+        GrievanceHistory.objects.create(grievance=grievance, sequence=1, event_type='created', new_status=grievance.status, actor_user=self.field_officer, actor_role_code=self.field_role.role_code)
+        return grievance
+
+    @staticmethod
+    def _member(folio):
+        return Member.objects.create(member_type='individual_farmer', legal_name=f'Grievance Member {folio}', display_name=f'Grievance Member {folio}', folio_number=folio, membership_status='active', pan_encrypted=f'encrypted-{folio}', pan_hash=f'hash-{folio}', kyc_status='verified', default_status='no_default', email=f'{folio.lower()}@example.test')

tokens used
600,290
Implemented slice `011N-grievance-workflow` and marked it **Ready for independent validation**.

Delivered:

- Grievance persistence, migration, generated references, governed evidence, and append-only history.
- Staff create/list/detail/update/assign/resolve/download APIs with permission and member-scope enforcement.
- Active-portal borrower creation and safe self-scoped retrieval.
- Explicit owner and due-date handling with server-derived TAT and overdue state.
- Idempotent resolution and honest communication-delivery truth.
- Retry-safe 011K escalation, including recovery-action fair-practice log linkage.
- Two declared PostgreSQL concurrency acceptance tests.
- Catalogue permissions, API contract documentation, and assumption A-166.

Validation completed:

- Final grievance acceptance: **12 passed**
- Grievance/catalogue pack: **27 passed**
- Reverse-consumer pack: **57 passed**, 12 PostgreSQL-only skips
- Django system check: clean
- Migration drift: none
- PostgreSQL acceptance class: exactly **2 tests discovered**; trusted PostgreSQL execution remains with Ralph
- Protected files: unchanged
- Product diff: below the 2,000-line cap
- No git add, commit, or push performed

Artifacts:

- [Review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_164006_normal_run/review-packet.md)
- [Risk assessment](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_164006_normal_run/risk-assessment.md)
- [Final summary](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_164006_normal_run/final-summary.md)
- [API evidence](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_164006_normal_run/evidence/api-responses/grievance-contract.md)
- [Final acceptance log](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/23-final-acceptance-green.log)
