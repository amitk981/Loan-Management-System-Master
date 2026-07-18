from pathlib import Path

from django.db import connection, migrations, models
from django.db.migrations.operations.base import Operation
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase, TransactionTestCase

from sfpcl_credit.legal_documents.migration_state_guard import (
    LEGAL_CHECKLIST_STATE_ALLOWLIST,
    _CHECKLIST_KEY,
    _HISTORICAL_MODULE,
    _HISTORICAL_PATH,
    _apply_operation_state,
    _is_retained_transition,
    legal_checklist_state_ownership_violations,
)


class ImportedChecklistMutation(Operation):
    def state_forwards(self, app_label, state):
        state.models[("legal_documents", "documentchecklist")].options.clear()


class InheritedChecklistMutation(ImportedChecklistMutation):
    pass


def mutate_checklist_through_helper(state):
    state.models[("legal_documents", "documentchecklist")].options.clear()


class HelperChecklistMutation(Operation):
    def state_forwards(self, app_label, state):
        mutate_checklist_through_helper(state)


class LegalChecklistMigrationAnchorTests(SimpleTestCase):
    boundary = [
        ("applications", "0016_bankverificationdecision_and_more"),
        ("legal_documents", "0012_portal_documentation_submission"),
    ]
    anchored = [
        ("legal_documents", "0013_application_evidence_state_anchor"),
    ]

    def test_anchor_owns_cross_app_checklist_state_without_duplicate_columns(self):
        loader = MigrationLoader(None)
        before = loader.project_state(self.boundary)
        state = loader.project_state(self.anchored)
        before_action = before.apps.get_model("legal_documents", "ChecklistAction")
        action = state.apps.get_model("legal_documents", "ChecklistAction")

        self.assertIsNotNone(action._meta.get_field("audit_log"))
        self.assertIsNotNone(action._meta.get_field("version_history"))
        self.assertEqual(
            {field.name for field in action._meta.local_fields},
            {field.name for field in before_action._meta.local_fields},
        )
        parent_keys = {
            node.key
            for node in loader.graph.node_map[
                ("legal_documents", "0013_application_evidence_state_anchor")
            ].parents
        }
        self.assertIn(
            ("applications", "0016_bankverificationdecision_and_more"), parent_keys
        )

    def test_anchor_reverses_to_supported_boundary_without_schema_change(self):
        loader = MigrationLoader(None)
        migration = loader.disk_migrations[self.anchored[0]]

        self.assertEqual(migration.operations, [])
        self.assertEqual(
            migration.dependencies,
            [
                ("applications", "0016_bankverificationdecision_and_more"),
                ("legal_documents", "0012_portal_documentation_submission"),
            ],
        )


