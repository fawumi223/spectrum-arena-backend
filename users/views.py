from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction

from .serializers import SignupSerializer, LoginSerializer, PhoneTokenObtainPairSerializer
from payments.services.wallet import ensure_wallet_exists


# -------------------------------------------------------------------------
# SIGNUP VIEW (DEMO: AUTO VERIFY + AUTO WALLET + NO OTP)
# -------------------------------------------------------------------------
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()

            user.is_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save(update_fields=["is_verified", "otp", "otp_created_at"])

            ensure_wallet_exists(user)
            refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Signup successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "role": user.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# -------------------------------------------------------------------------
# LOGIN VIEW (PHONE + PASSWORD)
# -------------------------------------------------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)


# -------------------------------------------------------------------------
# JWT PHONE TOKEN VIEW (STANDARD /api/token/)
# -------------------------------------------------------------------------
class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer

