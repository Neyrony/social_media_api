from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.authenticated_test_case import TestAPIAuthenticatedUser
from social_media.models import Comment, Post
from social_media.serializers import (
    CommentListSerializer,
    CommentRetrieveSerializer,
    CommentSerializer,
)


def get_list_url(post_pk):
    return reverse("social_media:post-comment-list", kwargs={"post_pk": post_pk})


def get_detailed_url(post_pk, pk):
    return reverse(
        "social_media:post-comment-detail", kwargs={"post_pk": post_pk, "pk": pk}
    )


class UnauthenticatedUserTest(APITestCase):
    def test_forbidden_access(self):
        test_user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test12345",
        )
        post = Post.objects.create(
            title="test title", content="test content", owner=test_user.profile
        )
        comment = Comment.objects.create(
            content="test comment", post=post, owner=test_user.profile
        )

        list_url = get_list_url(post.pk)
        detailed_url = get_detailed_url(post.pk, comment.pk)

        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(list_url)

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
        cls.my_comment = Comment.objects.create(
            content="test my comment",
            post=cls.my_post,
            owner=cls.user.profile,
        )
        cls.user_comment = Comment.objects.create(
            content="test user comment",
            post=cls.my_post,
            owner=cls.user1.profile,
        )

    def test_list(self):
        response = self.client.get(get_list_url(self.my_post.pk))

        all_comments = Comment.objects.filter(post=self.my_post)
        all_comments_serializer = CommentListSerializer(all_comments, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"], all_comments_serializer.data)

    def test_retrieve(self):
        response = self.client.get(
            get_detailed_url(self.my_post.pk, self.my_comment.pk)
        )

        my_comment_serializer = CommentRetrieveSerializer(self.my_comment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_comment_serializer.data)

    def test_create(self):
        response = self.client.post(
            get_list_url(post_pk=self.my_post.pk), {"content": "test comment"}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.get(pk=response.data["id"])

        self.assertEqual(comment.content, "test comment")
        self.assertEqual(comment.post, self.my_post)
        self.assertEqual(comment.owner, self.my_post.owner)

    def test_update(self):
        response = self.client.put(
            get_detailed_url(self.my_post.pk, self.user_comment.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(
            get_detailed_url(self.my_post.pk, self.my_comment.pk),
            {"content": "new test comment"},
        )

        self.my_comment.refresh_from_db()
        my_comment_serializer = CommentSerializer(self.my_comment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_comment_serializer.data)

    def test_partial_update(self):
        response = self.client.patch(
            get_detailed_url(self.my_post.pk, self.user_comment.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            get_detailed_url(self.my_post.pk, self.my_comment.pk),
            {"content": "new test comment"},
        )

        self.my_comment.refresh_from_db()
        my_comment_serializer = CommentSerializer(self.my_comment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, my_comment_serializer.data)

    def test_destroy(self):
        response = self.client.delete(
            get_detailed_url(self.my_post.pk, self.user_comment.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(
            get_detailed_url(self.my_post.pk, self.my_comment.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(pk=self.my_comment.pk)
