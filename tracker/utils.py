from tracker.models import UserProfile, UserDevice
from django.core import exceptions
from django.utils.timezone import get_current_timezone, make_aware
from datetime import datetime
from user.utils import Logger

def save_authorization_state_id(state_id, user):
    try:
        user_profile = UserProfile.objects.get(user=user)
    except exceptions.ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(
            user=user,
            state_id=state_id
        )
    else:
        user_profile.save_authorization_state_id(state_id)
    return user_profile

def get_user_with_state_id(state_id):
    return_dict = dict()
    try:
        user = UserProfile.objects.get(state_id=state_id).user
    except exceptions.ObjectDoesNotExist as e:
        return_dict['error'] = list(e.messages)
    else:
        # if no user_profile found, return error
        if not user:
            return_dict['error'].append('No user found')
        return_dict['user'] = user
    return return_dict

def save_user_profile(fitbit_obj, token_dict, user):
    action = 'User {} Fitbit profile was updated.'.format(user.username)
    Logger(user=user, action=action).info()

    access_token = token_dict['access_token']
    refresh_token = token_dict['refresh_token']
    expires_at = datetime.fromtimestamp(token_dict['expires_at'], tz=get_current_timezone())
    user_profile = fitbit_obj.get_user_profile()
    UserProfile.objects.filter(
        user=user
    ).update(
        access_token=access_token, 
        refresh_token=refresh_token, 
        expires_at=expires_at, 
        user_profile=user_profile
    )

def save_user_devices(fitbit_obj, user):
    def calc_last_sync_time(devices_dict):
        last_sync_time = datetime.fromisoformat("1990-01-01T12:00:00.000")
        for device_dict in devices_dict:
            current_sync_time = datetime.fromisoformat(device_dict['lastSyncTime'])
            if current_sync_time > last_sync_time:
                last_sync_time = current_sync_time
        return make_aware(last_sync_time)

    action = 'User {} Fitbit devices information was updated.'.format(user.username)
    Logger(user=user, action=action).info()
    user_devices_json = fitbit_obj.get_devices()
    try:
        user_devices = UserDevice.objects.get(user=user)
    except exceptions.ObjectDoesNotExist:
        user_devices = UserDevice.objects.create(
            user=user,
            devices=user_devices_json,
            last_sync_time=calc_last_sync_time(user_devices_json)
        )
    else:
        user_devices.update_devices(user_devices_json)
        user_devices.update_last_sync_time(calc_last_sync_time(user_devices_json))
    return user_devices