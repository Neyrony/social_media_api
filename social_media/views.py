from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from social_media.models import Post, Profile
from social_media.pagination import BasePagination
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
    ProfileListRetrieveSerializer,
)


class PostViewSet(ModelViewSet):
    pagination_class = BasePagination
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.all()

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "owner__user",
            ).prefetch_related("liked_by")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)


class ProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Profile.objects.all()
    serializer_class = ProfileListRetrieveSerializer
