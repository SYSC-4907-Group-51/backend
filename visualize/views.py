from rest_framework.response import Response
from rest_framework.views import APIView
from visualize.serializers import KeyDeleteSerializer
from user.utils import Logger
from rest_framework import permissions, status
from visualize.utils import *
from django.conf import settings
from visualize.models import *
from visualize.permissions import *
from user.models import User
from tracker.models import *
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
        if len(request.data.get('permissions', [])) != 5:
            return Response({
                'error': 'permissions must be 5 length'
            }, status=400)
        if sum(request.data.get('permissions')) == 0:
            return Response({
                'error': 'cannot create a key without permissions'
            }, status=400)
        for permission in request.data.get('permissions'):
            if type(permission) is not bool:
                return Response({
                    'error': 'permissions must be boolean'
                }, status=400)
        # check user sync status first
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'user profile does not exist'
            }, status=400)
        else:
            user_sync_status_objs = UserSyncStatus.objects.filter(user_profile=user_profile)
            if user_sync_status_objs.count() == 0:
                return Response({
                    'error': 'user sync status does not exist'
                }, status=400)
        key = create_key(request.user, request.data.get('notes'), request.data.get('permissions'))
        if key == -1:
            action = 'User {} failed to generate a key'.format(request.user.username)
            Logger(user=request.user, action=action).error()

            return Response({'details': 'Maximum allowable key limit {} is reached'.format(settings.UTILS_CONSTANTS['RE_GENERATE_KEY_LIMIT'])}, status=400)
        key_permissions_ = key.get_permissions()
        action = 'User {} created a key {} for {} with notes: {}'.format(request.user.username, key.key, ", ".join([KEY_PERMISSIONS[i] for i in range(len(key_permissions_)) if key_permissions_[i] is True]), request.data.get('notes'))
        Logger(user=request.user, action=action).info()
        run_task(
            dict(
                target=FitbitRetriever(user=request.user).retrieve_all,
                args=(),
                daemon=True,
            ),
        )
        return Response({
            'key': key.key,
            'notes': key.notes, 
            'permissions': key_permissions_
        }, status=201)

class KeyShowView(APIView):
    def get(self, request):
        key_objs = Key.objects.filter(user=request.user)
        keys = []
        for key in key_objs:
            keys.append({
                'key': key.key,
                'notes': key.notes,
                'permissions': key.get_permissions(),
                'created_at': key.created_at
            })
        return Response(keys)

class KeyDeleteView(APIView):
    def delete(self, request):
        serializer = KeyDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.delete(request.user, request.data)

        action = 'User {} deleted key {}'.format(request.user.username, serializer.initial_data['key'])
        Logger(request.user, action).info()

        return Response(status=status.HTTP_204_NO_CONTENT)

class VisualizeEntranceView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        if request.query_params.get('username') and request.query_params.get('key'):
            try:
                user = User.objects.get(username=request.query_params.get('username'))
            except:
                return Response({'error': 'No such user'}, status=400)
            else:
                try:
                    key = Key.objects.get(user=user, key=request.query_params.get('key'))
                except:
                    return Response({'error': 'No such key'}, status=400)
                else:
                    key_permissions_ = key.get_permissions()
                    action = 'User {} data is visualized using key {} for {} with notes: {}'.format(user.username, key.key, ", ".join([KEY_PERMISSIONS[i] for i in range(len(key_permissions_)) if key_permissions_[i] is True]), key.notes)
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
                            available_dates['step_time_series'].append(user_sync_status_obj.date_time_uuid)
                        if key_permissions_[1] is True and user_sync_status_obj.get_heartrate_time_series_status() is True:
                            available_dates['heartrate_time_series'].append(user_sync_status_obj.date_time_uuid)
                        if key_permissions_[2] is True and user_sync_status_obj.get_sleep_time_series_status() is True:
                            available_dates['sleep_time_series'].append(user_sync_status_obj.date_time_uuid)
                        if key_permissions_[3] is True and user_sync_status_obj.get_step_intraday_data_status() is True:
                            available_dates['step_intraday_data'].append(user_sync_status_obj.date_time_uuid)
                        if key_permissions_[4] is True and user_sync_status_obj.get_heartrate_intraday_data_status() is True:
                            available_dates['heartrate_intraday_data'].append(user_sync_status_obj.date_time_uuid)

                    authorization_key = generate_authorization_key(username=user.username, permissions=key_permissions_)
                    key.delete()
                    return Response({
                        'access': authorization_key,
                        'username': user.username,
                        'permissions': key_permissions_,
                        'available_dates': available_dates,
                    })
        else:
            return Response({'error': 'Invalid request'}, status=400)

