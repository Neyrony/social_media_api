from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from social_media.models import Post, Profile, Comment, Hashtag
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


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}


class PostSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, allow_empty=True, required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "image",
            "hashtags",
            "owner",
            "liked_by",
            "created_at",
            "publish_at",
            "is_published",
        )
        read_only_fields = ("id", "owner", "liked_by", "created_at", "is_published")
        extra_kwargs = {
            "hashtags": {"style": {"base_template": "checkbox_multiple.html"}}
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.owner != self.context["request"].user.profile:
            data.pop("publish_at", None)
            data.pop("is_published", None)

        return data

    def validate_publish_at(self, value):
        return validate_publish_at(value, ValidationError, self.instance)

    @transaction.atomic
    def create(self, validated_data):
        hashtags = validated_data.pop("hashtags", None)
        post = super().create(validated_data)
        if hashtags is not None:
            for hashtag_data in hashtags:
                hashtag, _ = Hashtag.objects.get_or_create(**hashtag_data)
                post.hashtags.add(hashtag)

        return post

    @transaction.atomic
    def update(self, instance, validated_data):
        hashtags = validated_data.pop("hashtags", None)
        instance = super().update(instance, validated_data)
        if hashtags is not None:
            instance.hashtags.clear()
            for hashtag_data in hashtags:
                hashtag, _ = Hashtag.objects.get_or_create(**hashtag_data)
                instance.hashtags.add(hashtag)

        return instance


class PostListSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
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
    hashtags = HashtagSerializer(many=True, read_only=True, allow_empty=True)
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
    class Meta:
        model = Comment
        fields = ("id", "content", "created_at", "post", "owner")
        read_only_fields = ("id", "post", "owner")
        extra_kwargs = {"created_at": {"format": "%d.%m.%Y %H:%M"}}


class CommentListSerializer(CommentSerializer):
    owner_username = serializers.CharField(read_only=True, source="owner.username")

    class Meta(CommentSerializer.Meta):
        fields = ("id", "content", "created_at", "owner_username")


class CommentRetrieveSerializer(CommentSerializer):
    owner = ProfileListRetrieveSerializer(read_only=True)
    post = serializers.SlugRelatedField(read_only=True, slug_field="title")
