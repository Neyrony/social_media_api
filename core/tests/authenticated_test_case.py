from django.contrib.auth import get_user_model
from django.test import TestCase


class TestAuthenticatedUser(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="test12345",
            first_name="John",
            last_name="Doe",
        )
        cls.profile = cls.user.profile

    def setUp(self):
        self.client.force_login(self.user)
