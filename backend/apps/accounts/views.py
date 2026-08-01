from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from grantloop.openapi import auth_token_schema, user_register_schema

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)
from .tokens import generate_password_reset_token, verify_password_reset_token

User = get_user_model()


def _tokens_for_user(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@user_register_schema
class RegisterView(APIView):
    """POST /auth/register/ — matches frontend authApi.register() exactly:
    returns {access, refresh, user}, same shape as login."""

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = _tokens_for_user(user)
        data["user"] = UserPublicSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)


@auth_token_schema
class LoginView(APIView):
    """POST /auth/login/ — {access, refresh, user}."""

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        data = _tokens_for_user(user)
        data["user"] = UserPublicSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"], summary="Logout and Blacklist Refresh Token")
class LogoutView(APIView):
    """POST /auth/logout/ — blacklists the refresh token. Best-effort by
    contract (frontend proceeds with local logout regardless), but this
    endpoint itself still reports failure clearly if the token is bad."""

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or already-expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Accounts"], summary="Retrieve Authenticated User Profile (Me)")
class MeView(RetrieveAPIView):
    """GET /auth/me/ — used by AuthContext to restore a session."""

    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=["Authentication"], summary="Request Password Reset Link via Email")
class PasswordResetRequestView(APIView):
    """POST /auth/password-reset/ — always returns 200 regardless of
    whether the email exists, per the frontend's own comment: "never
    reveal account existence through this form's response." """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        token = generate_password_reset_token(str(user.id))
        send_mail(
            subject="Reset your GrantLoop password",
            message=f"Use this token to reset your password: {token}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return Response(status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"], summary="Confirm and Reset Password with Token")
class PasswordResetConfirmView(APIView):
    """POST /auth/password-reset/confirm/ — {token, new_password}."""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = verify_password_reset_token(
            serializer.validated_data["token"], max_age=settings.PASSWORD_RESET_TIMEOUT
        )
        if not user_id:
            return Response(
                {"detail": "This reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(status=status.HTTP_200_OK)
