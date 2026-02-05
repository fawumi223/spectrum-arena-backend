from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    SignupSerializer,
    LoginSerializer,
    PhoneTokenObtainPairSerializer,
)

# Wallet import kept (we'll re-enable later safely)
from payments.services.wallet import ensure_wallet_exists


# ---------------------------------------------------------
# SIGNUP (PUBLIC)
# ---------------------------------------------------------
@method_decorator(csrf_exempt, name="dispatch")
@extend_schema(
    request=SignupSerializer,
    responses={201: OpenApiResponse(description="Signup successful")},
    tags=["Users"],
    auth=None,
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

                # Demo-safe: auto verify user
                user.is_verified = True
                user.save(update_fields=["is_verified"])

                # --------------------------------------------------
                # TEMP DISABLED — wallet causing Railway crash
                # --------------------------------------------------
                # ensure_wallet_exists(user)
                # --------------------------------------------------

                # Generate JWT tokens
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

        except Exception as e:
            return Response(
                {"detail": f"Signup failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ---------------------------------------------------------
# LOGIN (PUBLIC)
# ---------------------------------------------------------
@method_decorator(csrf_exempt, name="dispatch")
@extend_schema(
    request=LoginSerializer,
    responses={200: OpenApiResponse(description="Login successful")},
    tags=["Auth"],
    auth=None,
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# ---------------------------------------------------------
# JWT /token/ (PUBLIC)
# ---------------------------------------------------------
@extend_schema(
    request=PhoneTokenObtainPairSerializer,
    responses={200: OpenApiResponse(description="JWT Token Pair")},
    tags=["Auth"],
    auth=None,
)
class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer

