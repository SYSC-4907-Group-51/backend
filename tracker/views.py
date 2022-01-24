from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import get_current_timezone
# from tracker.serializers import 
from user.utils import Logger
from rest_framework import permissions, status
from tracker.utils import *
from datetime import datetime
from tracker.models import UserProfile
from tracker.wrapper.fitbit_wrapper import FitbitWrapper
from user.models import User

# Create your views here.
class TrackerAuthorizeView(APIView):
    permission_classes = [permissions.AllowAny]
    fitbit_obj = FitbitWrapper(None)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        url, state_id = self.fitbit_obj.get_authorization_url()
        save_authorization_state_id(state_id, request.user)
        return Response(
            {'authorization_url': url},
            status=200,
        )

    def get(self, request):
        state_id = request.query_params.get('state')
        code = request.query_params.get('code')
        try:
            token_dict = self.fitbit_obj.get_token_dict(code)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            access_token = token_dict['access_token']
            refresh_token = token_dict['refresh_token']
            expires_at = datetime.fromtimestamp(token_dict['expires_at'], tz=get_current_timezone())
            # TODO: move to the new job system
            user_profile = self.fitbit_obj.get_user_profile()
            query_dict = get_user_with_state_id(state_id)
            if 'error' in query_dict:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            UserProfile.objects.filter(
                user=query_dict['user']
            ).update(
                access_token=access_token, 
                refresh_token=refresh_token, 
                expires_at=expires_at, 
                user_profile=user_profile
            )
            return Response(
                {'details': 'Successfully authorized'},
                status=200,
            )