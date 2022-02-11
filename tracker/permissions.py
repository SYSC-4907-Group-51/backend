from rest_framework import permissions

class AuthorizationPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        if request.method == "POST":
            if request.user.is_authenticated:
                return True
            else:
                return False
        elif request.method == "GET":
            return True