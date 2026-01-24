from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# -------------------------------------------------------------------------
# SIGNUP SERIALIZER
# -------------------------------------------------------------------------
class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    otp_channel = serializers.ChoiceField(
        choices=["EMAIL", "PHONE"],
        default="PHONE",
        required=False
    )

    role = serializers.ChoiceField(
        choices=["client", "artisan", "company"],
        default="client"
    )

    def validate(self, data):
        phone = data["phone_number"]
        existing = User.objects.filter(phone_number=phone).first()
        if existing:
            self.context["existing"] = existing
        return data

    def create(self, validated_data):
        role_value = validated_data.get("role", "client").upper()
        email = validated_data.get("email") or None
        otp_channel = validated_data.get("otp_channel", "PHONE")

        existing = self.context.get("existing")

        if existing:
            existing.full_name = validated_data["full_name"]
            existing.email = email
            existing.role = role_value
            existing.set_password(validated_data["password"])
            existing.is_verified = True
            existing.otp = None
            existing.otp_created_at = None
            existing.otp_channel = otp_channel
            existing.save()
            return existing

        user = User.objects.create(
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            email=email,
            role=role_value,
            is_verified=True,
            otp_channel=otp_channel,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# -------------------------------------------------------------------------
# LOGIN SERIALIZER
# -------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["phone_number"],
            password=data["password"]
        )
        if not user:
            raise AuthenticationFailed("Invalid phone number or password.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "role": user.role,
            },
        }

