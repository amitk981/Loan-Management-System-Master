# backend-migrations Results

Command: "/Users/amitkallapa/LMS/.ralph/venv/bin/python" sfpcl_credit/manage.py makemigrations --check --dry-run

Migrations for 'disbursements':
  sfpcl_credit/disbursements/migrations/0007_remove_disbursement_disb_success_evidence_complete_and_more.py
    - Remove constraint disb_success_evidence_complete from model disbursement
    - Add field register_update to disbursement
    - Create constraint disb_success_evidence_complete on model disbursement

Duration milliseconds: 613
Exit code: 1
