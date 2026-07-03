from django.test import TestCase

from sfpcl_credit.identity.models import Role, User


class IdentityTestCase(TestCase):
    def setUp(self):
        self.role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            description="Credit workflow owner",
            is_system_role=True,
            status="active",
        )
        self.user = User.objects.create(
            full_name="Credit Manager",
            email="credit.manager@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        self.user.set_password("CorrectHorse123!")
        self.user.save()
