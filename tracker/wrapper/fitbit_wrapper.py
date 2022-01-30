from tracker.wrapper.fitbit import fitbit
from tracker.models import UserProfile, UserDevice
from django.core import exceptions
from user.models import User
from django.utils.timezone import get_current_timezone, make_aware
from datetime import datetime
from user.utils import Logger

FITBIT = {
    "ID": "23BJ8J",
    "SECRET": "3dfa10d04abfa792e90d8316cccb9991",
    "DEFAULT_SCOPE": ["activity", "heartrate", "profile", "settings", "sleep"],
}

class FitbitWrapper:

    def __init__(
            self, 
            token_updater,
            access_token=None, 
            refresh_token=None,
            expires_at=None,
        ) -> None:
        self.fitbit_obj = fitbit.Fitbit(
            FITBIT["ID"], 
            FITBIT["SECRET"],
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_cb=token_updater,
        )

    def get_authorization_url(self) -> str:
        url, _ = self.fitbit_obj.client.authorize_token_url(scope=FITBIT["DEFAULT_SCOPE"])
        return url, self.fitbit_obj.client.session._state

    def get_token_dict(self, code: str) -> dict:
        self.fitbit_obj.client.fetch_access_token(code)
        return self.fitbit_obj.client.session.token
    
    def get_user_profile(self) -> dict:
        return self.fitbit_obj.user_profile_get()

    def get_devices(self) -> dict:
        return self.fitbit_obj.get_devices()

class FitbitRetriever:

    def __init__(self, user: User) -> None:
        self.user = user
        self.access_token, self.refresh_token, self.expires_at = self.__get_tokens()
        self.fitbit_obj = FitbitWrapper(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
            token_updater=self.token_updater
        )

    def __get_tokens(self):
        try:
            user_profile = UserProfile.objects.get(user=self.user)
        except exceptions.ObjectDoesNotExist:
            pass
        else:
            return (user_profile.access_token, user_profile.refresh_token, user_profile.expires_at.timestamp())

    def retrieve_all(self):
        self.save_user_profile()
        self.save_user_devices()

    def token_updater(token_dict):
        access_token = token_dict['access_token']
        refresh_token = token_dict['refresh_token']
        expires_at = datetime.fromtimestamp(token_dict['expires_at'], tz=get_current_timezone())
        scope = token_dict['scope']
        user_account_id = token_dict['user_id']
        UserProfile.objects.filter(
            user_account_id=user_account_id
        ).update(
            access_token=access_token, 
            refresh_token=refresh_token, 
            expires_at=expires_at, 
            scope=scope,
            user_account_id=user_account_id
        )
    
    def save_user_profile(self):
        action = 'User {} Fitbit profile was updated.'.format(self.user.username)
        Logger(user=self.user, action=action).info()
        user_profile = self.fitbit_obj.get_user_profile()
        UserProfile.objects.filter(
            user=self.user
        ).update(
            user_profile=user_profile
        )

    def save_user_devices(self):
        def calc_last_sync_time(devices_dict):
            last_sync_time = datetime.fromisoformat("1990-01-01T12:00:00.000")
            for device_dict in devices_dict:
                current_sync_time = datetime.fromisoformat(device_dict['lastSyncTime'])
                if current_sync_time > last_sync_time:
                    last_sync_time = current_sync_time
            return make_aware(last_sync_time)

        action = 'User {} Fitbit devices information was updated.'.format(self.user.username)
        Logger(user=self.user, action=action).info()
        user_devices_json = self.fitbit_obj.get_devices()
        try:
            user_devices = UserDevice.objects.get(user=self.user)
        except exceptions.ObjectDoesNotExist:
            user_devices = UserDevice.objects.create(
                user=self.user,
                devices=user_devices_json,
                last_sync_time=calc_last_sync_time(user_devices_json)
            )
        else:
            user_devices.update_devices(user_devices_json)
            user_devices.update_last_sync_time(calc_last_sync_time(user_devices_json))
        return user_devices

