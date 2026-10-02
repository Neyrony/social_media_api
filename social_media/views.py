from django.db.models import Q
from drf_spectacular.utils import extend_schema_view, OpenApiParameter, extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from social_media.models import Post, Profile, Comment
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
    ProfileListRetrieveSerializer,
    ProfileFollowingSerializer,
    EmptySerializer,
    ProfileDetailedView,
    CommentListSerializer,
    CommentSerializer,
    CommentRetrieveSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all posts",
        description="Show list all posts that can be filtered by hashtags",
        parameters=[
            OpenApiParameter(
                name="hashtags",
                type=str,
                description="Filter by hashtags",
                location="query",
                required=False,
            ),
        ],
        responses=PostListSerializer,
    ),
    retrieve=extend_schema(
        summary="Show particular post by id",
        description="Show detailed information about a post",
        responses="PostRetrieveSerializer",
    ),
    create=extend_schema(
        summary="Create a new post",
        description="Create a new post with given data",
        request=PostSerializer,
        responses={201: PostSerializer},
    ),
    update=extend_schema(
        summary="Update an existing post",
        description="Update an existing post with given data",
        request=PostSerializer,
        responses={200: PostSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update an existing post",
        description="Partially update an existing post with given data",
        request=PostSerializer,
        responses={200: PostSerializer},
    ),
    destroy=extend_schema(
        summary="Destroy an existing post",
        description="Destroy an existing post by its id",
        request=None,
        responses={204: None},
    ),
    my_posts=extend_schema(
        summary="Show list of all users's posts",
        request=None,
        responses={200: PostListSerializer},
    ),
    following=extend_schema(
        summary="Show list of posts from user's following",
        request=None,
        responses={200: PostListSerializer},
    ),
    like=extend_schema(
        summary="Press like on the particular video",
        request=None,
        responses={204: None},
    ),
    liked=extend_schema(
        summary="Show list of posts that user liked",
        request=None,
        responses={200: PostListSerializer},
    ),
)
class PostViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @staticmethod
    def _str_to_int_list(hashtag_str: str) -> list:
        try:
            return [int(hashtag_id.strip()) for hashtag_id in hashtag_str.split(",")]
        except ValueError:
            return []

    def get_queryset(self):
        queryset = Post.objects.all()

        if self.action == "list":
            queryset = queryset.filter(is_published=True)
        elif self.action == "my_posts":
            queryset = queryset.filter(owner=self.request.user.profile)
        elif self.action == "following":
            queryset = queryset.filter(
                owner__in=self.request.user.profile.following.all()
            )
        elif self.action == "liked":
            queryset = queryset.filter(liked_by=self.request.user.profile)
        else:
            queryset = queryset.filter(
                Q(is_published=True) | Q(owner=self.request.user.profile)
            )

        if self.action in ("list", "retrieve", "my_posts", "following", "liked"):
            queryset = queryset.select_related(
                "owner__user",
            ).prefetch_related("liked_by", "hashtags")

        if self.action == "list":
            hashtag_str = self.request.query_params.get("hashtags")
            if hashtag_str is not None:
                hashtag_list = self._str_to_int_list(hashtag_str)
                queryset = queryset.filter(hashtags__in=hashtag_list)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "my_posts", "following", "liked"):
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        elif self.action == "like":
            return EmptySerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    @action(detail=False, methods=["GET"], url_path="my")
    def my_posts(self, request):
        my_posts = self.get_queryset()
        page = self.paginate_queryset(my_posts)
        my_posts_serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(my_posts_serializer.data)

    @action(detail=False, methods=["GET"])
    def following(self, request):
        following_post = self.get_queryset()
        page = self.paginate_queryset(following_post)
        following_post_serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(following_post_serializer.data)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def like(self, request, pk):
        post = self.get_object()
        user_profile = self.request.user.profile

        is_liked = post.liked_by.filter(id=user_profile.id).exists()

        if is_liked:
            post.liked_by.remove(user_profile)
        else:
            post.liked_by.add(user_profile)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"])
    def liked(self, request):
        liked_post = self.get_queryset()
        page = self.paginate_queryset(liked_post)
        liked_post_serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(liked_post_serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Show list of comments",
        description="Show list of comment related to particular post",
        responses={200: CommentListSerializer},
    ),
    retrieve=extend_schema(
        summary="Show particular comment by id",
        description="Show detailed information about a comment related to particular post",
    ),
    create=extend_schema(
        summary="Create a new comment",
        description="Create a new comment that connected to post",
        request=CommentSerializer,
        responses={200: CommentSerializer},
    ),
    update=extend_schema(
        summary="Update existing comment",
        request=CommentSerializer,
        responses={200: CommentSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update existing comment",
        request=CommentSerializer,
        responses={200: CommentSerializer},
    ),
    destroy=extend_schema(
        summary="Destroy existing comment", request=None, responses={204: None}
    ),
)
class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.filter(post_id=self.kwargs.get("post_pk"))

        if self.action == "list":
            queryset = queryset.select_related("owner")
        elif self.action == "retrieve":
            queryset = queryset.select_related("owner__user")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        elif self.action == "retrieve":
            return CommentRetrieveSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(
            post_id=self.kwargs.get("post_pk"), owner=self.request.user.profile
        )


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all profiles",
        responses={200: ProfileListRetrieveSerializer},
    ),
    retrieve=extend_schema(
        summary="Show particular profile by id",
        description="Show detailed information about profile",
    ),
    me=[
        extend_schema(
            methods=["GET"],
            summary="Show detailed info about user's profile",
            responses={200: ProfileListRetrieveSerializer},
        ),
        extend_schema(
            methods=["PUT"],
            summary="Update detailed info about user's profile",
            request=ProfileDetailedView,
            responses={200: ProfileDetailedView},
        ),
        extend_schema(
            methods=["PATCH"],
            summary="Partially update detailed info about user's profile",
            request=ProfileDetailedView,
            responses={200: ProfileDetailedView},
        ),
    ],
    following=extend_schema(
        summary="Show all profiles that user follows",
        responses={200: ProfileFollowingSerializer},
    ),
    followers=extend_schema(
        summary="Show all profiles that follows user",
        responses={200: ProfileFollowingSerializer},
    ),
    follow=extend_schema(
        summary="Follow user(profile) to particular profile",
        description="Change follow status to opposite",
        request=EmptySerializer,
        responses={200: EmptySerializer},
    ),
)
class ProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
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
            return ProfileDetailedView
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
        if user_profile.id == following_profile.id:
            return Response(
                {"detail": "You cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not is_followed:
            user_profile.following.add(following_profile)
        else:
            user_profile.following.remove(following_profile)

        return Response(status=status.HTTP_204_NO_CONTENT)