class VisualizeIntradayView(APIView):
    permission_classes = [VisualizePermission]
    def get(self, request):
        if request.query_params.get('type') and request.query_params.get('date'):
            data_type = request.query_params.get('type')
            data_date = request.query_params.get('date')
            authorization_key = decode_authorization_key(authorization_key=request.headers.get('X-Authorization'))
            
            try:
                date_time = date.fromisoformat(data_date)
            except:
                return Response({
                    'error': 'Invalid date format',
                    'date_format': 'YYYY-MM-DD'
                    }, status=400)
            
            try:
                user = User.objects.get(username=authorization_key['username'])
                user_profile = UserProfile.objects.get(user=user)
            except:
                return Response({'error': 'No such user'}, status=400)
            
            try:
                user_sync_status = UserSyncStatus.objects.get(user_profile=user_profile, date_time=date_time)
            except:
                return Response({'error': 'No data for {}'.format(data_date)}, status=400)
            
            if data_type == "step":
                if authorization_key['permissions'][3] is True and user_sync_status.get_step_intraday_data_status() is True:
                    return Response(
                        {
                            "date": data_date,
                            "time_series": {
                                "steps": user_sync_status.step_intraday_data.time_series.steps
                            },
                            "data": user_sync_status.step_intraday_data.dataset,
                            "dataset_type": user_sync_status.step_intraday_data.dataset_type,
                            "dataset_interval": user_sync_status.step_intraday_data.dataset_interval
                        },
                        status=200
                    )
                else:
                    return Response({'error': 'No permission or no data available'}, status=400)
            elif data_type == "heartrate":
                if authorization_key['permissions'][4] is True and user_sync_status.get_heartrate_intraday_data_status() is True:
                    return Response({
                            "date": data_date,
                            "time_series": {
                                "resting_heartrate": user_sync_status.heartrate_intraday_data.time_series.resting_heartrate,
                                "heartrate_zones": user_sync_status.heartrate_intraday_data.time_series.heartrate_zones

                            },
                            "data": user_sync_status.heartrate_intraday_data.dataset,
                            "dataset_type": user_sync_status.heartrate_intraday_data.dataset_type,
                            "dataset_interval": user_sync_status.heartrate_intraday_data.dataset_interval
                        },
                        status=200
                    )
                else:
                    return Response({'error': 'No permission or no data available'}, status=400)
            else:
                return Response({'error': 'Invalid type'}, status=400)

        return Response({'error': 'Invalid type or date'}, status=400)

