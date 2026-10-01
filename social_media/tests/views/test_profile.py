from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.authenticated_test_case import TestAPIAuthenticatedUser
from social_media.models import Profile
from social_media.serializers import (
    ProfileListRetrieveSerializer,
    ProfileDetailedView,
    ProfileFollowingSerializer,
)

LIST_URL = reverse("social_media:profile-list")


def get_detailed_url(pk):
    return reverse("social_media:profile-detail", kwargs={"pk": pk})


my_profile_url = reverse("social_media:profile-me")


class UnauthenticatedUserTest(APITestCase):
    def test_forbidden_access(self):
        test_user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test12345",
        )
        detailed_url = get_detailed_url(test_user.profile.pk)

        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(detailed_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(detailed_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(detailed_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(detailed_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(my_profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(my_profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(my_profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(reverse("social_media:profile-following"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(reverse("social_media:profile-followers"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(
            reverse("social_media:profile-follow", kwargs={"pk": test_user.profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(TestAPIAuthenticatedUser):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user1 = get_user_model().objects.create_user(
            email="user1@example.com",
            password="test12345",
        )
        cls.user2 = get_user_model().objects.create_user(
            email="user2@example.com",
            password="test12345",
        )

        cls.user.profile.following.add(cls.user1.profile)
        cls.user.profile.followers.add(cls.user2.profile)

    def test_list(self):
        profiles = Profile.objects.all()
        profile_serializer = ProfileListRetrieveSerializer(profiles, many=True)

        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"], profile_serializer.data)

    def test_retrieve(self):
        response = self.client.get(get_detailed_url(self.user.profile.pk))

        user_profile = Profile.objects.get(pk=self.user.profile.pk)
        user_profile_serializer = ProfileListRetrieveSerializer(user_profile)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_profile_serializer.data)

    def test_create(self):
        response = self.client.post(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        response = self.client.put(get_detailed_url(self.user.profile.pk))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update(self):
        response = self.client.patch(get_detailed_url(self.user.profile.pk))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_destroy(self):
        response = self.client.delete(get_detailed_url(self.user.profile.pk))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_me_get(self):
        response = self.client.get(my_profile_url)

        my_profile_user = Profile.objects.get(pk=self.user.profile.pk)
        my_profile_user_serializer = ProfileListRetrieveSerializer(my_profile_user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_profile_user_serializer.data)

    def test_me_update(self):
        response = self.client.put(
            my_profile_url, {"username": "new username", "bio": "new bio"}
        )

        self.user.profile.refresh_from_db()
        my_profile_user_serializer = ProfileDetailedView(self.user.profile)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_profile_user_serializer.data)

    def test_me_partial_update(self):
        response = self.client.patch(my_profile_url, {"username": "new username"})

        self.user.profile.refresh_from_db()
        my_profile_user_serializer = ProfileDetailedView(self.user.profile)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_profile_user_serializer.data)

    def test_following(self):
        response = self.client.get(reverse("social_media:profile-following"))

        profile_following_serializer = ProfileFollowingSerializer(
            self.user.profile.following, many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], profile_following_serializer.data)

    def test_followers(self):
        response = self.client.get(reverse("social_media:profile-followers"))

        profile_following_serializer = ProfileFollowingSerializer(
            self.user.profile.followers, many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], profile_following_serializer.data)

    def test_follow(self):
        response = self.client.post(
            reverse("social_media:profile-follow", kwargs={"pk": self.user2.profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(
            self.user.profile.following.filter(pk=self.user2.profile.pk).exists()
        )

        response = self.client.post(
            reverse("social_media:profile-follow", kwargs={"pk": self.user2.profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.user.profile.following.filter(pk=self.user2.profile.pk).exists()
        )
