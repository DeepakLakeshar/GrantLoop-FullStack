from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserPublicSerializer
from .models import ExecutionPartner


class ExecutionPartnerListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = ExecutionPartner
        fields = ["id", "user", "organization", "verification_status"]
        read_only_fields = fields


class ExecutionPartnerDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = ExecutionPartner
        fields = ["id", "user", "organization", "verification_status"]
        read_only_fields = fields


class ExecutionPartnerWriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = ExecutionPartner
        fields = ["user", "organization"]

