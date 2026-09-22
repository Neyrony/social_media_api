import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from social_media.models import Profile, Hashtag, Post, Comment


def create_profile():
    user = get_user_model().objects.create_user(
        email="test@example.com", password="password12345"
    )
    profile = Profile.objects.create(user=user, username="test", bio="test")
    return profile


class ProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.profile = create_profile()

    def test_str(self):
        self.assertEqual(str(self.profile), self.profile.username)


class HashtagTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.hashtag = Hashtag.objects.create(name="test")

    def test_str(self):
        self.assertEqual(str(self.hashtag), self.hashtag.name)


class PostTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        profile = create_profile()
        cls.post = Post.objects.create(
            title="test", content="test content", owner=profile
        )

    def test_str(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_validation(self):
        self.post.publish_at = timezone.now() + datetime.timedelta(minutes=5)
        self.post.full_clean()

        with self.assertRaises(ValidationError):
            self.post.publish_at = timezone.now() - datetime.timedelta(minutes=5)
            self.post.full_clean()


class CommentTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        profile = create_profile()
        post = Post.objects.create(title="test", content="test content", owner=profile)
        cls.comment = Comment.objects.create(
            content="test content", post=post, owner=profile
        )

    def test_str(self):
        self.assertEqual(str(self.comment), self.comment.content)