class VisualizeTimeSeriesView(APIView):
    permission_classes = [VisualizePermission]
    def get(self, request):
        if request.query_params.get('type') and request.query_params.get('start_date'):
            
            data_type = request.query_params.get('type')
            data_start_date = request.query_params.get('start_date')
            authorization_key = decode_authorization_key(authorization_key=request.headers.get('X-Authorization'))
            
            try:
                start_date = date.fromisoformat(data_start_date)
            except:
                return Response({
                    'error': 'Invalid start_date format',
                    'date_format': 'YYYY-MM-DD'
                    }, status=400)
            
            try:
                user = User.objects.get(username=authorization_key['username'])
                user_profile = UserProfile.objects.get(user=user)
            except:
                return Response({'error': 'No such user'}, status=400)
            
            try:
                user_sync_status_entries = UserSyncStatus.objects.filter(user_profile=user_profile)
            except:
                return Response({'error': 'No data available'}, status=400)

            if user_sync_status_entries.count() == 0:
                return Response({'error': 'No data available'}, status=400)
            else:
                if request.query_params.get('end_date'):
                    # with end date
                    data_end_date = request.query_params.get('end_date')
                else:
                    # without end date
                    data_end_date = user_sync_status_entries.last().date_time_uuid
                try:
                    end_date = date.fromisoformat(data_end_date)
                except:
                    return Response({
                        'error': 'Invalid end_date format',
                        'date_format': 'YYYY-MM-DD'
                        }, status=400)  
            
            if start_date > end_date:
                start_date, end_date = end_date, start_date

            if data_type == "step":
                if authorization_key['permissions'][0] is True:
                    user_step_time_series_objs = UserStepTimeSeries.objects.filter(user_profile=user_profile, date_time__range=(start_date, end_date))
                    if user_step_time_series_objs.count() == 0:
                        return Response({'error': 'No data in between {} and {}'.format(data_start_date, data_end_date)}, status=400)
                    else:
                        user_step_time_series = []
                        for user_step_time_series_obj in user_step_time_series_objs:
                            user_step_time_series.append({
                                "date": user_step_time_series_obj.date_time_uuid,
                                "steps": user_step_time_series_obj.steps
                            })
                        return Response(user_step_time_series, status=200)
                else:
                    return Response({'error': 'No permission'}, status=400)
            elif data_type == "heartrate":
                if authorization_key['permissions'][1] is True:
                    user_heartrate_time_series_objs = UserHeartRateTimeSeries.objects.filter(user_profile=user_profile, date_time__range=(start_date, end_date))
                    if user_heartrate_time_series_objs.count() == 0:
                        return Response({'error': 'No data in between {} and {}'.format(data_start_date, data_end_date)}, status=400)
                    else:
                        user_heartrate_time_series = []
                        for user_heartrate_time_series_obj in user_heartrate_time_series_objs:
                            user_heartrate_time_series.append({
                                "date": user_heartrate_time_series_obj.date_time_uuid,
                                "resting_heartrate": user_heartrate_time_series_obj.resting_heartrate,
                                "heartrate_zones": user_heartrate_time_series_obj.heartrate_zones
                            })
                        return Response(user_heartrate_time_series, status=200)
                else:
                    return Response({'error': 'No permission'}, status=400)
            elif data_type == "sleep":
                if authorization_key['permissions'][2] is True:
                    user_sleep_time_series_objs = UserSleepTimeSeries.objects.filter(user_profile=user_profile, date_time__range=(start_date, end_date))
                    if user_sleep_time_series_objs.count() == 0:
                        return Response({'error': 'No data in between {} and {}'.format(data_start_date, data_end_date)}, status=400)
                    else:
                        user_sleep_time_series = []
                        for user_sleep_time_series_obj in user_sleep_time_series_objs:
                            user_sleep_time_series.append({
                                "date": user_sleep_time_series_obj.date_time_uuid,
                                "start_time": user_sleep_time_series_obj.start_time,
                                "end_time": user_sleep_time_series_obj.end_time,
                                "duration": user_sleep_time_series_obj.duration,
                                "efficiency": user_sleep_time_series_obj.efficiency,
                                "minutes_after_wakeup": user_sleep_time_series_obj.minutes_after_wakeup,
                                "minutes_asleep": user_sleep_time_series_obj.minutes_asleep,
                                "minutes_awake": user_sleep_time_series_obj.minutes_awake,
                                "minutes_to_fall_asleep": user_sleep_time_series_obj.minutes_to_fall_asleep,
                                "time_in_bed": user_sleep_time_series_obj.time_in_bed,
                                "levels": user_sleep_time_series_obj.levels,
                                "summary": user_sleep_time_series_obj.summary
                            })
                        return Response(user_sleep_time_series, status=200)
                else:
                    return Response({'error': 'No permission'}, status=400)
            else:
                return Response({'error': 'Invalid type'}, status=400)
        return Response({'error': 'Invalid type or start_date or end_date'}, status=400)

class VisualizeAuthorizationKeyRefreshView(APIView):
    permission_classes = [VisualizePermission]
    def put(self, request):

        authorization_key = refresh_authorization_key(authorization_key=request.headers.get('X-Authorization'))
        
        return Response({
            'access': authorization_key,
        })