from rest_framework.response import Response
from rest_framework.views import APIView
# from tracker.serializers import 
from user.utils import Logger
from rest_framework import permissions, status
from tracker.utils import *
from tracker.wrapper.fitbit_wrapper import FitbitWrapper
from tracker.lib.thread import run_tasks

# Create your views here.
class TrackerAuthorizeView(APIView):
    permission_classes = [permissions.AllowAny]
    fitbit_obj = FitbitWrapper(None)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                "detail": "Given token not valid for any token type",
                "code": "token_not_valid",
                "messages": [
                    {
                    "token_class": "AccessToken",
                    "token_type": "access",
                    "message": "Token is invalid or expired"
                    }
                ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        url, state_id = self.fitbit_obj.get_authorization_url()

        action = 'User {} tried to authorize Fitbit account with state id: {}'.format(request.user.username, state_id)
        Logger(user=request.user, action=action).info()

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
            return Response({
                "detail": "Given token not valid for any token type",
                "code": "token_not_valid",
                "messages": [
                    {
                    "token_class": "AccessToken",
                    "token_type": "access",
                    "message": "Token is invalid or expired"
                    }
                ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            query_dict = get_user_with_state_id(state_id)
            if 'error' in query_dict:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            action = 'User {} authorized Fitbit account'.format(query_dict['user'].username)
            Logger(user=query_dict['user'], action=action).info()

            run_tasks(
                [
                    dict(
                        target=save_user_profile,
                        args=(self.fitbit_obj, token_dict, query_dict['user']),
                        daemon=True,
                    ),
                    dict(
                        target=save_user_devices,
                        args=(self.fitbit_obj, query_dict['user']),
                        daemon=True,
                    ),
                ]
            )
            return Response(
                {'details': 'Successfully authorized'},
                status=200,
            )