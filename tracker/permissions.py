from rest_framework import permissions

class AuthorizationPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        """
            Permission class for 
                /auth
            POST method to generate authorization URL requires authorization
            header
            GET method (redirecting from Fitbit) cannot contain authorization
            header, thus bypass it

            Args:
                request: user request

            Return:
                bool: True for is authenticated, False otherwise
        """
        if request.method == 'OPTIONS':
            return True
        if request.method == "POST":
            if request.user.is_authenticated:
                return True
            else:
                return False
        elif request.method == "GET":
            return True