class LegalChecklistConstraintOwnerMigrationTests(TransactionTestCase):
    reset_sequences = True

    before_009g2 = [
        ("communications", "0003_notification"),
        ("disbursements", "0004_transfer_success"),
        ("legal_documents", "0014_staff_documentation_durable_actions"),
    ]
    current_dependencies = [
        ("communications", "0004_advice_outbox_and_receipt_owner"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
        ("legal_documents", "0014_staff_documentation_durable_actions"),
    ]
    anchored = [
        ("legal_documents", "0015_checklist_constraint_state_owner_anchor"),
    ]
    live_constraints = {
        "checklist_finance_requires_sanction",
        "checklist_ready_evidence_complete",
    }
    retired_constraints = {
        "checklist_account_requires_epic_009",
        "checklist_finance_requires_epic_009",
    }

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_anchor_preserves_exact_state_schema_and_rows_through_reverse_reapply(self):
        before_apps = self._migrate(self.before_009g2)
        retained = self._create_retained_facts(before_apps)

        anchored_apps = self._migrate(self.anchored)
        anchored_manifest = self._manifest(anchored_apps, retained)
        self._assert_live_constraint_manifest(anchored_apps, anchored_manifest)

        reversed_apps = self._migrate(self.current_dependencies)
        reversed_manifest = self._manifest(reversed_apps, retained)
        self._assert_live_constraint_manifest(reversed_apps, reversed_manifest)
        self.assertEqual(reversed_manifest, anchored_manifest)

        reapplied_apps = self._migrate(self.anchored)
        reapplied_manifest = self._manifest(reapplied_apps, retained)
        self._assert_live_constraint_manifest(reapplied_apps, reapplied_manifest)
        self.assertEqual(reapplied_manifest, anchored_manifest)

    def test_anchor_is_legal_owned_zero_sql_and_anchors_all_reviewed_leaves(self):
        loader = MigrationLoader(None)
        target = self.anchored[0]
        migration = loader.disk_migrations[target]

        self.assertEqual(migration.operations, [])
        self.assertEqual(
            set(migration.dependencies),
            {
                ("communications", "0004_advice_outbox_and_receipt_owner"),
                (
                    "disbursements",
                    "0007_remove_disbursement_disb_success_evidence_complete_and_more",
                ),
                (
                    "disbursements",
                    "0005_disbursementadviceintent_loanregisterupdate_and_more",
                ),
                ("legal_documents", "0014_staff_documentation_durable_actions"),
            },
        )
        self.assertEqual(loader.graph.forwards_plan(target).count(target), 1)

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _create_retained_facts(self, apps):
        Role = apps.get_model("identity", "Role")
        User = apps.get_model("identity", "User")
        Member = apps.get_model("members", "Member")
        LoanApplication = apps.get_model("applications", "LoanApplication")
        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
        WorkflowEvent = apps.get_model("workflows", "WorkflowEvent")
        ChecklistAction = apps.get_model("legal_documents", "ChecklistAction")

        role = Role.objects.create(
            role_code="migration_guard_reviewer",
            role_name="Migration guard reviewer",
            description="Synthetic migration fixture role",
        )
        actor = User.objects.create(
            full_name="Migration Guard Reviewer",
            email="migration-guard@example.invalid",
            mobile_number="0000000000",
            approval_authority_type="none",
            password_hash="not-a-real-password",
            primary_role=role,
        )
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Migration Fixture Member",
            display_name="Migration Fixture Member",
            folio_number="MIG-009G4",
            membership_status="active",
            pan_encrypted="synthetic-pan-token",
            pan_hash="synthetic-pan-hash",
            aadhaar_encrypted="synthetic-aadhaar-token",
            aadhaar_hash="synthetic-aadhaar-hash",
            registered_address_line1="Synthetic address",
            registered_address_line2="",
            registered_village_city="Synthetic village",
            registered_district="Synthetic district",
            registered_state="Synthetic state",
            registered_pincode="000000",
            mobile_number="0000000000",
            email="member-migration@example.invalid",
            kyc_status="verified",
            default_status="current",
            holding_mode="physical",
            active_member_status="active",
        )
        application = LoanApplication.objects.create(
            application_reference_number="MIG-009G4-APP",
            borrower_type="individual_farmer",
            declared_purpose="Synthetic migration fixture",
            purpose_category="crop_finance",
            loan_type_requested="short_term",
            borrower_request_notes="",
            member=member,
            received_by_user=actor,
        )
        checklist = DocumentChecklist.objects.create(
            loan_application=application,
            remarks="Retain this exact checklist fact",
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="document_checklist",
            entity_type="document_checklist",
            entity_id=checklist.pk,
            to_state="item_completed",
            trigger_reason="Synthetic retained migration fact",
            triggered_by_user=actor,
        )
        action = ChecklistAction.objects.create(
            document_checklist=checklist,
            action_type="company_secretary_approval",
            meaning="Synthetic retained checklist approval",
            comments="Retain this exact action fact",
            actor_user=actor,
            actor_user_name_snapshot=actor.full_name,
            canonical_role_code=role.role_code,
            request_id="migration-009g4-retained",
            workflow_event=workflow,
        )
        return {
            "checklist_id": checklist.pk,
            "action_id": action.pk,
        }

    def _manifest(self, apps, retained):
        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
        ChecklistAction = apps.get_model("legal_documents", "ChecklistAction")
        checklist = DocumentChecklist.objects.values(
            "document_checklist_id",
            "loan_application_id",
            "checklist_status",
            "remarks",
        ).get(pk=retained["checklist_id"])
        action = ChecklistAction.objects.values(
            "checklist_action_id",
            "document_checklist_id",
            "action_type",
            "meaning",
            "comments",
            "actor_user_name_snapshot",
            "canonical_role_code",
            "request_id",
            "workflow_event_id",
        ).get(pk=retained["action_id"])
        with connection.cursor() as cursor:
            physical = connection.introspection.get_constraints(
                cursor, "document_checklists"
            )
        physical_schema = {
            name: {
                key: tuple(value) if isinstance(value, list) else value
                for key, value in details.items()
                if key
                in {
                    "columns",
                    "primary_key",
                    "unique",
                    "foreign_key",
                    "check",
                    "index",
                }
            }
            for name, details in physical.items()
        }
        return {
            "checklist": {key: str(value) for key, value in checklist.items()},
            "action": {key: str(value) for key, value in action.items()},
            "live_physical_constraint_counts": {
                name: int(name in physical) for name in self.live_constraints
            },
            "retired_physical_constraint_counts": {
                name: int(name in physical) for name in self.retired_constraints
            },
            "physical_schema": physical_schema,
        }

    def _assert_live_constraint_manifest(self, apps, manifest):
        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
        state_names = [
            constraint.name for constraint in DocumentChecklist._meta.constraints
        ]
        for name in self.live_constraints:
            self.assertEqual(state_names.count(name), 1, state_names)
            self.assertEqual(manifest["live_physical_constraint_counts"][name], 1)
        for name in self.retired_constraints:
            self.assertEqual(state_names.count(name), 0, state_names)
            self.assertEqual(manifest["retired_physical_constraint_counts"][name], 0)


