from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.utils.crypto import constant_time_compare

from .models import User
from .serializers import SignupSerializer, LoginSerializer

# SMS OTP (Temporarily disabled)
# from .utils_sms import send_sms_otp

# EMAIL OTP
from .utils_email import send_otp_email

# Wallet auto-init service
from payments.services.wallet import ensure_wallet_exists


# -------------------------------------------------------------------------
# SIGNUP VIEW (TEMP — NO OTP, NO EMAIL/SMS)
# -------------------------------------------------------------------------
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()

            # TEMP: Do not generate or send OTP
            user.is_verified = False
            user.otp = None
            user.otp_created_at = None
            user.save(update_fields=["is_verified", "otp", "otp_created_at"])

        return Response(
            {
                "message": "TEMP: Signup successful (no OTP sent)",
                "user_id": user.id,
                "otp_channel": None,
            },
            status=status.HTTP_201_CREATED,
        )


# -------------------------------------------------------------------------
# VERIFY OTP VIEW — TEMPORARY BYPASS FOR TESTING
# -------------------------------------------------------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"message": "User ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TEMP: bypass OTP verification
        user.is_verified = True
        user.otp = None
        user.otp_created_at = None
        user.save(update_fields=["is_verified", "otp", "otp_created_at"])

        # Auto create wallet
        ensure_wallet_exists(user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "TEMP: Verification bypassed",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "plan_type": user.plan_type,
                    "job_post_limit": user.job_post_limit,
                },
            },
            status=status.HTTP_200_OK,
        )


# -------------------------------------------------------------------------
# RESEND OTP VIEW (EMAIL ONLY)
# -------------------------------------------------------------------------
class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"message": "User ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_verified:
            return Response(
                {"message": "User already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = user.generate_otp(channel="EMAIL")

        # Disabled SMS → Using EMAIL
        # send_sms_otp(user.phone_number, otp)
        send_otp_email(user)

        return Response(
            {"message": "OTP resent via Email"},
            status=status.HTTP_200_OK,
        )


# -------------------------------------------------------------------------
# LOGIN VIEW
# -------------------------------------------------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

