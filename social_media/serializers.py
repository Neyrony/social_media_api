from rest_framework import serializers

from social_media.models import Post, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user", "username", "bio", "profile_picture", "following")


class ProfileListSerializer(ProfileSerializer):
    user = serializers.StringRelatedField(read_only=True)
    following = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )


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
        )
        extra_kwargs = {
            "liked_by": {"style": {"base_template": "checkbox_multiple.html"}}
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.owner == self.context["request"].user:
            data.pop("publish_at", None)

        return data


class PostListSerializer(PostSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    liked_by = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )

    class Meta(PostSerializer.Meta):
        extra_kwargs = {"created_at": {"format": "%d.%m.%Y %H:%M"}}


class PostRetrieveSerializer(PostSerializer):
    owner = ProfileListSerializer(read_only=True)
    liked_by = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("publish_at",)
        extra_kwargs = {
            "created_at": {"format": "%d.%m.%Y %H:%M"},
            "publish_at": {"format": "%d.%m.%Y %H:%M"},
        }
