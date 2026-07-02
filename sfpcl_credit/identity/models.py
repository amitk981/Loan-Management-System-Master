import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class Role(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_code = models.CharField(max_length=80, unique=True)
    role_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    status = models.CharField(max_length=40, default="active", db_index=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.role_code


class Team(models.Model):
    team_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_code = models.CharField(max_length=80, unique=True)
    team_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=40, default="active", db_index=True)

    class Meta:
        db_table = "teams"

    def __str__(self):
        return self.team_code


class User(models.Model):
    ACTIVE_STATUS = "active"
    AUTHENTICABLE_STATUSES = {ACTIVE_STATUS}

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, unique=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    employee_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    status = models.CharField(max_length=40, default=ACTIVE_STATUS, db_index=True)
    primary_role = models.ForeignKey(Role, on_delete=models.PROTECT)
    approval_authority_type = models.CharField(max_length=80, blank=True)
    password_hash = models.CharField(max_length=256)
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by_user = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="created_users",
    )
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by_user = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_users",
    )

    class Meta:
        db_table = "users"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def can_authenticate(self):
        return self.status in self.AUTHENTICABLE_STATUSES

    def role_codes(self):
        if self.primary_role.status != "active":
            return []
        return [self.primary_role.role_code]

    def team_codes(self):
        return list(
            self.team_memberships.filter(status="active", team__status="active")
            .values_list("team__team_code", flat=True)
            .order_by("team__team_code")
        )

    def permissions_version(self):
        timestamp = self.updated_at or self.created_at
        return timestamp.isoformat().replace("+00:00", "Z")

    def __str__(self):
        return self.email


class UserTeamMembership(models.Model):
    user_team_membership_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="team_memberships"
    )
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    team_role = models.CharField(max_length=80, default="member")
    effective_from = models.DateField(blank=True, null=True)
    effective_to = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=40, default="active", db_index=True)

    class Meta:
        db_table = "user_team_memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"], name="unique_user_team_membership"
            )
        ]


class UserSession(models.Model):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"

    user_session_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    refresh_token_hash = models.CharField(max_length=128)
    session_status = models.CharField(max_length=40, default=ACTIVE, db_index=True)
    ip_address = models.CharField(max_length=80, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(blank=True, null=True)
    revoked_reason = models.CharField(max_length=80, blank=True)

    class Meta:
        db_table = "user_sessions"

    def is_active(self):
        return self.session_status == self.ACTIVE and self.expires_at > timezone.now()

    def revoke(self, reason):
        self.session_status = self.REVOKED
        self.revoked_reason = reason
        self.revoked_at = timezone.now()
        self.save(update_fields=["session_status", "revoked_reason", "revoked_at"])


class AuditLog(models.Model):
    audit_log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="audit_logs"
    )
    actor_type = models.CharField(max_length=60, default="user")
    action = models.CharField(max_length=150, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(blank=True, null=True, db_index=True)
    old_value_json = models.JSONField(blank=True, null=True)
    new_value_json = models.JSONField(blank=True, null=True)
    ip_address = models.CharField(max_length=80, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["created_at"]
