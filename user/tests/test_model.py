from django.contrib.auth import get_user_model
from django.test import TestCase


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create(
            email="user@example.com",
            password="password12345",
        )

    def test_username_absence(self):
        with self.assertRaises(TypeError):
            get_user_model().objects.create(
                username="user",
                password="password",
            )

    def test_username_field(self):
        self.assertEqual(get_user_model().USERNAME_FIELD, "email")

    def test_base_field(self):
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_str(self):
        self.assertEqual(str(self.user), self.user.email)
