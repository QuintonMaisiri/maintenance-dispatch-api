from rest_framework import viewsets

from .models import MaintenanceRequest
from .permissions import MaintenanceRequestAccessPolicy
from .serializers import MaintenanceRequestSerializer


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """
    /api/requests/      GET (list), POST (residents create)
    /api/requests/<id>/ GET (retrieve), PATCH (managers any field, staff status)
                         DELETE (managers only)

    The queryset is scoped to what the caller is allowed to see so listing
    cannot leak rows. Object-level access is enforced by
    `MaintenanceRequestAccessPolicy`.
    """

    serializer_class = MaintenanceRequestSerializer
    permission_classes = [MaintenanceRequestAccessPolicy]

    def get_queryset(self):
        user = self.request.user

        # DRF needs a queryset of the right model even when the user is
        # anonymous (e.g. during schema generation).
        base = MaintenanceRequest.objects.select_related(
            'created_by', 'assigned_to'
        )

        if not user.is_authenticated:
            return base.none()

        if user.is_manager:
            return base.all()

        if user.is_staff_member:
            return base.filter(assigned_to=user)

        if user.is_resident:
            return base.filter(created_by=user)

        return base.none()

    def perform_create(self, serializer):
        # Server-side stamping - the resident cannot spoof another user.
        serializer.save(created_by=self.request.user)