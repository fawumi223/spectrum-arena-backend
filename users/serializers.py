from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


# ---------------------------------------------------------
# SIGNUP SERIALIZER
# ---------------------------------------------------------
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number", "password", "role"]

    def validate(self, attrs):
        email = attrs.get("email")
        phone = attrs.get("phone_number")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError({"phone_number": "Phone number already exists."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ---------------------------------------------------------
# LOGIN SERIALIZER (PHONE + PASSWORD)
# ---------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone_number")
        password = attrs.get("password")

        user = authenticate(username=phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password.")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "role": user.role,
            },
        }


# ---------------------------------------------------------
# JWT TOKEN SERIALIZER FOR /api/token/
# ---------------------------------------------------------
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "phone_number"

