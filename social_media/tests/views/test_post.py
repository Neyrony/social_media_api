from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from core.tests.authenticated_test_case import TestAPIAuthenticatedUser
from social_media.models import Post
from social_media.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
)

LIST_URL = reverse("social_media:post-list")


def get_detailed_url(pk):
    return reverse("social_media:post-detail", kwargs={"pk": pk})


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

        cls.my_post = Post.objects.create(
            title="test my title",
            content="test my content",
            owner=cls.user.profile,
        )
        cls.following_post = Post.objects.create(
            title="test following title",
            content="test following content",
            owner=cls.user1.profile,
        )

    def test_list(self):
        posts = Post.objects.all()

        factory = APIRequestFactory()
        request = factory.get(LIST_URL)
        request.user = self.user

        post_serializer = PostListSerializer(
            posts, many=True, context={"request": request}
        )

        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"], post_serializer.data)

    def test_retrieve(self):
        detailed_url = get_detailed_url(self.my_post.pk)
        response = self.client.get(detailed_url)

        post = Post.objects.get(pk=self.my_post.pk)

        factory = APIRequestFactory()
        request = factory.get(detailed_url)
        request.user = self.user

        post_serializer = PostRetrieveSerializer(post, context={"request": request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, post_serializer.data)

    def test_create(self):
        data = {
            "title": "title",
            "content": "content",
            "hashtags": [{"name": "hashtag"}],
        }
        response = self.client.post(LIST_URL, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_post = Post.objects.get(pk=response.data["id"])

        for key, value in data.items():
            with self.subTest(info=key):
                if key != "hashtags":
                    self.assertEqual(value, getattr(new_post, key))

        self.assertTrue(new_post.hashtags.filter(name="hashtag").exists())

    def test_update(self):
        response = self.client.put(get_detailed_url(self.following_post.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(
            get_detailed_url(self.my_post.pk),
            data={
                "title": "new title",
                "content": "new content",
            },
        )

        factory = APIRequestFactory()
        request = factory.put(get_detailed_url(self.my_post.pk))
        request.user = self.user

        self.my_post.refresh_from_db()

        my_post_serializer = PostSerializer(self.my_post, context={"request": request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_post_serializer.data)

    def test_partial_update(self):
        response = self.client.patch(get_detailed_url(self.following_post.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        factory = APIRequestFactory()
        request = factory.patch(get_detailed_url(self.my_post.pk))
        request.user = self.user

        response = self.client.patch(
            get_detailed_url(self.my_post.pk), data={"title": "new title"}
        )

        self.my_post.refresh_from_db()

        my_post_serializer = PostSerializer(
            self.my_post,
            context={"request": request},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_post_serializer.data)

    def test_destroy(self):
        response = self.client.delete(get_detailed_url(self.following_post.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(get_detailed_url(self.my_post.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(pk=self.my_post.pk)

    def test_my_post(self):
        my_posts_url = reverse("social_media:post-my-posts")

        response = self.client.get(my_posts_url)

        factory = APIRequestFactory()
        request = factory.get(my_posts_url)
        request.user = self.user

        my_posts = Post.objects.filter(owner=self.user.profile)
        my_posts_serializer = PostListSerializer(
            my_posts, many=True, context={"request": request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], my_posts_serializer.data)

    def test_following(self):
        my_posts_url = reverse("social_media:post-following")

        response = self.client.get(my_posts_url)

        factory = APIRequestFactory()
        request = factory.get(my_posts_url)
        request.user = self.user

        following_posts = Post.objects.filter(
            owner__in=self.user.profile.following.all()
        )
        following_posts_serializer = PostListSerializer(
            following_posts, many=True, context={"request": request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], following_posts_serializer.data)

    def test_like(self):
        like_url = reverse(
            "social_media:post-like", kwargs={"pk": self.following_post.pk}
        )

        response = self.client.post(like_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(
            self.following_post.liked_by.filter(pk=self.user.profile.pk).exists()
        )

        response = self.client.post(like_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.following_post.liked_by.filter(pk=self.user.profile.pk).exists()
        )

    def test_liked(self):
        liked_posts_url = reverse("social_media:post-liked")

        self.following_post.liked_by.add(self.user.profile)

        response = self.client.get(liked_posts_url)

        factory = APIRequestFactory()
        request = factory.get(liked_posts_url)
        request.user = self.user

        liked_posts = self.user.profile.liked_posts.all()
        liked_posts_serializer = PostListSerializer(
            liked_posts, many=True, context={"request": request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], liked_posts_serializer.data)
