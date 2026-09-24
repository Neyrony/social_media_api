from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_205_RESET_CONTENT, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers import UserSerializer


class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []


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
