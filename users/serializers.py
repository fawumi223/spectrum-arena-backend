from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

# -------------------------------------------------------------------------
# SIGNUP SERIALIZER (OTP-AWARE — FINAL)
# -------------------------------------------------------------------------
class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    otp_channel = serializers.ChoiceField(choices=["EMAIL", "PHONE"])
    email = serializers.EmailField(required=False, allow_null=True)

    def validate(self, data):
        phone = data["phone_number"]
        otp_channel = data["otp_channel"]
        email = data.get("email")

        # Email required if OTP via email
        if otp_channel == "EMAIL" and not email:
            raise serializers.ValidationError(
                {"email": "Email is required for email OTP"}
            )

        # Check existing
        existing_user = User.objects.filter(phone_number=phone).first()

        if existing_user:
            if existing_user.is_verified:
                raise serializers.ValidationError(
                    {"phone_number": "Account already exists. Please log in instead."}
                )
            # Unverified user -> allow update/resend
            self.context["existing_user"] = existing_user

        return data

    def create(self, validated_data):
        existing_user = self.context.get("existing_user")

        if existing_user:
            existing_user.full_name = validated_data["full_name"]
            existing_user.email = validated_data.get("email")
            existing_user.set_password(validated_data["password"])
            existing_user.save()
            return existing_user

        user = User.objects.create(
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            email=validated_data.get("email"),
            is_verified=False,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# -------------------------------------------------------------------------
# LOGIN SERIALIZER
# -------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get("phone_number")
        password = data.get("password")

        user = authenticate(
            username=phone,  # MUST match USERNAME_FIELD
            password=password
        )

        if not user:
            raise AuthenticationFailed("Invalid phone number or password.")

        if not user.is_verified:
            raise AuthenticationFailed(
                "Account not verified. Please verify OTP first."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "plan_type": user.plan_type,
                "job_post_limit": user.job_post_limit,
            },
        }

