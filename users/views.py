from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from .models import User
from .serializers import SignupSerializer, LoginSerializer

# Wallet auto-init service
from payments.services.wallet import ensure_wallet_exists


# -------------------------------------------------------------------------
# SIGNUP VIEW (TEMP — NO OTP SENT)
# -------------------------------------------------------------------------
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()

            # TEMP: OTP bypass mode
            user.is_verified = False
            user.otp = None
            user.otp_created_at = None
            user.save(update_fields=["is_verified", "otp", "otp_created_at"])

        return Response(
            {
                "message": "TEMP: Signup successful (OTP bypassed)",
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


# -------------------------------------------------------------------------
# VERIFY VIEW (TEMP — AUTO VERIFY)
# -------------------------------------------------------------------------
class VerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"message": "User ID is required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        # TEMP: auto verify user
        user.is_verified = True
        user.otp = None
        user.otp_created_at = None
        user.save(update_fields=["is_verified", "otp", "otp_created_at"])

        # Auto-create wallet
        ensure_wallet_exists(user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "TEMP: User verified automatically",
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
            status=200,
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
        return Response(serializer.validated_data, status=200)

