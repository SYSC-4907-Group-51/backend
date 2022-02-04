from rest_framework.response import Response
from rest_framework.views import APIView
from visualize.serializers import KeyShowSerializer, KeyDeleteSerializer
from user.utils import Logger
from rest_framework import permissions, status
from visualize.utils import create_key, RE_GENERATE_KEY_LIMIT, delete_key
from visualize.models import Key
from user.models import User
from tracker.models import *

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
        if len(request.data.get('permissions')) != 5:
            return Response({
                'error': 'permissions must be 5 length'
            }, status=400)
        # check user sync status first
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'user profile does not exist'
            }, status=400)
        else:
            try:
                UserSyncStatus.objects.get(user_profile=user_profile)
            except UserSyncStatus.DoesNotExist:
                return Response({
                    'error': 'user sync status does not exist'
                }, status=400)
        key = create_key(request.user, request.data.get('notes'), request.data.get('permissions'))
        if key == -1:
            action = 'User {} failed to generate a key'.format(request.user.username)
            Logger(user=request.user, action=action).info()

            return Response({'details': 'Maximum allowable key limit {} is reached'.format(RE_GENERATE_KEY_LIMIT)}, status=400)
        key_permissions_ = key.get_permissions()
        action = 'User {} created a key {} for {} with notes: {}'.format(request.user.username, key.key, ", ".join([KEY_PERMISSIONS[i] for i in range(len(key_permissions_)) if key_permissions_[i] is True]), request.data.get('notes'))
        Logger(user=request.user, action=action).info()

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

class VisualizeView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        if request.query_params.get('username') and request.query_params.get('key'):
            try:
                user = User.objects.get(username=request.query_params.get('username'))
            except:
                return Response({'details': 'Invalid request'}, status=400)
            else:
                try:
                    key = Key.objects.get(user=user, key=request.query_params.get('key'))
                except:
                    return Response({'details': 'Invalid request'}, status=400)
                else:
                    # TODO: data visualization
                    delete_key(key)
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

                    return Response({
                        'key': key.key,
                        'username': user.username,
                        'permissions': key_permissions_,
                        'available_dates': available_dates,
                    })
        else:
            return Response({'details': 'Invalid request'}, status=400)