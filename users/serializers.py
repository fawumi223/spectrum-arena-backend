from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


# -------------------------------------------------------------------
# SIGNUP SERIALIZER (DEMO MODE: NO OTP)
# -------------------------------------------------------------------
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "full_name",
            "email",
            "phone_number",
            "password",
            "role",
        )

    def validate_role(self, value):
        """
        Accept lowercase or uppercase roles.
        Normalize to uppercase to match ROLE_CHOICES.
        """
        value = value.upper()
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {valid_roles}")
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        phone = attrs.get("phone_number")

        # Email is optional in demo mode
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email": "Email already exists."})

        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError({"phone_number": "Phone number already exists."})

        return attrs

    def create(self, validated_data):
        # Remove email if empty
        email = validated_data.get("email")
        if not email:
            validated_data.pop("email", None)

        password = validated_data.pop("password")

        # CORRECT WAY: pass password into create_user
        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


# -------------------------------------------------------------------
# LOGIN SERIALIZER (PHONE + PASSWORD → JWT)
# -------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone_number")
        password = attrs.get("password")

        # Authenticate using phone_number
        user = authenticate(phone_number=phone, password=password)

        if not user:
            raise serializers.ValidationError("Invalid phone number or password.")

        # RETURN USER OBJECT (view expects this)
        return {
            "user": user
        }


# -------------------------------------------------------------------
# JWT TOKEN SERIALIZER FOR /api/token/
# -------------------------------------------------------------------
class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "phone_number"

