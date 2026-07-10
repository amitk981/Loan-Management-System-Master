import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Member(models.Model):
    MEMBER_TYPES = {"individual_farmer", "fpc", "producer_institution"}
    MEMBERSHIP_STATUSES = {"active", "inactive", "pending_verification"}
    KYC_STATUSES = {"verified", "missing", "rekyc_due", "pending", "rejected"}
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
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, blank=True, null=True)
    last_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=40, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=150, blank=True, null=True)
    land_area_under_cultivation_acres = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    primary_crop = models.CharField(max_length=100, blank=True)
    services_availed_flag = models.BooleanField(default=False)
    employment_or_service_years = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "individual_member_profiles"

    def clean(self):
        super().clean()
        if self.member_id and self.member.member_type != "individual_farmer":
            raise ValidationError(
                {"member": "Individual profiles require an individual_farmer member."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


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

    def clean(self):
        super().clean()
        if self.member_id and self.member.member_type not in {
            "fpc",
            "producer_institution",
        }:
            raise ValidationError(
                {
                    "member": (
                        "Producer institution profiles require an fpc or "
                        "producer_institution member."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Nominee(models.Model):
    nominee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="nominees")
    loan_application_id = models.UUIDField(blank=True, null=True)
    nominee_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    age_at_application = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=40)
    relationship_to_borrower = models.CharField(max_length=100, blank=True)
    pan_encrypted = models.TextField()
    pan_hash = models.CharField(max_length=128, db_index=True)
    aadhaar_encrypted = models.TextField()
    aadhaar_hash = models.CharField(max_length=128, db_index=True)
    kyc_status = models.CharField(max_length=60, default="pending")
    minor_flag = models.BooleanField(default=False, db_index=True)
    signature_required_flag = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "nominees"
        indexes = [
            models.Index(fields=["member"], name="idx_nominees_member"),
            models.Index(fields=["minor_flag"], name="idx_nominees_minor_flag"),
            models.Index(fields=["pan_hash"], name="idx_nominees_pan_hash"),
            models.Index(fields=["aadhaar_hash"], name="idx_nominees_aadhaar_hash"),
        ]

    def __str__(self):
        return self.nominee_name


class Shareholding(models.Model):
    HOLDING_MODES = {"physical", "demat", "mixed"}
    STATUSES = {"active", "inactive"}

    shareholding_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="shareholdings")
    folio_number = models.CharField(max_length=100, db_index=True)
    number_of_shares = models.IntegerField()
    holding_mode = models.CharField(max_length=40, db_index=True)
    demat_account_id = models.UUIDField(blank=True, null=True)
    latest_share_valuation_id = models.UUIDField(blank=True, null=True)
    valuation_per_share = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    valuation_effective_date = models.DateField(blank=True, null=True)
    pledged_share_count = models.IntegerField(default=0)
    available_share_count = models.IntegerField()
    future_shares_pledge_flag = models.BooleanField(default=False)
    status = models.CharField(max_length=40, default="active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "shareholdings"
        indexes = [
            models.Index(fields=["member"], name="idx_shareholdings_member"),
            models.Index(fields=["folio_number"], name="idx_shareholdings_folio"),
            models.Index(fields=["holding_mode"], name="idx_shareholdings_mode"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(number_of_shares__gte=0),
                name="shareholdings_non_negative_shares",
            ),
            models.CheckConstraint(
                check=models.Q(pledged_share_count__gte=0),
                name="shareholdings_non_negative_pledged",
            ),
            models.CheckConstraint(
                check=models.Q(pledged_share_count__lte=models.F("number_of_shares")),
                name="shareholdings_pledged_lte_total",
            ),
            models.CheckConstraint(
                check=models.Q(
                    available_share_count=models.F("number_of_shares")
                    - models.F("pledged_share_count")
                ),
                name="shareholdings_available_derived",
            ),
        ]

    def clean(self):
        super().clean()
        if self.holding_mode not in self.HOLDING_MODES:
            raise ValidationError({"holding_mode": "Unsupported holding mode."})
        if self.status not in self.STATUSES:
            raise ValidationError({"status": "Unsupported shareholding status."})
        if self.number_of_shares is not None and self.number_of_shares < 0:
            raise ValidationError({"number_of_shares": "Share count cannot be negative."})
        if self.pledged_share_count is not None and self.pledged_share_count < 0:
            raise ValidationError({"pledged_share_count": "Pledged share count cannot be negative."})
        if (
            self.number_of_shares is not None
            and self.pledged_share_count is not None
            and self.pledged_share_count > self.number_of_shares
        ):
            raise ValidationError(
                {"pledged_share_count": "Pledged shares cannot exceed total shares."}
            )
        self.available_share_count = (
            self.number_of_shares or 0
        ) - (self.pledged_share_count or 0)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio_number} ({self.number_of_shares})"


class LandHolding(models.Model):
    VERIFICATION_STATUSES = {"pending", "verified", "rejected"}

    land_holding_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="land_holdings")
    document_type = models.CharField(max_length=80)
    survey_number = models.CharField(max_length=120, blank=True)
    village = models.CharField(max_length=150, blank=True)
    taluka = models.CharField(max_length=150, blank=True)
    district = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=150, blank=True)
    area_acres = models.DecimalField(max_digits=12, decimal_places=2)
    document_id = models.UUIDField()
    verification_status = models.CharField(max_length=60, default="pending", db_index=True)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_land_holdings",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "land_holdings"
        indexes = [
            models.Index(fields=["member"], name="idx_land_holdings_member"),
            models.Index(fields=["verification_status"], name="idx_land_holdings_verify"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(area_acres__gt=0),
                name="land_holdings_positive_area",
            ),
        ]

    def clean(self):
        super().clean()
        if self.verification_status not in self.VERIFICATION_STATUSES:
            raise ValidationError({"verification_status": "Unsupported verification status."})
        if self.area_acres is not None and self.area_acres <= 0:
            raise ValidationError({"area_acres": "Area acres must be greater than zero."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.survey_number or self.land_holding_id} ({self.area_acres} acres)"


class CropPlan(models.Model):
    VERIFICATION_STATUSES = {"pending", "verified", "rejected"}

    crop_plan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="crop_plans")
    loan_application_id = models.UUIDField(blank=True, null=True)
    crop_type = models.CharField(max_length=100, db_index=True)
    season = models.CharField(max_length=100, blank=True)
    planned_area_acres = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_cost_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    loan_purpose_alignment = models.CharField(max_length=60)
    document_id = models.UUIDField(blank=True, null=True)
    verification_status = models.CharField(max_length=60, default="pending", db_index=True)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_crop_plans",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "crop_plans"
        indexes = [
            models.Index(fields=["member"], name="idx_crop_plans_member"),
            models.Index(fields=["crop_type"], name="idx_crop_plans_crop_type"),
            models.Index(fields=["verification_status"], name="idx_crop_plans_verify"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(planned_area_acres__gt=0),
                name="crop_plans_positive_area",
            ),
        ]

    def clean(self):
        super().clean()
        if self.verification_status not in self.VERIFICATION_STATUSES:
            raise ValidationError({"verification_status": "Unsupported verification status."})
        if self.planned_area_acres is not None and self.planned_area_acres <= 0:
            raise ValidationError(
                {"planned_area_acres": "Planned area acres must be greater than zero."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.crop_type} ({self.planned_area_acres} acres)"


class KycProfile(models.Model):
    PARTY_TYPES = {"member"}
    KYC_STATUSES = {"pending", "verified", "rejected", "rekyc_due"}
    RISK_RATINGS = {"low", "medium", "high"}

    kyc_profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party_type = models.CharField(max_length=60, db_index=True)
    party_id = models.UUIDField(db_index=True)
    kyc_status = models.CharField(max_length=60, default="pending", db_index=True)
    ckyc_identifier_encrypted = models.TextField(blank=True, null=True)
    ckyc_consent_flag = models.BooleanField()
    beneficial_ownership_verified_flag = models.BooleanField(blank=True, null=True)
    risk_rating = models.CharField(max_length=60, blank=True, null=True)
    last_verified_at = models.DateTimeField(blank=True, null=True)
    last_verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="last_verified_kyc_profiles",
    )
    rekyc_due_date = models.DateField(blank=True, null=True, db_index=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "kyc_profiles"
        indexes = [
            models.Index(fields=["party_type", "party_id"], name="idx_kyc_profiles_party"),
            models.Index(fields=["kyc_status"], name="idx_kyc_profiles_status"),
            models.Index(fields=["rekyc_due_date"], name="idx_kyc_profiles_rekyc_due"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["party_type", "party_id"],
                name="kyc_profiles_unique_party",
            ),
        ]

    def clean(self):
        super().clean()
        if self.party_type not in self.PARTY_TYPES:
            raise ValidationError({"party_type": "Unsupported party type."})
        if self.kyc_status not in self.KYC_STATUSES:
            raise ValidationError({"kyc_status": "Unsupported KYC status."})
        if self.risk_rating and self.risk_rating not in self.RISK_RATINGS:
            raise ValidationError({"risk_rating": "Unsupported risk rating."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.party_type}:{self.party_id}"


class KycDocument(models.Model):
    DOCUMENT_TYPES = {"pan", "aadhaar", "photo", "ckyc_consent"}
    SELF_ATTESTED_REQUIRED_TYPES = {"pan", "aadhaar"}
    VERIFICATION_STATUSES = {"pending", "verified", "rejected"}

    kyc_document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_profile = models.ForeignKey(
        KycProfile, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=80, db_index=True)
    document_file = models.ForeignKey(
        "documents.DocumentFile",
        on_delete=models.PROTECT,
        related_name="kyc_documents",
    )
    self_attested_flag = models.BooleanField()
    verification_status = models.CharField(max_length=60, default="pending", db_index=True)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_kyc_documents",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "kyc_documents"
        indexes = [
            models.Index(fields=["kyc_profile"], name="idx_kyc_documents_profile"),
            models.Index(fields=["document_type"], name="idx_kyc_documents_type"),
            models.Index(fields=["verification_status"], name="idx_kyc_documents_status"),
        ]

    def clean(self):
        super().clean()
        if self.document_type not in self.DOCUMENT_TYPES:
            raise ValidationError({"document_type": "Unsupported KYC document type."})
        if self.verification_status not in self.VERIFICATION_STATUSES:
            raise ValidationError(
                {"verification_status": "Unsupported verification status."}
            )
        if (
            self.document_type in self.SELF_ATTESTED_REQUIRED_TYPES
            and not self.self_attested_flag
        ):
            raise ValidationError(
                {"self_attested_flag": "Self-attestation is required for PAN and Aadhaar."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.document_type}:{self.kyc_document_id}"


class CancelledCheque(models.Model):
    VERIFICATION_STATUSES = {"pending", "verified", "rejected"}

    cancelled_cheque_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application_id = models.UUIDField(blank=True, null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="cancelled_cheques")
    document_id = models.UUIDField()
    account_number_encrypted = models.TextField()
    account_number_hash = models.CharField(max_length=128, db_index=True)
    account_number_last4 = models.CharField(max_length=4, blank=True)
    ifsc = models.CharField(max_length=20, db_index=True)
    branch_name = models.CharField(max_length=150, blank=True)
    verification_status = models.CharField(max_length=60, default="pending", db_index=True)
    signature_mismatch_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "cancelled_cheques"
        indexes = [
            models.Index(fields=["member"], name="idx_can_cheques_member"),
            models.Index(fields=["document_id"], name="idx_can_cheques_doc"),
            models.Index(fields=["account_number_hash"], name="idx_can_cheques_acct_hash"),
            models.Index(fields=["verification_status"], name="idx_can_cheques_verify"),
        ]

    def clean(self):
        super().clean()
        if self.verification_status not in self.VERIFICATION_STATUSES:
            raise ValidationError({"verification_status": "Unsupported verification status."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_id}:{self.account_number_last4}"


class BankAccount(models.Model):
    OWNER_PARTY_TYPES = {"member"}
    VERIFICATION_STATUSES = {"pending", "verified", "rejected"}
    STATUSES = {"active", "inactive"}

    bank_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_party_type = models.CharField(max_length=60, db_index=True)
    owner_party_id = models.UUIDField(db_index=True)
    account_holder_name = models.CharField(max_length=255)
    account_number_encrypted = models.TextField()
    account_number_hash = models.CharField(max_length=128, db_index=True)
    account_number_last4 = models.CharField(max_length=4, blank=True)
    ifsc = models.CharField(max_length=20, db_index=True)
    bank_name = models.CharField(max_length=150, blank=True)
    branch_name = models.CharField(max_length=150, blank=True)
    verification_status = models.CharField(max_length=60, default="pending", db_index=True)
    cancelled_cheque = models.ForeignKey(
        CancelledCheque,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="bank_accounts",
    )
    signature_verified_flag = models.BooleanField(blank=True, null=True)
    status = models.CharField(max_length=40, default="active", db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "bank_accounts"
        indexes = [
            models.Index(fields=["owner_party_type", "owner_party_id"], name="idx_bank_accounts_owner"),
            models.Index(fields=["account_number_hash"], name="idx_bank_accounts_hash"),
            models.Index(fields=["ifsc"], name="idx_bank_accounts_ifsc"),
            models.Index(fields=["verification_status"], name="idx_bank_accounts_verify"),
            models.Index(fields=["status"], name="idx_bank_accounts_status"),
        ]

    def clean(self):
        super().clean()
        if self.owner_party_type not in self.OWNER_PARTY_TYPES:
            raise ValidationError({"owner_party_type": "Unsupported owner party type."})
        if self.verification_status not in self.VERIFICATION_STATUSES:
            raise ValidationError({"verification_status": "Unsupported verification status."})
        if self.status not in self.STATUSES:
            raise ValidationError({"status": "Unsupported bank account status."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner_party_type}:{self.owner_party_id}:{self.account_number_last4}"
