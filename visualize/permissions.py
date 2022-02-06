from rest_framework import permissions
from visualize.utils import decode_authorization_key

class VisualizePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        authorization_key = request.headers.get('X-Authorization')
        try:
            decode_authorization_key(authorization_key)
            return True
        except Exception as e:
            self.message = e.args[0]
            return False
