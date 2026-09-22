from django.conf import settings
from django.db import models

from social_media.validators import validate_publish_at


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    username = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True)
    # profile_picture = models.ImageField(null=True, upload_to=...)
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    # image = models.ImageField(null=True, upload_to=...)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="posts")
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    liked_by = models.ManyToManyField(Profile, related_name="liked_posts", blank=True)
    publish_at = models.DateTimeField(
        null=True, blank=True, validators=[validate_publish_at]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="comments"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.content
