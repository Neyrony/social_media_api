from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import UserCreateView, LogOutAPIView, UserManagerView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", LogOutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("token/verify/", TokenVerifyView.as_view(), name="verify-token"),
    path("me/", UserManagerView.as_view(), name="personal-info"),
]

app_name = "user"
