from rest_framework.response import Response
from rest_framework.views import APIView
from user.utils import Logger
from rest_framework import permissions, status
from tracker.utils import *
from tracker.wrapper.fitbit_wrapper import *
from tracker.lib.thread import run_task
from django.utils.timezone import get_current_timezone
from datetime import datetime
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from visualize.models import *

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
        if not state_id or not code:
            Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token_dict = self.fitbit_obj.get_token_dict(code)
        except Warning as e:
            return Response(
                headers={'Location': '/mismatcherror'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidGrantError as e:
            return Response(
                headers={"Location": "/invaliderror"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            query_dict = get_user_with_state_id(state_id)
            if 'error' in query_dict:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            action = 'User {} authorized Fitbit account'.format(query_dict['user'].username)
            Logger(user=query_dict['user'], action=action).info()
            access_token = token_dict['access_token']
            refresh_token = token_dict['refresh_token']
            expires_at = datetime.fromtimestamp(token_dict['expires_at'], tz=get_current_timezone())
            scope = token_dict['scope']
            user_account_id = token_dict['user_id']
            UserProfile.objects.filter(
                user=query_dict['user']
            ).update(
                access_token=access_token, 
                refresh_token=refresh_token, 
                expires_at=expires_at, 
                scope=scope,
                user_account_id=user_account_id,
                is_authorized=True
            )
            run_task(
                dict(
                    target=FitbitRetriever(query_dict['user']).retrieve_all,
                    args=(),
                    daemon=True,
                ),
            )
            # TODO: use header redirect here
            return Response(
                {'details': 'Successfully authorized'},
                status=200,
            )

class TrackerRefreshView(APIView):
    def put(self, request):
        date_time = None
        action = 'User {} initialized a refresh request'.format(request.user.username)
        if request.data.get('date') is not None:
            date_time = date.fromisoformat(request.data.get('date'))
            action = 'User {} initialized a refresh request for {}'.format(request.user.username, request.data.get('date'))
        
        Logger(user=request.user, action=action).info()
        run_task(
            dict(
                target=FitbitRetriever(request.user).retrieve_all,
                args=(date_time, date_time),
                daemon=True,
            ),
        )
        return Response(
            {'details': 'Successed'},
            status=200,
        )

class TrackerDeleteView(APIView):
    def delete(self, request):
        user_created_keys = Key.objects.filter(user=request.user, is_available=True)
        if user_created_keys.count() > 0:
            return Response(
                {'error': 'Keys are still in use, authorization cannot be deleted!'},
                status=400,
            )
        action = 'User {} deleted the authorization for Fitbit'.format(request.user.username)
        Logger(user=request.user, action=action).info()
        UserProfile.objects.get(user=request.user).delete()
        return Response(
            {'details': 'Successed'},
            status=200,
        )