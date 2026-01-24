from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    SignupSerializer,
    LoginSerializer,
    PhoneTokenObtainPairSerializer,
)
from payments.services.wallet import ensure_wallet_exists


# ---------------------------------------------------------
# SIGNUP (DEMO MODE – AUTO VERIFY + AUTO WALLET + NO OTP)
# ---------------------------------------------------------
@extend_schema(
    request=SignupSerializer,
    responses={201: OpenApiResponse(description="Signup successful")},
    tags=["Users"],
)
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = serializer.save()
                user.is_verified = True  # DEMO MODE
                user.save(update_fields=["is_verified"])

                ensure_wallet_exists(user)

                refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Signup successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "role": user.role,
                },
            }, status=201)

        except Exception as e:
            return Response(
                {"detail": f"Signup failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ---------------------------------------------------------
# LOGIN (PHONE + PASSWORD)
# ---------------------------------------------------------
@extend_schema(
    request=LoginSerializer,
    responses={200: OpenApiResponse(description="Login successful")},
    tags=["Auth"],
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)


# ---------------------------------------------------------
# JWT PHONE TOKEN (STANDARD /api/token/)
# ---------------------------------------------------------
@extend_schema(
    request=PhoneTokenObtainPairSerializer,
    responses={200: OpenApiResponse(description="JWT Token Pair")},
    tags=["Auth"],
)
class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer

