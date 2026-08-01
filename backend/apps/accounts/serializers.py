from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User

REGISTRABLE_ROLES = ["donor", "ngo", "institution", "execution_partner"]
# admin is deliberately excluded — ADR-003 / RBAC model: admin accounts
# are provisioned, never self-registered. Enforced here, not just by
# frontend UI omission.


class UserPublicSerializer(serializers.ModelSerializer):
    # Frontend's User.username is a display-name slot in this project's
    # contract (see mock data: "WaterHelp International", "Sarah Chen") —
    # backed here by full_name, not Django's internal username column.
    username = serializers.CharField(source="full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=REGISTRABLE_ROLES)

    class Meta:
        model = User
        fields = ["full_name", "email", "password", "role"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            role=validated_data["role"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(request, username=attrs["email"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.", code="authorization")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.", code="authorization")
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
