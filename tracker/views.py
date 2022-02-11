from rest_framework.response import Response
from rest_framework.views import APIView
from user.utils import Logger
from rest_framework import status
from tracker.utils import *
from tracker.permissions import *
from tracker.wrapper.fitbit_wrapper import *
from tracker.lib.thread import run_task
from django.utils.timezone import get_current_timezone
from datetime import datetime
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from visualize.models import *
from django.conf import settings

# Create your views here.
class TrackerAuthorizeView(APIView):
    permission_classes = [AuthorizationPermission]
    fitbit_obj = FitbitWrapper(None)

    def post(self, request):
        url, state_id = self.fitbit_obj.get_authorization_url()

        action = 'User {} tried to authorize Fitbit account with state id: {}'.format(request.user.username, state_id)
        Logger(user=request.user, action=action).info()

        save_authorization_state_id(state_id, request.user)
        return Response(
            {
                'authorization_url': url
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        state_id = request.query_params.get('state')
        code = request.query_params.get('code')
        if not state_id or not code:
            #TODO: update redirect url
            return Response(
                headers={"Location": "{}/invaliderror".format(settings.UTILS_CONSTANTS["DOMAIN"])},
                status=status.HTTP_302_FOUND
            )
        try:
            token_dict = self.fitbit_obj.get_token_dict(code)
        except Warning as e:
            return Response(
                headers={'Location': '{}/mismatcherror'.format(settings.UTILS_CONSTANTS["DOMAIN"])},
                status=status.HTTP_302_FOUND
            )
        except InvalidGrantError as e:
            return Response(
                headers={"Location": "{}/invaliderror".format(settings.UTILS_CONSTANTS["DOMAIN"])},
                status=status.HTTP_302_FOUND
            )
        else:
            query_dict = get_user_with_state_id(state_id)
            if 'error' in query_dict:
                return Response(
                    headers={"Location": "{}/invaliderror".format(settings.UTILS_CONSTANTS["DOMAIN"])},
                    status=status.HTTP_302_FOUND
                )

            action = 'User {} authorized Fitbit account'.format(query_dict['user'].username)
            Logger(user=query_dict['user'], action=action).info()
            access_token = token_dict['access_token']
            refresh_token = token_dict['refresh_token']
            expires_at = datetime.fromtimestamp(token_dict['expires_at'], tz=get_current_timezone())
            scope = token_dict['scope']
            user_account_id = token_dict['user_id']
            user_profile = UserProfile.objects.get(user=query_dict['user'])
            user_profile.update_access_token(access_token)
            user_profile.update_refresh_token(refresh_token)
            user_profile.update_expires_at(expires_at)
            user_profile.update_scope(scope)
            user_profile.update_user_account_id(user_account_id)
            user_profile.update_is_authorized(True)
            run_task(
                dict(
                    target=FitbitRetriever(user_profile=user_profile).retrieve_all,
                    args=(),
                    daemon=True,
                ),
            )
            return Response(
                headers={"Location": "{}/share".format(settings.UTILS_CONSTANTS["DOMAIN"])},
                status=status.HTTP_302_FOUND,
            )

class TrackerRefreshView(APIView):
    def put(self, request):
        date_time = None
        action = 'User {} initialized a refresh request'.format(request.user.username)
        if request.data.get('date') is not None:
            date_time = date.fromisoformat(request.data.get('date'))
            action = 'User {} initialized a refresh request for {}'.format(request.user.username, request.data.get('date'))
        
        Logger(user=request.user, action=action).info()
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.is_authorized:
            return Response(
                {
                    'detail': 'User is no longer authorized'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        if user_profile.is_retrieving:
            return Response(
                {
                    'detail': 'A retreiving task is already waiting or running.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        run_task(
            dict(
                target=FitbitRetriever(user_profile=user_profile).retrieve_all,
                args=(date_time, date_time,),
                daemon=True,
            ),
        )
        return Response(
            {
                'detail': 'Successed'
            },
            status=status.HTTP_202_ACCEPTED,
        )

class TrackerDeleteView(APIView):
    def delete(self, request):
        user_created_keys = Key.objects.filter(user=request.user, is_available=True)
        if user_created_keys.count() > 0:
            return Response(
                {
                    'detail': 'Keys are still in use, authorization cannot be deleted!'
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        action = 'User {} deleted the authorization for Fitbit'.format(request.user.username)
        Logger(user=request.user, action=action).info()
        UserProfile.objects.get(user=request.user).delete()
        return Response(
            {
                'detail': 'Successed'
            },
            status=status.HTTP_200_OK,
        )