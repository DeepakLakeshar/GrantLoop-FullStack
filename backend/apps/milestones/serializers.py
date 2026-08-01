from rest_framework import serializers

from .models import Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Milestone
        fields = [
            "id", "campaign", "title", "description", "target_amount",
            "released_amount", "status", "order", "deadline", "completed_at",
            "completion_percentage", "created_at",
        ]
        # released_amount and status change only through the service layer
        # (transition_status) — never a direct field write. released_amount
        # in particular is meant to become a derived sum once FundRelease
        # exists (Reconciliation v1.1) — already read-only here in
        # anticipation of that, not a new decision.
        read_only_fields = ["id", "released_amount", "status", "completed_at", "created_at"]

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("target_amount must be greater than 0.")
        return value


class MilestoneReorderSerializer(serializers.Serializer):
    ordered_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class MilestoneStatusTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["in_progress", "completed"])
