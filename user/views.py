from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema, inline_serializer
from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView as JWTokenObtainPairView,
    TokenRefreshView as JWTokenRefreshView,
    TokenVerifyView as JWTokenVerifyView,
)

from user.serializers import UserSerializer, UserRetrieveSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Create a new user in the system",
        description="Create a new user and corresponding profile in the system",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
)
class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a user by it's id", responses={200: UserRetrieveSerializer}
    ),
    put=extend_schema(
        summary="Update current user",
        request=UserRetrieveSerializer,
        responses={200: UserRetrieveSerializer},
    ),
    patch=extend_schema(
        summary="Partially update current user",
        request=UserRetrieveSerializer,
        responses={200: UserRetrieveSerializer},
    ),
    delete=extend_schema(
        summary="Delete current user account and all corresponding data",
        request=None,
        responses={204: None},
    ),
)
class UserManagerView(RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRetrieveSerializer

    def get_object(self):
        return self.request.user


@extend_schema_view(
    post=extend_schema(
        summary="Logout user from service",
        description="Put refresh token in blacklist to logout user",
        request=inline_serializer(
            name="RefreshTokenDelete",
            fields={"refresh_token": serializers.CharField(help_text="Refresh token")},
        ),
        responses={
            204: None,
            400: inline_serializer(
                name="ErrorRefreshToken", fields={"error": serializers.CharField()}
            ),
        },
    )
)
class LogOutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token is None:
                return Response(
                    {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            refresh_token = RefreshToken(refresh_token)
            refresh_token.blacklist()
            return Response({"message": "success"}, status=HTTP_204_NO_CONTENT)
        except TokenError:
            return Response(
                {"error": "Token is invalid"}, status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    post=extend_schema(
        summary="Obtain access and refresh token by given credentials",
    )
)
class TokenObtainPairView(JWTokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Refresh access token by given refresh token",
    )
)
class TokenRefreshView(JWTokenRefreshView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Verify if access is valid or not",
    )
)
class TokenVerifyView(JWTokenVerifyView):
    pass
