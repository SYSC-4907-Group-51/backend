from rest_framework import permissions

class IsAuthenticated(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        """
            Default permisson class. To bypass authorization header
            from OPTION requests

            Args:
                request: request dict

            Return:
                bool: True for is authenticated, False otherwise
        """
        if request.method == 'OPTIONS':
            return True
        return super(IsAuthenticated, self).has_permission(request, view)