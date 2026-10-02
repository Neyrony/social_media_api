from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.tests.authenticated_test_case import TestAPIAuthenticatedUser
from user.serializers import UserRetrieveSerializer


class UnauthenticatedUserTest(APITestCase):
    def test_forbidden_access(self):
        response = self.client.get(reverse("user:personal-info"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(reverse("user:logout"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(TestAPIAuthenticatedUser):
    def test_register(self):
        data = {
            "email": "email@example.com",
            "password": "test12345",
        }
        response = self.client.post(reverse("user:register"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(id=response.data["id"])

        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_personal_info_get(self):
        response = self.client.get(reverse("user:personal-info"))

        user_serializer = UserRetrieveSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_serializer.data)

    def test_personal_info_put(self):
        response = self.client.put(
            reverse("user:personal-info"),
            data={"email": "new_email@example.com", "password": "newpassword"},
        )

        self.user.refresh_from_db()
        user_serializer = UserRetrieveSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_serializer.data)

    def test_personal_info_patch(self):
        response = self.client.patch(
            reverse("user:personal-info"),
            data={"email": "new_email@example.com"},
        )

        self.user.refresh_from_db()
        user_serializer = UserRetrieveSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_serializer.data)

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            reverse("user:logout"), data={"refresh_token": str(refresh)}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(TokenError):
            refresh.check_blacklist()
