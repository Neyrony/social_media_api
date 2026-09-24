import pathlib
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify

from social_media.validators import validate_publish_at


@deconstructible
class ImagePath:
    def __init__(self, path_to_store: str, field: str):
        self.path_to_store = path_to_store
        self.field = field

    def __call__(self, instance, filename) -> pathlib.Path:
        filename = f"{slugify(getattr(instance, self.field))}-{uuid.uuid4()}{pathlib.Path(filename).suffix}"
        return pathlib.Path(self.path_to_store) / pathlib.Path(filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    username = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        null=True,
        upload_to=ImagePath(path_to_store="profile_picture/uploads/", field="username"),
    )
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
    image = models.ImageField(
        null=True, blank=True, upload_to=ImagePath("posts/uploads/", field="title")
    )
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="posts")
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    liked_by = models.ManyToManyField(Profile, related_name="liked_posts", blank=True)
    publish_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        instance_to_check = self if self.pk is not None else None
        validate_publish_at(self.publish_at, ValidationError, instance_to_check)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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
