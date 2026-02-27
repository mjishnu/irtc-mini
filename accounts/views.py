from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class RegisterView(APIView):
    """
    POST /api/register/

    Create a new user account and return JWT tokens.
    Open to everyone (no authentication required).
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Accounts"],
        summary="Register a new user",
        description="Create a new user account and return JWT tokens. Open to everyone.",
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/login/

    Authenticate with email + password and receive JWT tokens.
    Open to everyone (no authentication required).
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Accounts"],
        summary="User Login",
        description="Authenticate with email + password and receive JWT tokens.",
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={
                    "email": serializers.EmailField(),
                    "role": serializers.CharField(),
                    "tokens": inline_serializer(
                        name="LoginTokens",
                        fields={
                            "refresh": serializers.CharField(),
                            "access": serializers.CharField(),
                        },
                    ),
                },
            )
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = serializer.get_tokens(user)
        return Response(
            {
                "email": user.email,
                "role": user.role,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )
