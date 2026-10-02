from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter

from social_media.views import PostViewSet, ProfileViewSet, CommentViewSet

social_media_router = routers.DefaultRouter()
social_media_router.register("posts", PostViewSet, basename="post")
social_media_router.register("profiles", ProfileViewSet, basename="profile")
post_router = NestedDefaultRouter(social_media_router, "posts", lookup="post")
post_router.register("comments", CommentViewSet, basename="post-comment")

urlpatterns = [
    path("", include(social_media_router.urls)),
    path("", include(post_router.urls)),
]

app_name = "social_media"
