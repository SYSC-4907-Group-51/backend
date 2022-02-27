from rest_framework.response import Response
from rest_framework.views import APIView
from visualize.serializers import *
from user.utils import Logger
from rest_framework import permissions, status
from visualize.utils import *
from django.conf import settings
from visualize.models import *
from visualize.permissions import *
from user.models import User
from tracker.models import *
from tracker.serializers import *
from tracker.lib.thread import run_task
from tracker.wrapper.fitbit_wrapper import *

# Create your views here.
KEY_PERMISSIONS = [
    "step time series",
    "heartrate time series",
    "sleep time series",
    "step intraday data",
    "heartrate intraday data"
]

class KeyCreateView(APIView):
    def post(self, request):
        """
            Patient Generate Key API
            See: README.md -> /create-key

            Args:
                request: user request data

            Return:
                dict: response
        """
        if len(request.data.get('permissions', [])) != 5:
            return Response(
                {
                    'detail': 'permissions must be 5 in length'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if sum(request.data.get('permissions')) == 0:
            return Response(
                {
                    'detail': 'cannot create a key without permissions'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        for permission in request.data.get('permissions'):
            if type(permission) is not bool:
                return Response(
                    {
                        'detail': 'permissions must be boolean'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        # check user sync status first
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'detail': 'user profile does not exist'
                }, 
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            user_sync_status_objs = UserSyncStatus.objects.filter(user_profile=user_profile)
            if user_sync_status_objs.count() == 0:
                return Response(
                    {
                        'detail': 'user sync status does not exist'
                    }, 
                    status=status.HTTP_403_FORBIDDEN
                )
        key = generate_key(request.user)
        if key == -1:
            action = 'User {} failed to generate a key'.format(request.user.username)
            Logger(user=request.user, action=action).error()

            return Response(
                {
                    'detail': 'Maximum allowable key limit is reached',
                    'limit': settings.UTILS_CONSTANTS['RE_GENERATE_KEY_LIMIT']
                }, 
                status=status.HTTP_403_FORBIDDEN
            )

        data = {
            'user': request.user.id,
            'notes': request.data.get('notes', ''),
            'allow_step_time_series': request.data.get('permissions')[0],
            'allow_heartrate_time_series': request.data.get('permissions')[1],
            'allow_sleep_time_series': request.data.get('permissions')[2],
            'allow_step_intraday_data': request.data.get('permissions')[3],
            'allow_heartrate_intraday_data': request.data.get('permissions')[4],
            'key': key
        }
        
        serializer = KeySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        key_permissions = request.data.get('permissions')

        action = 'User {} created a key {} for {} with notes: {}'.format(
            request.user.username, 
            key, 
            ", ".join([KEY_PERMISSIONS[i] for i in range(len(key_permissions)) if key_permissions[i] is True]), 
            data['notes']
        )
        Logger(user=request.user, action=action).info()
        run_task(
            dict(
                target=FitbitRetriever(user=request.user).retrieve_all,
                args=(),
                daemon=True,
            ),
        )
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED
        )

class KeyShowView(APIView):
    def get(self, request):
        """
            Patient Get Available Keys API
            See: README.md -> /show-keys

            Args:
                request: user request data

            Return:
                dict: response
        """
        key_objs = Key.objects.filter(user=request.user)
        serializer = KeySerializer(key_objs, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class KeyDeleteView(APIView):
    def delete(self, request):
        """
            Patient Delete A Key API
            See: README.md -> /delete-key

            Args:
                request: user request data

            Return:
                dict: response
        """
        serializer = KeyDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.delete(request.user, request.data)

        action = 'User {} deleted key {}'.format(request.user.username, serializer.initial_data['key'])
        Logger(request.user, action).info()

        return Response(
            {
                'detail': 'Successfully deleted',
            },
            status=status.HTTP_200_OK
        )

class VisualizeEntranceView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        """
            Healthcare Provider Enter Key API
            See: README.md -> /view

            Args:
                request: user request data

            Return:
                dict: response
        """
        if request.query_params.get('username') and request.query_params.get('key'):
            try:
                user = User.objects.get(username=request.query_params.get('username'))
            except:
                return Response(
                    {
                        'detail': 'No such user'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                try:
                    key = Key.objects.get(user=user, key=request.query_params.get('key'))
                except:
                    return Response(
                        {
                            'detail': 'No such key'
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    key_permissions_ = key.get_permissions()
                    action = 'User {} data is visualized using key {} for {} with notes: {}'.format(
                        user.username, key.key, 
                        ", ".join([KEY_PERMISSIONS[i] for i in range(len(key_permissions_)) if key_permissions_[i] is True]), 
                        key.notes
                    )
                    Logger(user, action).info()

                    # user should have profile and sync status
                    user_profile_obj = UserProfile.objects.get(user=user)
                    user_sync_status_objs = UserSyncStatus.objects.filter(user_profile=user_profile_obj)

                    available_dates = {
                        "step_time_series": [],
                        "heartrate_time_series": [],
                        "sleep_time_series": [],
                        "step_intraday_data": [],
                        "heartrate_intraday_data": []
                    }

                    for user_sync_status_obj in user_sync_status_objs:
                        if key_permissions_[0] is True and user_sync_status_obj.get_step_time_series_status() is True:
                            available_dates['step_time_series'].append(user_sync_status_obj.date_time.strftime("%Y-%m-%d"))
                        
                        if key_permissions_[1] is True and user_sync_status_obj.get_heartrate_time_series_status() is True:
                            available_dates['heartrate_time_series'].append(user_sync_status_obj.date_time.strftime("%Y-%m-%d"))
                        
                        if key_permissions_[2] is True and user_sync_status_obj.get_sleep_time_series_status() is True:
                            available_dates['sleep_time_series'].append(user_sync_status_obj.date_time.strftime("%Y-%m-%d"))
                        
                        if key_permissions_[3] is True and user_sync_status_obj.get_step_intraday_data_status() is True:
                            available_dates['step_intraday_data'].append(user_sync_status_obj.date_time.strftime("%Y-%m-%d"))
                        
                        if key_permissions_[4] is True and user_sync_status_obj.get_heartrate_intraday_data_status() is True:
                            available_dates['heartrate_intraday_data'].append(user_sync_status_obj.date_time.strftime("%Y-%m-%d"))

                    authorization_key = generate_authorization_key(username=user.username, permissions=key_permissions_)
                    key.delete()
                    return Response(
                        {
                            'access': authorization_key,
                            'username': user.username,
                            'permissions': key_permissions_,
                            'available_dates': available_dates,
                        },
                        status=status.HTTP_200_OK
                    )
        else:
            return Response(
                {
                    'detail': 'Invalid request'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

class VisualizeIntradayView(APIView):
    permission_classes = [VisualizePermission]
    def get(self, request):
        """
            Healthcare Provider Get Intraday Data API
            See: README.md -> /intraday

            Args:
                request: user request data

            Return:
                dict: response
        """
        if request.query_params.get('type') and request.query_params.get('date'):
            data_type = request.query_params.get('type')
            data_date = request.query_params.get('date')
            authorization_key = decode_authorization_key(authorization_key=request.headers.get('X-Authorization'))
            
            try:
                date_time = date.fromisoformat(data_date)
            except:
                return Response(
                    {
                        'detail': 'Invalid date format',
                        'format': 'YYYY-MM-DD'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(username=authorization_key['username'])
                user_profile = UserProfile.objects.get(user=user)
            except:
                return Response(
                    {
                        'detail': 'No such user'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user_sync_status = UserSyncStatus.objects.get(user_profile=user_profile, date_time=date_time)
            except:
                return Response(
                    {
                        'detail': 'No data for {}'.format(data_date)
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if data_type == "step":
                if authorization_key['permissions'][3] is True and user_sync_status.get_step_intraday_data_status() is True:
                    serializer = UserStepIntradayDataSerializer(user_sync_status.step_intraday_data)
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'detail': 'No permission or no data available'
                        }, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif data_type == "heartrate":
                if authorization_key['permissions'][4] is True and user_sync_status.get_heartrate_intraday_data_status() is True:
                    serializer = UserHeartrateIntradayDataSerializer(user_sync_status.heartrate_intraday_data)
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'detail': 'No permission or no data available'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {
                        'detail': 'Invalid type',
                        'types' : ['step', 'heartrate']
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {
                'detail': 'Invalid type or date'
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )

class VisualizeTimeSeriesView(APIView):
    permission_classes = [VisualizePermission]
    def get(self, request):
        """
            Healthcare Provider Get Time Series Data API
            See: README.md -> /time-series

            Args:
                request: user request data

            Return:
                dict: response
        """
        if request.query_params.get('type') and request.query_params.get('start_date'):
            
            data_type = request.query_params.get('type')
            data_start_date = request.query_params.get('start_date')
            authorization_key = decode_authorization_key(authorization_key=request.headers.get('X-Authorization'))
            
            try:
                start_date = date.fromisoformat(data_start_date)
            except:
                return Response(
                    {
                        'detail': 'Invalid date format',
                        'date_format': 'YYYY-MM-DD'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(username=authorization_key['username'])
                user_profile = UserProfile.objects.get(user=user)
            except:
                return Response(
                    {
                        'detail': 'No such user'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user_sync_status_entries = UserSyncStatus.objects.filter(user_profile=user_profile)
            except:
                return Response(
                    {
                        'detail': 'No data available'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user_sync_status_entries.count() == 0:
                return Response(
                    {
                        'detail': 'No data available'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                if request.query_params.get('end_date'):
                    # with end date
                    data_end_date = request.query_params.get('end_date')
                else:
                    # without end date
                    data_end_date = user_sync_status_entries.last().date_time.strftime("%Y-%m-%d")
                try:
                    end_date = date.fromisoformat(data_end_date)
                except:
                    return Response(
                        {
                            'detail': 'Invalid date format',
                            'format': 'YYYY-MM-DD'
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if start_date > end_date:
                start_date, end_date = end_date, start_date

            if data_type == "step":
                if authorization_key['permissions'][0] is True:
                    user_step_time_series_objs = UserStepTimeSeries.objects.filter(user_profile=user_profile, date_time__range=(start_date, end_date))
                    serializer = UserStepTimeSeriesSerializer(user_step_time_series_objs, many=True)
                    if len(serializer.data) == 0:
                        return Response(
                            {
                                'detail': 'No data in between {} and {}'.format(data_start_date, data_end_date)
                            }, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response(
                        serializer.data, 
                        status=status.HTTP_200_OK
                    ) 
                else:
                    return Response(
                        {
                            'detail': 'No permission'
                        }, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif data_type == "heartrate":
                if authorization_key['permissions'][1] is True:
                    user_heartrate_time_series_objs = UserHeartrateTimeSeries.objects.filter(user_profile=user_profile, date_time__range=(start_date, end_date))
                    serializer = UserHeartrateTimeSeriesSerializer(user_heartrate_time_series_objs, many=True)
                    if len(serializer.data) == 0:
                        return Response(
                            {
                                'detail': 'No data in between {} and {}'.format(data_start_date, data_end_date)
                            }, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response(
                        serializer.data, 
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'detail': 'No permission'
                        }, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif data_type == "sleep":
                if authorization_key['permissions'][2] is True:
                    user_sleep_time_series_objs = UserSleepTimeSeries.objects.filter(user_profile=user_profile, date_time__range=(start_date, end_date))
                    serializer = UserSleepTimeSeriesSerializer(user_sleep_time_series_objs, many=True)
                    if len(serializer.data) == 0:
                        return Response(
                            {
                                'detail': 'No data in between {} and {}'.format(data_start_date, data_end_date)
                            }, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response(
                        serializer.data, 
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'detail': 'No permission'
                        }, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {
                        'detail': 'Invalid type',
                        'types': ['step', 'heartrate', 'sleep']
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {
                'detail': 'Invalid type or start_date'
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )

class VisualizeAuthorizationKeyRefreshView(APIView):
    permission_classes = [VisualizePermission]
    def put(self, request):
        """
            Healthcare Provider Get New Access Token API
            See: README.md -> /refresh-authorization-key

            Args:
                request: user request data

            Return:
                dict: response
        """
        authorization_key = refresh_authorization_key(authorization_key=request.headers.get('X-Authorization'))
        
        return Response(
            {
                'access': authorization_key,
            },
            status=status.HTTP_201_CREATED
        )