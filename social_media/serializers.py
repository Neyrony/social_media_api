from django.core.exceptions import ValidationError
from rest_framework import serializers

from social_media.models import Post, Profile, Comment
from social_media.validators import validate_publish_at


class EmptySerializer(serializers.Serializer):
    pass


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user", "username", "bio", "profile_picture", "following")
        read_only_fields = ("id", "user")
        extra_kwargs = {
            "following": {"style": {"base_template": "checkbox_multiple.html"}}
        }


class ProfileDetailedView(ProfileSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "username",
            "bio",
            "profile_picture",
        )
        read_only_fields = ("id", "user")


class ProfileListRetrieveSerializer(ProfileSerializer):
    user = serializers.StringRelatedField(read_only=True)
    following = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )


class ProfileFollowingSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = ("id", "username", "bio", "profile_picture")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "image",
            "owner",
            "liked_by",
            "created_at",
            "publish_at",
        )
        read_only_fields = ("id", "owner", "liked_by", "created_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.owner != self.context["request"].user.profile:
            data.pop("publish_at", None)

        return data

    def validate_publish_at(self, value):
        return validate_publish_at(value, ValidationError, self.instance)


class PostListSerializer(PostSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    liked_by = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )

    class Meta(PostSerializer.Meta):
        extra_kwargs = {
            "created_at": {"format": "%d.%m.%Y %H:%M"},
            "publish_at": {"format": "%d.%m.%Y %H:%M"},
        }


class PostRetrieveSerializer(PostSerializer):
    owner = ProfileListRetrieveSerializer(read_only=True)
    liked_by = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("publish_at",)
        extra_kwargs = {
            "created_at": {"format": "%d.%m.%Y %H:%M"},
            "publish_at": {"format": "%d.%m.%Y %H:%M"},
        }


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.filter(is_published=True)
    )

    class Meta:
        model = Comment
        fields = ("content", "created_at", "post", "owner")
        read_only_fields = ("id", "post", "owner")


class CommentListSerializer(CommentSerializer):
    owner_username = serializers.CharField(read_only=True, source="owner.username")
    post_title = serializers.CharField(read_only=True, source="post.title")

    class Meta(CommentSerializer.Meta):
        fields = ("content", "created_at", "post_title", "owner_username")


class CommentRetrieveSerializer(CommentSerializer):
    owner = ProfileListRetrieveSerializer(read_only=True)
    post = serializers.SlugRelatedField(read_only=True, slug_field="title")
