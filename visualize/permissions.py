from rest_framework import permissions
from visualize.models import *

class VisualizePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'X-AUTHORIZATION' in request.headers:
            authorization_key = request.headers['X-AUTHORIZATION']
            try:
                AuthorizationKey.objects.get(authorization_key=authorization_key)
            except AuthorizationKey.DoesNotExist:
                return False
            return True
        return False