from rest_framework import permissions
from .membership_status import member_status_checker

class IsActiveMember(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        return member_status_checker.user_is_active_member(request.user.email)
