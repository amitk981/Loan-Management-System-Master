import ast
from pathlib import Path
from django.test import SimpleTestCase
ROOT = Path(__file__).resolve().parents[1]

class StaffDocumentationWorkspaceDesignTests(SimpleTestCase):

    def test_public_coordinator_is_shallow_and_uses_bounded_owner_seams(self):
        source = (ROOT / 'processes' / 'staff_documentation_workspace.py').read_text()
        self.assertIn('staff_documentation_queue', source)
        self.assertIn('legal_workspace_actions', source)
        self.assertIn('application_workspace_actions', source)
        self.assertIn('security_workspace_actions', source)
        self.assertNotIn('__class__.__name__', source)
        self.assertNotIn('def _dispatch_action', source)
        self.assertNotIn('owner_url', source)

    def test_queue_selector_pages_before_projection_and_never_locks_the_queue(self):
        source = (ROOT / 'processes' / 'staff_documentation_queue.py').read_text()
        self.assertNotIn('select_for_update', source)
        self.assertIn('Paginator', source)
        self.assertIn('projector(', source)
        self.assertIn('scope_post_sanction_checklists', source)
        self.assertNotIn('ApprovalCaseReadScopeGrant', source)
        self.assertNotIn('company_secretary', source)

    def test_owner_boundary_does_not_infer_authority_from_exception_names(self):
        source = (ROOT / 'processes' / 'staff_documentation_workspace.py').read_text()
        self.assertNotIn('__class__.__name__', source)
        self.assertNotIn('_uuid_from_owner_url', source)
        self.assertNotIn('def _dispatch_action', source)
        self.assertNotIn('command["action_code"]', source)
        for owner_implementation in ('def _execute_generation', 'def _execute_signature', 'def _execute_stamp', 'def _execute_bank_verification', 'def _execute_security_create', 'DocumentTemplate.objects', 'SignatureRecord.objects', 'StampDutyRecord.objects', 'Shareholding.objects', 'request_contracts'):
            self.assertNotIn(owner_implementation, source)

    def test_security_decisions_and_execution_are_owned_by_security_module(self):
        source = (ROOT / 'processes' / 'staff_documentation_workspace.py').read_text()
        tree = ast.parse(source)
        imported_modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        self.assertIn('sfpcl_credit.security_instruments.modules', imported_modules)
        self.assertNotIn('sfpcl_credit.security_instruments.request_contracts', imported_modules)
        self.assertNotIn('def _security_create_action', source)
        self.assertNotIn('def _execute_security_create', source)
        self.assertNotIn('Shareholding.objects', source)
        self.assertNotIn('PowerOfAttorneyRequest', source)
        owner_source = (ROOT / 'security_instruments' / 'modules' / 'staff_workspace_actions.py').read_text()
        self.assertIn('def project_workflows', owner_source)
        self.assertIn('def _execute_security_create', owner_source)
        self.assertIn('OwnerConflict', owner_source)
        self.assertNotIn('sfpcl_credit.legal_documents', owner_source)
        self.assertNotIn('sfpcl_credit.processes', owner_source)

    def test_each_action_family_issues_an_owner_bound_execute_contract(self):
        coordinator = (ROOT / 'processes' / 'staff_documentation_workspace.py').read_text()
        owner_modules = {'legal': ROOT / 'legal_documents' / 'modules' / 'staff_workspace_actions.py', 'bank': ROOT / 'applications' / 'modules' / 'staff_workspace_actions.py', 'security': ROOT / 'security_instruments' / 'modules' / 'staff_workspace_actions.py'}
        for family, path in owner_modules.items():
            with self.subTest(family=family):
                source = path.read_text()
                self.assertIn('_owner_execute', source)
                self.assertIn('partial(', source)
                self.assertIn('OwnerConflict', source)
                self.assertNotIn('from sfpcl_credit.processes', source)
        self.assertNotIn('owner_url', coordinator)
        self.assertNotIn('def _execute_', coordinator)
