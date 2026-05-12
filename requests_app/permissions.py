"""
Row-level access policy for MaintenanceRequest.

Two layers of defence:

  1. `MaintenanceRequestViewSet.get_queryset` returns *only* the rows the
     caller is allowed to see, so listing is naturally scoped.
  2. `MaintenanceRequestAccessPolicy` below also enforces per-action and
     per-object checks, so a resident who guesses an ID still gets 404/403.

Both layers are required: defence in depth.
"""
from rest_framework import permissions


SAFE_METHODS = permissions.SAFE_METHODS  # ('GET', 'HEAD', 'OPTIONS')


class MaintenanceRequestAccessPolicy(permissions.BasePermission):

    # -- Action / verb level --------------------------------------------------
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        action = getattr(view, 'action', None)

        if user.is_manager:
            # Managers can do everything.
            return True

        if user.is_resident:
            # Residents may list/retrieve (their own) and create new tickets.
            # They may NOT update or delete tickets - even their own.
            return action in {'list', 'retrieve', 'create'}

        if user.is_staff_member:
            # Staff may list/retrieve (their assigned tickets) and update
            # the status. They cannot create or delete.
            return action in {'list', 'retrieve', 'update', 'partial_update'}

        return False

    # -- Row level ------------------------------------------------------------
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_manager:
            return True

        if user.is_resident:
            # Residents can only ever touch (read) their own requests.
            if request.method in SAFE_METHODS:
                return obj.created_by_id == user.id
            return False

        if user.is_staff_member:
            # Staff can only see/edit requests assigned to *them*.
            return obj.assigned_to_id == user.id

        return False