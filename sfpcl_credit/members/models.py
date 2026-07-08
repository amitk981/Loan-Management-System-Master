import uuid

from django.db import models
from django.utils import timezone


class Member(models.Model):
    MEMBER_TYPES = {"individual_farmer", "fpc", "producer_institution"}
    MEMBERSHIP_STATUSES = {"active", "inactive", "pending_verification"}
    KYC_STATUSES = {"verified", "missing", "rekyc_due", "pending"}
    DEFAULT_STATUSES = {"no_default", "existing_default", "past_default"}

    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member_number = models.CharField(max_length=80, blank=True, null=True, unique=True)
    member_type = models.CharField(max_length=60, db_index=True)
    legal_name = models.CharField(max_length=255, db_index=True)
    display_name = models.CharField(max_length=255)
    folio_number = models.CharField(max_length=100, db_index=True)
    membership_start_date = models.DateField(blank=True, null=True)
    membership_status = models.CharField(max_length=60, db_index=True)
    pan_encrypted = models.TextField()
    pan_hash = models.CharField(max_length=128, db_index=True)
    aadhaar_encrypted = models.TextField(blank=True)
    aadhaar_hash = models.CharField(max_length=128, blank=True, db_index=True)
    registered_address_line1 = models.CharField(max_length=255, blank=True)
    registered_address_line2 = models.CharField(max_length=255, blank=True)
    registered_village_city = models.CharField(max_length=150, blank=True)
    registered_district = models.CharField(max_length=150, blank=True)
    registered_state = models.CharField(max_length=150, blank=True)
    registered_pincode = models.CharField(max_length=20, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True, db_index=True)
    email = models.EmailField(max_length=255, blank=True, db_index=True)
    kyc_status = models.CharField(max_length=60, db_index=True)
    rekyc_due_date = models.DateField(blank=True, null=True, db_index=True)
    default_status = models.CharField(max_length=60, db_index=True)
    active_member_status_id = models.UUIDField(blank=True, null=True)
    primary_bank_account_id = models.UUIDField(blank=True, null=True)
    number_of_shares = models.PositiveIntegerField(blank=True, null=True)
    holding_mode = models.CharField(max_length=60, blank=True)
    available_share_count = models.PositiveIntegerField(blank=True, null=True)
    active_member_status = models.CharField(max_length=60, blank=True)
    active_member_verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="created_members",
    )
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_members",
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "members"
        indexes = [
            models.Index(fields=["member_type", "membership_status"], name="idx_members_type_status"),
            models.Index(fields=["folio_number"], name="idx_members_folio_number"),
            models.Index(fields=["pan_hash"], name="idx_members_pan_hash"),
            models.Index(fields=["aadhaar_hash"], name="idx_members_aadhaar_hash"),
            models.Index(fields=["mobile_number"], name="idx_members_mobile"),
            models.Index(fields=["kyc_status"], name="idx_members_kyc_status"),
            models.Index(fields=["default_status"], name="idx_members_default_status"),
        ]

    def __str__(self):
        return self.member_number or str(self.member_id)


class IndividualMemberProfile(models.Model):
    individual_member_profile_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="individual_profile"
    )
    land_area_under_cultivation_acres = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    primary_crop = models.CharField(max_length=100, blank=True)
    services_availed_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "individual_member_profiles"


class ProducerInstitutionProfile(models.Model):
    producer_institution_profile_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="producer_institution_profile"
    )
    institution_type = models.CharField(max_length=80)
    registration_number = models.CharField(max_length=120, blank=True, db_index=True)
    authorised_signatory_name = models.CharField(max_length=200)
    board_resolution_required_flag = models.BooleanField(default=False)
    services_availed_flag = models.BooleanField(default=False)
    produce_supply_years = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "producer_institution_profiles"
