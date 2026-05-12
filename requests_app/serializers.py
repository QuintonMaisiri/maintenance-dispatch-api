from rest_framework import serializers

from accounts.models import User
from accounts.serializers import UserSerializer

from .models import MaintenanceRequest


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """
    Field-level rules:

    * `created_by` is always set by the server (the requesting user).
    * `assigned_to` is writable ONLY by managers; the input field is
      `assigned_to_id` (a Staff user id). Nested `assigned_to` is read-only.
    * `status`:
        - Managers can set any status.
        - Staff can change status freely on their own tickets.
        - Residents cannot change status.
    * Anything else a non-manager tries to PATCH is rejected.
    """

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    assigned_to_id = serializers.PrimaryKeyRelatedField(
        source='assigned_to',
        queryset=User.objects.filter(role=User.Role.STAFF),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id',
            'title',
            'description',
            'status',
            'created_by',
            'assigned_to',
            'assigned_to_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    # ------------------------------------------------------------------ create
    def create(self, validated_data):
        # The view sets created_by via perform_create; status is always Pending.
        validated_data['status'] = MaintenanceRequest.Status.PENDING
        validated_data.pop('assigned_to', None)
        return super().create(validated_data)

    # ------------------------------------------------------------------ update
    def validate(self, attrs):
        request = self.context.get('request')
        if request is None or self.instance is None:
            return attrs  # creation path - rules above already handled it

        user = request.user

        # Managers: anything goes.
        if user.is_manager:
            return attrs

        # Staff: only `status` is allowed in the payload.
        if user.is_staff_member:
            allowed = {'status'}
            disallowed = set(attrs.keys()) - allowed
            if disallowed:
                raise serializers.ValidationError({
                    field: 'Maintenance staff may only change `status`.'
                    for field in disallowed
                })
            return attrs

        # Residents (and anything else): no edits.
        raise serializers.ValidationError(
            'You do not have permission to modify this request.'
        )