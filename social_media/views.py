from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from social_media.models import Post, Profile
from social_media.pagination import BasePagination
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
    ProfileListRetrieveSerializer,
    ProfileSerializer,
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

    def get_serializer_class(self):
        if self.action == "me" and self.request.method in ("PUT", "PATCH"):
            return ProfileSerializer
        return ProfileListRetrieveSerializer

    @action(detail=False, methods=["GET", "PUT", "PATCH"])
    def me(self, request):
        user_profile = request.user.profile

        if request.method == "GET":
            user_profile_serializer = self.get_serializer(user_profile)

            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PUT":
            user_profile_serializer = self.get_serializer(
                user_profile, data=request.data
            )
            user_profile_serializer.is_valid(raise_exception=True)
            user_profile_serializer.save()

            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PATCH":
            user_profile_serializer = self.get_serializer(
                user_profile, data=request.data, partial=True
            )
            user_profile_serializer.is_valid(raise_exception=True)
            user_profile_serializer.save()

            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)
