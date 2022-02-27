from rest_framework import permissions
from visualize.utils import decode_authorization_key

class VisualizePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        """
            Permission class for 
                /time-series
                /intraday
            By pass OPTIONS method.
            Determine the access based on the key presented in the `X-Authorization` header

            Args:
                request: user request

            Return:
                bool: True for is authenticated, False otherwise
        """
        if request.method == 'OPTIONS':
            return True
        authorization_key = request.headers.get('X-Authorization')
        try:
            decode_authorization_key(authorization_key)
            return True
        except Exception as e:
            self.message = e.args[0]
            return False
