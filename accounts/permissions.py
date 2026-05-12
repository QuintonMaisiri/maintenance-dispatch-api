"""Reusable, role-based permission classes."""
from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """Only Property Managers may pass."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_manager
        )


class IsStaffMember(permissions.BasePermission):
    """Only Maintenance Staff may pass."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff_member
        )


class IsResident(permissions.BasePermission):
    """Only Residents may pass."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_resident
        )