class LegalChecklistMigrationOwnershipGuardTests(SimpleTestCase):
    def test_guard_snapshots_all_four_historical_operation_changes(self):
        loader = MigrationLoader(None)
        migration = loader.disk_migrations[
            (
                "disbursements",
                "0005_disbursementadviceintent_loanregisterupdate_and_more",
            )
        ]
        state = loader.project_state(migration.dependencies)

        for index, operation in enumerate(migration.operations[:4]):
            with self.subTest(index=index):
                before, changed_models = _apply_operation_state(
                    owner_app="disbursements",
                    state=state,
                    operation=operation,
                )

                self.assertEqual(changed_models, {_CHECKLIST_KEY})
                self.assertTrue(
                    _is_retained_transition(
                        path=_HISTORICAL_PATH,
                        operation=operation,
                        index=index,
                        before=before,
                        after=state,
                        changed_models=changed_models,
                    )
                )

    def test_historical_exception_rejects_extra_same_model_option_mutation(self):
        after = MigrationLoader(None).project_state()
        before = after.clone()
        before_model = before.models[_CHECKLIST_KEY]
        before_model.options["constraints"] = [
            item
            for item in before_model.options.get("constraints", ())
            if item.name != "checklist_finance_requires_sanction"
        ]
        before_model.options["review_probe_extra_change"] = "before"
        after.models[_CHECKLIST_KEY].options["review_probe_extra_change"] = "after"
        operation_type = type(
            "AddLegalChecklistConstraint",
            (Operation,),
            {"__module__": _HISTORICAL_MODULE},
        )

        self.assertFalse(
            _is_retained_transition(
                path=_HISTORICAL_PATH,
                operation=operation_type(),
                index=2,
                before=before,
                after=after,
                changed_models={_CHECKLIST_KEY},
            )
        )

    def test_historical_exception_rejects_changed_expected_constraint_definition(self):
        after = MigrationLoader(None).project_state()
        before = after.clone()
        constraint_name = "checklist_finance_requires_sanction"
        before.models[_CHECKLIST_KEY].options["constraints"] = [
            item
            for item in before.models[_CHECKLIST_KEY].options.get("constraints", ())
            if item.name != constraint_name
        ]
        after_model = after.models[_CHECKLIST_KEY]
        after_model.options["constraints"] = [
            models.CheckConstraint(
                check=models.Q(
                    ("senior_manager_finance_signature_id__isnull", False)
                ),
                name=constraint_name,
            )
            if item.name == constraint_name
            else item
            for item in after_model.options.get("constraints", ())
        ]
        operation_type = type(
            "AddLegalChecklistConstraint",
            (Operation,),
            {"__module__": _HISTORICAL_MODULE},
        )

        self.assertFalse(
            _is_retained_transition(
                path=_HISTORICAL_PATH,
                operation=operation_type(),
                index=2,
                before=before,
                after=after,
                changed_models={_CHECKLIST_KEY},
            )
        )

    def test_historical_exception_rejects_complete_model_state_mutation_matrix(self):
        def replace_field(model_state):
            model_state.fields["remarks"] = models.TextField(blank=False)

        def replace_constraint(model_state):
            model_state.options["constraints"] = [
                models.CheckConstraint(
                    check=models.Q(("checklist_status", "review_probe")),
                    name="document_checklist_valid_status",
                )
                if item.name == "document_checklist_valid_status"
                else item
                for item in model_state.options.get("constraints", ())
            ]

        def append_index(model_state):
            model_state.options["indexes"] = [
                *model_state.options.get("indexes", ()),
                models.Index(
                    fields=["created_at"], name="review_probe_checklist_idx"
                ),
            ]

        def change_option(model_state):
            model_state.options["ordering"] = ["updated_at"]

        def change_bases(model_state):
            model_state.bases = ("legal_documents.reviewprobebase",)

        def change_managers(model_state):
            model_state.managers = [("review_probe", models.Manager())]

        mutations = {
            "fields": replace_field,
            "constraints": replace_constraint,
            "indexes": append_index,
            "options": change_option,
            "bases": change_bases,
            "managers": change_managers,
        }
        loader = MigrationLoader(None)
        migration = loader.disk_migrations[
            (
                "disbursements",
                "0005_disbursementadviceintent_loanregisterupdate_and_more",
            )
        ]

        for index, operation in enumerate(migration.operations[:4]):
            for footprint, mutate in mutations.items():
                with self.subTest(index=index, footprint=footprint):
                    state = loader.project_state(migration.dependencies)
                    for prior_operation in migration.operations[:index]:
                        _apply_operation_state(
                            owner_app="disbursements",
                            state=state,
                            operation=prior_operation,
                        )
                    before, changed_models = _apply_operation_state(
                        owner_app="disbursements",
                        state=state,
                        operation=operation,
                    )
                    mutate(state.models[_CHECKLIST_KEY])

                    self.assertFalse(
                        _is_retained_transition(
                            path=_HISTORICAL_PATH,
                            operation=operation,
                            index=index,
                            before=before,
                            after=state,
                            changed_models=changed_models,
                        )
                    )

    def test_shared_package_contains_no_legal_migration_policy(self):
        shared_root = Path(__file__).resolve().parents[1] / "shared"
        shared_source = "\n".join(
            path.read_text()
            for path in sorted(shared_root.rglob("*.py"))
        ).lower()

        for business_token in (
            "legal_documents",
            "documentchecklist",
            "0005_disbursementadviceintent_loanregisterupdate_and_more",
            "legal_checklist_state_allowlist",
        ):
            self.assertNotIn(business_token, shared_source)

    def test_guard_does_not_report_database_only_runpython(self):
        path = Path("future_app/migrations/0005_data_only.py")
        operation = migrations.RunPython(lambda apps, schema_editor: None)

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={path: [operation]}
            ),
            [],
        )

    def test_guard_accepts_future_legal_owned_operation(self):
        path = Path("legal_documents/migrations/0016_future.py")

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={path: [HelperChecklistMutation()]}
            ),
            [],
        )

    def test_historical_exception_rejects_renamed_path_and_class(self):
        historical_path = Path(
            "disbursements/migrations/"
            "0005_disbursementadviceintent_loanregisterupdate_and_more.py"
        )
        renamed_path = Path("disbursements/migrations/0006_renamed.py")

        def state_forwards(operation, app_label, state):
            state.models[("legal_documents", "documentchecklist")].options.clear()

        exact_name_wrong_module = type(
            "RemoveLegalChecklistConstraint",
            (Operation,),
            {"state_forwards": state_forwards},
        )()
        renamed_class = type(
            "RenamedLegalChecklistConstraint",
            (Operation,),
            {"state_forwards": state_forwards},
        )()

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={renamed_path: [exact_name_wrong_module]}
            ),
            [f"{renamed_path.as_posix()}:RemoveLegalChecklistConstraint"],
        )
        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={historical_path: [renamed_class]}
            ),
            [f"{historical_path.as_posix()}:RenamedLegalChecklistConstraint"],
        )

    def test_historical_exception_rejects_changed_target_footprint(self):
        historical_path = Path(
            "disbursements/migrations/"
            "0005_disbursementadviceintent_loanregisterupdate_and_more.py"
        )

        def state_forwards(operation, app_label, state):
            state.models[("legal_documents", "documentchecklist")].options.clear()
            state.models[("legal_documents", "checklistitem")].options.clear()

        changed_target_class = type(
            "RemoveLegalChecklistConstraint",
            (Operation,),
            {
                "__module__": (
                    "sfpcl_credit.disbursements.migrations."
                    "0005_disbursementadviceintent_loanregisterupdate_and_more"
                ),
                "state_forwards": state_forwards,
            },
        )

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={historical_path: [changed_target_class()]}
            ),
            [f"{historical_path.as_posix()}:RemoveLegalChecklistConstraint"],
        )

    def test_historical_exception_is_immutable_and_rejects_sibling_operation(self):
        historical_path = Path(
            "disbursements/migrations/"
            "0005_disbursementadviceintent_loanregisterupdate_and_more.py"
        )

        def state_forwards(operation, app_label, state):
            state.models[("legal_documents", "documentchecklist")].options.clear()

        sibling_class = type(
            "AddLegalChecklistConstraint",
            (Operation,),
            {
                "__module__": (
                    "sfpcl_credit.disbursements.migrations."
                    "0005_disbursementadviceintent_loanregisterupdate_and_more"
                ),
                "state_forwards": state_forwards,
            },
        )

        self.assertIsInstance(LEGAL_CHECKLIST_STATE_ALLOWLIST, frozenset)
        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={
                    historical_path: [
                        migrations.RunPython(lambda apps, schema_editor: None),
                        migrations.RunPython(lambda apps, schema_editor: None),
                        migrations.RunPython(lambda apps, schema_editor: None),
                        migrations.RunPython(lambda apps, schema_editor: None),
                        sibling_class(),
                    ]
                }
            ),
            [
                f"{historical_path.as_posix()}:AddLegalChecklistConstraint"
            ],
        )

    def test_guard_rejects_helper_indirected_cross_app_operation(self):
        path = Path("future_app/migrations/0004_helper.py")

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={path: [HelperChecklistMutation()]}
            ),
            [f"{path.as_posix()}:HelperChecklistMutation"],
        )

    def test_guard_rejects_inherited_cross_app_operation(self):
        path = Path("future_app/migrations/0003_inherited.py")

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={path: [InheritedChecklistMutation()]}
            ),
            [f"{path.as_posix()}:InheritedChecklistMutation"],
        )

    def test_guard_rejects_imported_cross_app_operation(self):
        path = Path("future_app/migrations/0002_imported.py")

        self.assertEqual(
            legal_checklist_state_ownership_violations(
                operations={path: [ImportedChecklistMutation()]}
            ),
            [f"{path.as_posix()}:ImportedChecklistMutation"],
        )

    def test_guard_rejects_module_constant_cross_app_checklist_state_mutation(self):
        synthetic = {
            Path("future_app/migrations/0001_bad.py"): """
from django.db.migrations.operations.base import Operation

TARGET_APP = "legal_documents"
TARGET_MODEL = "documentchecklist"

class BadChecklistMutation(Operation):
    def state_forwards(self, app_label, state):
        state.models[(TARGET_APP, TARGET_MODEL)].options.clear()
"""
        }

        self.assertEqual(
            legal_checklist_state_ownership_violations(sources=synthetic),
            ["future_app/migrations/0001_bad.py:BadChecklistMutation"],
        )

    def test_guard_rejects_synthetic_cross_app_checklist_state_mutation(self):
        synthetic = {
            Path("future_app/migrations/0001_bad.py"): """
from django.db.migrations.operations.base import Operation

class BadChecklistMutation(Operation):
    def state_forwards(self, app_label, state):
        state.models[("legal_documents", "documentchecklist")].options.clear()
"""
        }

        self.assertEqual(
            legal_checklist_state_ownership_violations(sources=synthetic),
            ["future_app/migrations/0001_bad.py:BadChecklistMutation"],
        )

    def test_guard_allows_only_reviewed_009g2_history_in_repository(self):
        package_root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            LEGAL_CHECKLIST_STATE_ALLOWLIST,
            {
                "disbursements/migrations/"
                "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
                "AddLegalChecklistConstraint",
                "disbursements/migrations/"
                "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
                "RemoveLegalChecklistConstraint",
            },
        )
        self.assertEqual(
            legal_checklist_state_ownership_violations(package_root=package_root),
            [],
        )
