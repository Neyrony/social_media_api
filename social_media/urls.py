from django.urls import include, path
from rest_framework import routers

from social_media.views import PostViewSet, ProfileViewSet

social_media_router = routers.DefaultRouter()
social_media_router.register("posts", PostViewSet, basename="post")
social_media_router.register("profiles", ProfileViewSet, basename="profile")

urlpatterns = [path("", include(social_media_router.urls))]

app_name = "social_media"
