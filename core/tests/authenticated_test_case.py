from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APITestCase


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
        super().setUp()
        self.client.force_login(self.user)


class TestAPIAuthenticatedUser(APITestCase):
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
        super().setUp()
        self.client.force_authenticate(user=self.user)
