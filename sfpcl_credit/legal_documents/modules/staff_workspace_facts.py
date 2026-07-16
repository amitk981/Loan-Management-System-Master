"""Locked legal prerequisites exposed to the staff-workspace process."""
from dataclasses import dataclass
from django.db import models
from sfpcl_credit.legal_documents.models import LoanDocument, NotarisationRecord, StampDutyRecord

@dataclass(frozen=True)
class SecurityLegalFacts:
    poa_document_id: object | None
    poa_stamp_id: object | None
    poa_notary_id: object | None
    sh4_document_id: object | None

def security_creation_facts(*, application_id):
    poa_document = LoanDocument.objects.filter(loan_application_id=application_id, document_type='power_of_attorney', renderer_validated_document_id=models.F('document_id')).order_by('-created_at').first()
    poa_stamp = StampDutyRecord.objects.filter(loan_document=poa_document, status='adequate').order_by('created_at', 'stamp_duty_record_id').first()
    poa_notary = NotarisationRecord.objects.filter(loan_document=poa_document, status='completed').order_by('created_at', 'notarisation_record_id').first()
    sh4_document_id = LoanDocument.objects.filter(loan_application_id=application_id, document_type='sh4').order_by('-created_at').values_list('loan_document_id', flat=True).first()
    return SecurityLegalFacts(poa_document_id=poa_document.pk if poa_document else None, poa_stamp_id=poa_stamp.pk if poa_stamp else None, poa_notary_id=poa_notary.pk if poa_notary else None, sh4_document_id=sh4_document_id)
