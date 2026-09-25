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
    ProfileFollowingSerializer,
    EmptySerializer,
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
    pagination_class = BasePagination

    def get_queryset(self):
        queryset = Profile.objects.all()

        if self.action in ("list", "retrieve", "me"):
            queryset = queryset.select_related("user").prefetch_related("following")

            if self.action == "list":
                username = self.request.query_params.get("username")

                if username:
                    queryset = queryset.filter(username__icontains=username)
        elif self.action == "following":
            queryset = self.request.user.profile.following.all()
        elif self.action == "followers":
            queryset = self.request.user.profile.followers.all()

        return queryset

    def get_serializer_class(self):
        if self.action == "me" and self.request.method in ("PUT", "PATCH"):
            return ProfileSerializer
        elif self.action in ("following", "followers"):
            return ProfileFollowingSerializer
        elif self.action == "follow":
            return EmptySerializer
        return ProfileListRetrieveSerializer

    @action(detail=False, methods=["GET", "PUT", "PATCH"])
    def me(self, request):
        user_profile = self.get_queryset().get(user=self.request.user)

        if request.method == "GET":
            user_profile_serializer = self.get_serializer(user_profile)

            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PUT":
            user_profile_serializer = self.get_serializer(
                user_profile, data=request.data
            )
            user_profile_serializer.is_valid(raise_exception=True)
            user_profile_serializer.save(user=self.request.user)

            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PATCH":
            user_profile_serializer = self.get_serializer(
                user_profile, data=request.data, partial=True
            )
            user_profile_serializer.is_valid(raise_exception=True)
            user_profile_serializer.save(user=self.request.user)

            return Response(user_profile_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="me/following")
    def following(self, request):
        following = self.get_queryset()
        page = self.paginate_queryset(following)
        following_serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(following_serializer.data)

    @action(detail=False, methods=["GET"], url_path="me/followers")
    def followers(self, request):
        followers = self.get_queryset()
        page = self.paginate_queryset(followers)
        followers_serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(followers_serializer.data)

    @action(detail=True, methods=["POST"])
    def follow(self, request, pk):
        user_profile = self.request.user.profile
        following_profile = self.get_object()
        is_followed = user_profile.following.filter(pk=pk).exists()

        if not is_followed:
            user_profile.following.add(following_profile)
        else:
            user_profile.following.remove(following_profile)

        return Response(status=status.HTTP_200_OK)
