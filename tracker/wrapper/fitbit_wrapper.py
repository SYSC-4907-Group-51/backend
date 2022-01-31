from tracker.wrapper.fitbit import fitbit
from tracker.models import *
from django.core import exceptions
from user.models import User
from django.utils.timezone import get_current_timezone, make_aware
from datetime import datetime, timedelta, date
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

    def get_step_time_series(self, start_date: str="today", end_date: str="today"):
        return self.__get_time_series('activities/tracker/steps', start_date, end_date)["activities-tracker-steps"]
    
    def get_heartrate_time_series(self, start_date: str="today", end_date: str="today"):
        return self.__get_time_series('activities/heart', start_date, end_date)["activities-heart"]

    def get_sleep_time_series(self, start_date: str="today", end_date: str="today"):
        return self.__get_time_series('sleep', start_date, end_date)["sleep"]

    def get_step_intraday_data(self, start_date: str="today", end_date: str="today", detail_level: str="1min") -> dict:
        return self.__get_intraday_data('activities/steps', start_date, end_date, detail_level)["activities-steps-intraday"]

    def get_heartrate_intraday_data(self, start_date: str="today", end_date: str="today", detail_level: str="1min") -> dict:
        return self.__get_intraday_data('activities/heart', start_date, end_date, detail_level)["activities-heart-intraday"]

    def __get_intraday_data(self, resource: str, start_date: datetime, end_date: datetime, detail_level: str) -> dict:
        return self.fitbit_obj.intraday_time_series(resource, base_date=start_date, end_date=end_date)

    def __get_time_series(self, resource: str, start_date: str, end_date: str) -> dict:
        return self.fitbit_obj.time_series(resource, base_date=start_date, end_date=end_date)

class FitbitRetriever:

    def __init__(self, user: User, default_time_range=30) -> None:
        self.user = user
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.user_id = None
        self.scope = None
        self.user_profile = None
        self.__get_db_profile()
        self.fitbit_obj = FitbitWrapper(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
            token_updater=self.token_updater
        )
        self.default_time_range = default_time_range

    def __get_db_profile(self):
        try:
            user_profile = UserProfile.objects.get(user=self.user)
        except exceptions.ObjectDoesNotExist:
            pass
        else:
            self.user_profile = user_profile.user_profile
            self.access_token = user_profile.access_token
            self.refresh_token = user_profile.refresh_token
            self.expires_at = user_profile.expires_at.timestamp()
            self.user_id = user_profile.user_account_id
            self.scope = user_profile.scope

    def retrieve_all(self):
        self.save_user_profile()
        self.save_user_devices()
        self.save_step_time_series()
        self.save_heartrate_time_series()

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
        user_profile = self.fitbit_obj.get_user_profile()['user']
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

    def save_step_time_series(self):
        user_step_time_series = UserStepTimeSeries.objects.filter(user=self.user)
        if user_step_time_series.count() == 0:
            start_date = date.fromisoformat(self.user_profile["memberSince"])
        else:
            start_date = user_step_time_series.last().date_time
        end_date = date.today()
        # split time series into chunks of 30 days
        time_delta = (end_date - start_date).days
        time_intervals = [(start_date + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, time_delta, self.default_time_range)]
        if len(time_intervals) != 0 and time_intervals[-1] != end_date.strftime("%Y-%m-%d"):
            time_intervals.append(end_date.strftime("%Y-%m-%d"))
        for i in range(0, len(time_intervals) - 1):
            start_date = time_intervals[i]
            end_date = time_intervals[i+1]
            action = 'User {} Fitbit step time series from {} to {} was updated.'.format(self.user.username, start_date, end_date)
            Logger(user=self.user, action=action).info()
            user_step_time_series_from_fitbit = self.fitbit_obj.get_step_time_series(start_date, end_date)
            for item in user_step_time_series_from_fitbit:
                user_step_time_series = UserStepTimeSeries.objects.update_or_create(
                    user=self.user,
                    date_time_uuid=item['dateTime'],
                    date_time=date.fromisoformat(item['dateTime']),
                    steps=item["value"]
                )
    
    def save_heartrate_time_series(self):
        user_heartrate_time_series = UserHeartRateTimeSeries.objects.filter(user=self.user)
        if user_heartrate_time_series.count() == 0:
            start_date = date.fromisoformat(self.user_profile["memberSince"])
        else:
            start_date = user_heartrate_time_series.last().date_time
        end_date = date.today()
        # split time series into chunks of 30 days
        time_delta = (end_date - start_date).days
        time_intervals = [(start_date + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, time_delta, self.default_time_range)]
        if len(time_intervals) and time_intervals[-1] != end_date.strftime("%Y-%m-%d"):
            time_intervals.append(end_date.strftime("%Y-%m-%d"))
        for i in range(0, len(time_intervals) - 1):
            start_date = time_intervals[i]
            end_date = time_intervals[i+1]
            action = 'User {} Fitbit heartrate time series from {} to {} was updated.'.format(self.user.username, start_date, end_date)
            Logger(user=self.user, action=action).info()
            user_heartrate_time_series_from_fitbit = self.fitbit_obj.get_heartrate_time_series(start_date, end_date)
            for item in user_heartrate_time_series_from_fitbit:
                user_heartrate_time_series = UserHeartRateTimeSeries.objects.update_or_create(
                    user=self.user,
                    date_time_uuid=item['dateTime'],
                    date_time=date.fromisoformat(item['dateTime']),
                    resting_heart_rate=item["value"]["restingHeartRate"],
                    heart_rate_zones=item["value"]["heartRateZones"]
                )