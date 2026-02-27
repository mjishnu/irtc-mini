from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration.
    Accepts name, email, password (+ confirmation), and optional profile fields.
    Returns the created user's data along with JWT tokens.
    """

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(
        write_only=True, min_length=8, label="Confirm password"
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
            "phone_number",
            "date_of_birth",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        # Run Django's AUTH_PASSWORD_VALIDATORS (min length, common, numeric, etc.)
        validate_password(attrs["password"])

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        """Append JWT tokens to the response."""
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data["tokens"] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return data


class LoginSerializer(serializers.Serializer):
    """
    Authenticates a user by email + password and returns JWT tokens.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        attrs["user"] = user
        return attrs

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
