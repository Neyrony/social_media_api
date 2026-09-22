from django.urls import reverse
from django.utils import dateformat

from core.tests.authenticated_test_case import TestAuthenticatedUser
from social_media.models import Post, Comment, Hashtag


class ProfileAdminTest(TestAuthenticatedUser):
    def test_display_profile(self):
        self.profile.bio = "Test bio"
        self.profile.save()

        url = reverse("admin:social_media_profile_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.profile.username)
        self.assertContains(response, self.profile.bio)
        self.assertContains(response, str(self.profile))


class HashtagAdminTest(TestAuthenticatedUser):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.hashtag = Hashtag.objects.create(name="Test hashtag")

    def test_display_hashtags(self):
        url = reverse("admin:social_media_hashtag_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.hashtag.name)


class PostsAdminTest(TestAuthenticatedUser):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.post = Post.objects.create(
            title="Test title",
            content="Test content",
            owner=cls.profile,
        )

    def test_display_posts(self):
        url = reverse("admin:social_media_post_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertContains(response, str(self.post.owner))
        self.assertContains(
            response, dateformat.format(self.post.created_at, "N j, Y, g:i a")
        )


class CommentsAdminTest(TestAuthenticatedUser):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.post = Post.objects.create(
            title="Test title",
            content="Test content",
            owner=cls.profile,
        )
        cls.comment = Comment.objects.create(
            content="Test comment",
            post=cls.post,
            owner=cls.profile,
        )

    def test_display_comments(self):
        url = reverse("admin:social_media_comment_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.comment.content)
        self.assertContains(response, str(self.comment.owner))
        self.assertContains(response, str(self.comment.post))
        self.assertContains(
            response, dateformat.format(self.comment.created_at, "N j, Y, g:i a")
        )
