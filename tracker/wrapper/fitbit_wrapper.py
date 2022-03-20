import traceback
import hashlib
from tracker.wrapper.fitbit import fitbit
from tracker.wrapper.fitbit.fitbit.exceptions import *
from tracker.models import *
from user.models import User
from django.utils.timezone import get_current_timezone, make_aware
from datetime import datetime, timedelta, date
from user.utils import Logger
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from tracker.lib.thread import sleep_then_run_task

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
        """
            A wrapper that provides abstruct methods for communicating with 
            Fitbit API.

            Args:
                token_updater: A function that updates the token.
                access_token: string, the access token, None for new user to 
                authorize.
                refresh_token: string, the refresh token, None for new user to 
                authorize.
                expires_at: datetime, the time when the token expires.
        """
        self.fitbit_obj = fitbit.Fitbit(
            FITBIT["ID"], 
            FITBIT["SECRET"],
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_cb=token_updater,
        )

    def get_authorization_url(self) -> str:
        """
            Generate the authorization url.
            
            Return:
                url: string, the authorization url.
                state: string, unique state code for current authorization.
        """
        url, _ = self.fitbit_obj.client.authorize_token_url(scope=FITBIT["DEFAULT_SCOPE"])
        return url, self.fitbit_obj.client.session._state

    def get_token_dict(self, code: str) -> dict:
        """
            When the user authorize the application, Fitbit issues an 
            authorization code, which is used to acquire access token and 
            refresh token.

            Args:
                code: The authorization code.
            
            Return:
                dict: A dictionary containing access token, refresh token, and 
                expiration time.
        """
        self.fitbit_obj.client.fetch_access_token(code)
        return self.fitbit_obj.client.session.token
    
    def get_user_profile(self) -> dict:
        """
            Get the user profile.

            Return:
                dict: A dictionary containing user profile.
        """
        return self.fitbit_obj.user_profile_get()

    def get_devices(self) -> dict:
        """
            Get the user devices.
            
            Return:
                dict: A dictionary containing user devices.
        """
        return self.fitbit_obj.get_devices()

    def get_step_time_series(self, start_date: str="today", end_date: str="today"):
        """
            Get step time series.

            Args:
                start_date: string or datetime, the start date.
                end_date: string or datetime, the end date.
            
            Return:
                dict: A dictionary containing step time series.
        """
        return self.__get_time_series('activities/tracker/steps', start_date, end_date)["activities-tracker-steps"]
    
    def get_heartrate_time_series(self, start_date: str="today", end_date: str="today"):
        """
            Get heart rate time series.

            Args:
                start_date: string or datetime, the start date.
                end_date: string or datetime, the end date.
            
            Return:
                dict: A dictionary containing heart rate time series.
        """
        return self.__get_time_series('activities/heart', start_date, end_date)["activities-heart"]

    def get_sleep_time_series(self, start_date: str="today", end_date: str="today"):
        """
            Get sleep time series.

            Args:
                start_date: string or datetime, the start date.
                end_date: string or datetime, the end date.
            
            Return:
                dict: A dictionary containing sleep time series.
        """
        return self.__get_time_series('sleep', start_date, end_date)["sleep"]

    def get_step_intraday_data(self, start_date: str="today", end_date: str="today", detail_level: str="1min") -> dict:
        """
            Get step intraday data.

            Args:
                start_date: string or datetime, the start date.
                end_date: string or datetime, the end date.
                detail_level: string, the detail level. `1min` or `15min`.
            
            Return:
                dict: A dictionary containing step intraday data.
        """
        return self.__get_intraday_data('activities/steps', start_date, detail_level)

    def get_heartrate_intraday_data(self, start_date: str="today", end_date: str="today", detail_level: str="1min") -> dict:
        """
            Get heart rate intraday data.

            Args:
                start_date: string or datetime, the start date.
                end_date: string or datetime, the end date.
                detail_level: string, the detail level. `1min` or `15min`.
            
            Return:
                dict: A dictionary containing heart rate intraday data.
        """
        return self.__get_intraday_data('activities/heart', start_date, detail_level)

    def __get_intraday_data(self, resource: str, base_date: datetime, detail_level: str) -> dict:
        """
            Abstract method for getting intraday data.

            Args:
                resource: string, the resource. `activities/steps` or 
                `activities/heart`.
                base_date: datetime, the start date.
            
            Return:
                dict: A dictionary containing intraday data.
        """
        return self.fitbit_obj.intraday_time_series(resource, base_date=base_date, detail_level=detail_level)

    def __get_time_series(self, resource: str, start_date: str, end_date: str) -> dict:
        """
            Abstract method for getting time series.

            Args:
                resource: string, the resource. `activities/tracker/steps` or
                `activities/heart` or `sleep`.
                start_date: string or datetime, the start date.
                end_date: string or datetime, the end date.
            
            Return:
                dict: A dictionary containing time series.
        """
        return self.fitbit_obj.time_series(resource, base_date=start_date, end_date=end_date)

class FitbitRetriever:

    def __init__(self, user: User=None, user_profile: UserProfile=None) -> None:
        """
            Initialize the FitbitRetriever.

            Args:
                user: User, the user.
                user_profile: UserProfile, the user profile. One of user or
                user_profile must be provided.
        """
        self.user = user
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.user_id = None
        self.scope = None
        self.user_profile = user_profile
        self.user_profile_json = None
        self.is_authorized = False
        self.__partial_entries = None
        if user is None and user_profile is None:
            raise ValueError("user or user_profile must be specified")
        self.__get_db_profile()
        self.fitbit_obj = FitbitWrapper(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
            token_updater=self.token_updater
        )

    def __get_db_profile(self) -> None:
        """
            Get the user profile from database.
        """
        try:
            self.user_profile = UserProfile.objects.get(user=self.user)
        except UserProfile.DoesNotExist:
            pass
        finally:
            if self.user is None:
                self.user = self.user_profile.user
            self.user_profile_json = self.user_profile.user_profile
            self.access_token = self.user_profile.access_token
            self.refresh_token = self.user_profile.refresh_token
            self.expires_at = self.user_profile.expires_at.timestamp()
            self.user_id = self.user_profile.user_account_id
            self.scope = self.user_profile.scope
            self.is_authorized = self.user_profile.is_authorized

    def retrieve_all(self, start_date: date=None, end_date: date=None, force_update: bool=False) -> None:
        """
            Retrieve all tracker data from Fitbit.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
                force_update: bool, whether to force update.
        """
        if type(start_date) is str:
            start_date = date.fromtimestamp(start_date)
        if type(end_date) is str:
            end_date = date.fromtimestamp(end_date)
        if self.user_profile.is_retrieving and not force_update:
            action = 'A retreiving task for User {} is already waiting or running.'.format(self.user.username)
            Logger(user=self.user, action=action).info()
            return
        try:
            self.user_profile.update_retrieving_status(True)
            self.save_user_profile()
            if self.is_authorized:
                self.save_user_devices()
                self.save_step_time_series(start_date=start_date, end_date=end_date)
                self.save_heartrate_time_series(start_date=start_date, end_date=end_date)
                self.save_sleep_time_series(start_date=start_date, end_date=end_date)
                self.save_step_intraday_data(start_date=start_date, end_date=end_date)
                self.save_heartrate_intraday_data(start_date=start_date, end_date=end_date)
            self.user_profile.update_retrieving_status(False)
        except HTTPTooManyRequests as e:
            action = 'Fail to retrieve User {} data because {}, retry after {} sec.'.format(self.user.username, "API quota exceeded", e.retry_after_secs + 60)
            Logger(user=self.user, action=action).warn()
            sleep_then_run_task(
                task=dict(
                    target=self.retrieve_all,
                    args=(None, None, True),
                    daemon=True,
                ),
                sleep_time=e.retry_after_secs + 60,
            )
        except Exception as e:
            # handle other exceptions
            print(traceback.format_exc())
            action = 'Fail to retrieve User {} data due to unknown error. A manual refresh is needed.'.format(self.user.username)
            Logger(user=self.user, action=action).warn()
            self.user_profile.update_retrieving_status(False)
        finally:
            self.calculate_sync_status()

    def token_updater(self, token_dict):
        """
            Update the access token, refresh token, expiry time, scope, and 
            account id for the patient.

            Args:
                token_dict: dict, the token dictionary.
        """
        self.access_token = token_dict['access_token']
        self.refresh_token = token_dict['refresh_token']
        self.expires_at = datetime.fromtimestamp(token_dict['expires_at'], tz=get_current_timezone())
        self.scope = token_dict['scope']
        user_account_id = token_dict['user_id']
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.update_access_token(self.access_token)
        self.user_profile.update_refresh_token(self.refresh_token)
        self.user_profile.update_expires_at(self.expires_at)
        self.user_profile.update_scope(self.scope)
        self.user_profile.update_user_account_id(user_account_id)
    
    def calculate_sync_status(self, start_date: date=None, end_date: date=None):
        """
            Calculate the sync status for the user, including what data is 
            synced and which date is synced.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
        """
        if start_date is None:
            start_date = date.fromisoformat(self.user_profile_json["memberSince"])
        if end_date is None:
            end_date = date.today()
        time_intervals = self.__calculate_time_intervals(start_date, end_date, 1)
        for time in time_intervals:
            date_time = date.fromisoformat(time)
            uuid = self.__generate_uuid(time)
            try:
                entry = UserSyncStatus.objects.get(user_profile=self.user_profile, uuid=uuid)
            except UserSyncStatus.DoesNotExist:
                UserSyncStatus.objects.create(
                    user_profile=self.user_profile,
                    uuid=uuid,
                    date_time=date_time,
                    step_time_series=self.__get_step_time_series(date_time),
                    heartrate_time_series=self.__get_heartrate_time_series(date_time),
                    sleep_time_series=self.__get_sleep_time_series(date_time),
                    step_intraday_data=self.__get_step_intraday_data(date_time),
                    heartrate_intraday_data=self.__get_heartrate_intraday_data(date_time)
                )
            else:
                entry.step_time_series = self.__get_step_time_series(date_time)
                entry.heartrate_time_series = self.__get_heartrate_time_series(date_time)
                entry.sleep_time_series = self.__get_sleep_time_series(date_time)
                entry.step_intraday_data = self.__get_step_intraday_data(date_time)
                entry.heartrate_intraday_data = self.__get_heartrate_intraday_data(date_time)
                entry.save()
        return
    
    def save_user_profile(self):
        """
            Save the user profile into the database.
        """
        self.user_profile = UserProfile.objects.get(user=self.user)
        try:
            self.user_profile_json = self.fitbit_obj.get_user_profile()['user']
        except HTTPUnauthorized as e:
            action = 'Fail to retrieve User {} data due to {}.'.format(self.user.username, "invalid authorization")
            Logger(user=self.user, action=action).warn()
            self.user_profile.update_is_authorized(False)
            self.is_authorized = False
        except InvalidGrantError as e:
            action = 'Fail to retrieve User {} data due to {}'.format(self.user.username, "invalid authorization")
            Logger(user=self.user, action=action).warn()
            self.user_profile.update_is_authorized(False)
            self.is_authorized = False
        except Exception as e:
            raise e
        else:
            action = 'User {} Fitbit profile was updated.'.format(self.user.username)
            Logger(user=self.user, action=action).info()
            self.user_profile.update_user_profile(self.user_profile_json)

    def save_user_devices(self):
        """
            Save the user devices into the database.
        """
        def calc_last_sync_time(devices_dict):
            last_sync_time = datetime.fromisoformat("1990-01-01T12:00:00.000")
            for device_dict in devices_dict:
                current_sync_time = datetime.fromisoformat(device_dict['lastSyncTime'])
                if current_sync_time > last_sync_time:
                    last_sync_time = current_sync_time
            return make_aware(last_sync_time)

        model = UserDevice
        user_devices_json = self.fitbit_obj.get_devices()
        try:
            user_devices = model.objects.get(user_profile=self.user_profile)
        except model.DoesNotExist:
            user_devices = model.objects.create(
                user_profile=self.user_profile,
                devices=user_devices_json,
                last_sync_time=calc_last_sync_time(user_devices_json)
            )
        else:
            user_devices.update_devices(user_devices_json)
            user_devices.update_last_sync_time(calc_last_sync_time(user_devices_json))
        action = 'User {} Fitbit devices information was updated.'.format(self.user.username)
        Logger(user=self.user, action=action).info()
        return user_devices

    def save_step_time_series(self, start_date: date=None, end_date: date=None):
        """
            Save the step time series into the database.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
        """
        model = UserStepTimeSeries
        error = None
        try:
            user_step_time_series_from_fitbit = self.__retrieve_latest_date(
                model=model,
                duration=30,
                action='User {} Fitbit step time series from {} to {} was updating.',
                endpoint=self.fitbit_obj.get_step_time_series,
                start_date=start_date,
                end_date=end_date
            )
            action = 'User {} Fitbit step time series was updated.'.format(self.user.username)
        except Exception as e:
            if self.__partial_entries is None:
                raise e
            user_step_time_series_from_fitbit = self.__partial_entries
            action = 'User {} Fitbit step time series was partially updated till {}.'.format(self.user.username, user_step_time_series_from_fitbit[-1]['dateTime'])
            error = e
        for item in user_step_time_series_from_fitbit:
            uuid = self.__generate_uuid(item['dateTime'])
            try:
                last_entry = model.objects.get(uuid=uuid, user_profile=self.user_profile)
                last_entry.update_steps(item["value"])
            except model.DoesNotExist:
                model.objects.create(
                    user_profile=self.user_profile,
                    uuid=uuid,
                    date_time=date.fromisoformat(item['dateTime']),
                    steps=item["value"]
                )
        Logger(user=self.user, action=action).info()
        if error is not None:
            raise error
    
    def save_heartrate_time_series(self, start_date: date=None, end_date: date=None):
        """
            Save the heartrate time series into the database.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
        """
        model = UserHeartrateTimeSeries
        error = None
        try:
            user_heartrate_time_series_from_fitbit = self.__retrieve_latest_date(
                model=model,
                duration=30,
                action='User {} Fitbit heartrate time series from {} to {} was updating.',
                endpoint=self.fitbit_obj.get_heartrate_time_series,
                start_date=start_date,
                end_date=end_date
            )
            action = 'User {} Fitbit heartrate time series was updated.'.format(self.user.username)
        except Exception as e:
            if self.__partial_entries is None:
                raise e
            user_heartrate_time_series_from_fitbit = self.__partial_entries
            action = 'User {} Fitbit heartrate time series was partially updated till {}.'.format(self.user.username, user_heartrate_time_series_from_fitbit[-1]['dateTime'])
            error = e
        for item in user_heartrate_time_series_from_fitbit:
            if "restingHeartRate" not in item["value"]:
                item["value"]["restingHeartRate"] = 0
            uuid = self.__generate_uuid(item['dateTime'])
            try:
                last_entry = model.objects.get(uuid=uuid, user_profile=self.user_profile)
                last_entry.update_resting_heartrate(item["value"]["restingHeartRate"])
                last_entry.update_heartrate_zones(item["value"]["heartRateZones"])
            except model.DoesNotExist:
                model.objects.update_or_create(
                    user_profile=self.user_profile,
                    uuid=uuid,
                    date_time=date.fromisoformat(item['dateTime']),
                    resting_heartrate=item["value"]["restingHeartRate"],
                    heartrate_zones=item["value"]["heartRateZones"]
                )
        Logger(user=self.user, action=action).info()
        if error is not None:
            raise error
    
    def save_sleep_time_series(self, start_date: date=None, end_date: date=None):
        """
            Save the sleep time series into the database.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
        """
        model = UserSleepTimeSeries
        error = None
        try:
            user_sleep_time_series_from_fitbit = self.__retrieve_latest_date(
                model=model,
                duration=30,
                action='User {} Fitbit sleep time series from {} to {} was updating.',
                endpoint=self.fitbit_obj.get_sleep_time_series,
                start_date=start_date,
                end_date=end_date
            )
            action = 'User {} Fitbit sleep time series was updated.'.format(self.user.username)
        except Exception as e:
            if self.__partial_entries is None:
                raise e
            user_sleep_time_series_from_fitbit = self.__partial_entries
            action = 'User {} Fitbit sleep time series was partially updated till {}.'.format(self.user.username, user_sleep_time_series_from_fitbit[-1]['dateTime'])
            error = e
        for item in user_sleep_time_series_from_fitbit:
            if "data" not in item["levels"]:
                item["levels"]["data"] = {}
            if "summary" not in item["levels"]:
                item["levels"]["summary"] = {}
            uuid = self.__generate_uuid(item['dateOfSleep'])
            try:
                last_entry = model.objects.get(uuid=uuid, user_profile=self.user_profile)
                last_entry.update_duration(item["duration"])
                last_entry.update_efficiency(item["efficiency"])
                last_entry.update_start_time(item['startTime'])
                last_entry.update_end_time(item['endTime'])
                last_entry.update_minutes_after_wakeup(item["minutesAfterWakeup"])
                last_entry.update_minutes_asleep(item["minutesAsleep"])
                last_entry.update_minutes_awake(item["minutesAwake"])
                last_entry.update_minutes_to_fall_asleep(item["minutesToFallAsleep"])
                last_entry.update_time_in_bed(item["timeInBed"])
                last_entry.update_levels(item["levels"]["data"])
                last_entry.update_summary(item["levels"]["summary"])
            except model.DoesNotExist:
                model.objects.update_or_create(
                    user_profile=self.user_profile,
                    uuid=uuid,
                    date_time= date.fromisoformat(item['dateOfSleep']),
                    duration = item["duration"],
                    efficiency = item["efficiency"],
                    start_time = make_aware(datetime.fromisoformat(item['startTime'])),
                    end_time = make_aware(datetime.fromisoformat(item['endTime'])),
                    minutes_after_wakeup = item["minutesAfterWakeup"],
                    minutes_asleep = item["minutesAsleep"],
                    minutes_awake = item["minutesAwake"],
                    minutes_to_fall_asleep = item["minutesToFallAsleep"],
                    time_in_bed = item["timeInBed"],
                    levels = item["levels"]["data"],
                    summary = item["levels"]["summary"],
                )
        Logger(user=self.user, action=action).info()
        if error is not None:
            raise error

    def save_step_intraday_data(self, start_date: date=None, end_date: date=None):
        """
            Save the step intraday data into the database.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
        """
        model = UserStepIntradayData
        error = None
        try:
            user_step_intraday_data_from_fitbit = self.__retrieve_latest_date(
                model=model,
                duration=1,
                action='User {} Fitbit step intraday data from {} to {} was updating.',
                endpoint=self.fitbit_obj.get_step_intraday_data,
                start_date=start_date,
                end_date=end_date
            )
            action = 'User {} Fitbit step intraday data was updated.'.format(self.user.username)
        except Exception as e:
            if self.__partial_entries is None:
                raise e
            user_step_intraday_data_from_fitbit = self.__partial_entries
            action = 'User {} Fitbit step intraday data was partially updated till {}.'.format(self.user.username, user_step_intraday_data_from_fitbit[-1]["activities-steps"][0]['dateTime'])
            error = e
        for item in user_step_intraday_data_from_fitbit:
            activities_steps = item["activities-steps"][0]
            activities_steps_intraday = item["activities-steps-intraday"]
            date_time = date.fromisoformat(activities_steps['dateTime'])
            correspoding_time_series = UserStepTimeSeries.objects.get(
                user_profile=self.user_profile,
                date_time=date_time
            )
            try:
                last_entry = model.objects.get(
                    user_profile=self.user_profile,
                    time_series=correspoding_time_series
                )
                last_entry.update_dataset(activities_steps_intraday["dataset"])
            except model.DoesNotExist:
                model.objects.create(
                    user_profile=self.user_profile,
                    time_series=correspoding_time_series,
                    dataset=activities_steps_intraday["dataset"],
                    dataset_interval=activities_steps_intraday["datasetInterval"],
                    dataset_type=activities_steps_intraday["datasetType"],
                )
        Logger(user=self.user, action=action).info()
        if error is not None:
            raise error

    def save_heartrate_intraday_data(self, start_date: date=None, end_date: date=None):
        """
            Save the heartrate intraday data into the database.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
        """
        model = UserHeartrateIntradayData
        error = None
        try:
            user_heartrate_intraday_data_from_fitbit = self.__retrieve_latest_date(
                model=model,
                duration=1,
                action='User {} Fitbit heartrate intraday data from {} to {} was updating.',
                endpoint=self.fitbit_obj.get_heartrate_intraday_data,
                start_date=start_date,
                end_date=end_date
            )
            action = 'User {} Fitbit heartrate intraday data was updated.'.format(self.user.username)
        except Exception as e:
            if self.__partial_entries is None:
                raise e
            user_heartrate_intraday_data_from_fitbit = self.__partial_entries
            action = 'User {} Fitbit heartrate intraday data was partially updated till {}.'.format(self.user.username, user_heartrate_intraday_data_from_fitbit[-1]["activities-heart"][0]['dateTime'])
            error = e
        for item in user_heartrate_intraday_data_from_fitbit:
            activities_heart = item["activities-heart"][0]
            activities_heart_intraday = item["activities-heart-intraday"]
            date_time = date.fromisoformat(activities_heart['dateTime'])
            correspoding_time_series = UserHeartrateTimeSeries.objects.get(
                user_profile=self.user_profile,
                date_time=date_time
            )
            try:
                last_entry = model.objects.get(
                    user_profile=self.user_profile,
                    time_series=correspoding_time_series
                )
                last_entry.update_dataset(activities_heart_intraday["dataset"])
            except model.DoesNotExist:
                model.objects.create(
                    user_profile=self.user_profile,
                    time_series=correspoding_time_series,
                    dataset=activities_heart_intraday["dataset"],
                    dataset_interval=activities_heart_intraday["datasetInterval"],
                    dataset_type=activities_heart_intraday["datasetType"],
                )
        Logger(user=self.user, action=action).info()
        if error is not None:
            raise error
    
    def __retrieve_latest_date(self, model, action, duration, endpoint, start_date: date=None, end_date: date=None, detail_level: str=None):
        """
            Retrieve the latest date from Fitbit.

            Args:
                model: model, the database model to be used.
                action: str, the action to be logged.
                duration: int, the duration of the data to be retrieved.
                endpoint: function, the Fitbit API endpoint to be used.
                start_date: date, the start date.
                end_date: date, the end date.
                detail_level: str, the detail level of the data to be 
                retrieved. `1min` or `15min`
            
            Return:
                list: the retrieved data.

            Raises:
                Exception: API quota exceeded, the retrieved data is partial and is stored in `self.__partial_entries`.
        """
        existing_entries = model.objects.filter(user_profile=self.user_profile)
        if start_date is None:
            if existing_entries.count() == 0:
                start_date = date.fromisoformat(self.user_profile_json["memberSince"])
            else:
                if model == UserStepIntradayData or model == UserHeartrateIntradayData:
                    start_date = existing_entries.last().time_series.date_time
                else: 
                    start_date = existing_entries.last().date_time
        if end_date is None:
            end_date = date.today()
        time_intervals = self.__calculate_time_intervals(start_date, end_date, duration)
        items = []
        endpoint_args = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if detail_level is not None:
            endpoint_args["detail_level"] = detail_level
        action = action.format(self.user.username, start_date, end_date)
        Logger(user=self.user, action=action).info()
        if len(time_intervals) == 0:
            # refresh start date to today, will always less than 30 days
            try:
                new_entries_from_fitbit = endpoint(**endpoint_args)
            except Exception as e:
                raise e
            else:
                items = self.__append_items(items, new_entries_from_fitbit)
        else:
            for i in range(0, len(time_intervals) - 1):
                endpoint_args["start_date"] = time_intervals[i]
                endpoint_args["end_date"] = time_intervals[i+1]
                try:
                    new_entries_from_fitbit = endpoint(**endpoint_args)
                except Exception as e:
                    if len(items) != 0:
                        self.__partial_entries = items
                    raise e
                else:
                    items = self.__append_items(items, new_entries_from_fitbit)
        return items

    def __append_items(self, items: dict, data):
        """
            Append the retrieved data to the existing data.

            Args:
                items: dict, the existing data.
                data: dict, the retrieved data.
            
            Return:
                list: the appended data.
        """
        if type(data) is list:
            for item in data:
                items.append(item)
        elif type(data) is dict:
            items.append(data)
        return items
    
    def __calculate_time_intervals(self, start_date, end_date, duration):
        """
            Calculate the time intervals between the start date and the end date.

            Args:
                start_date: date, the start date.
                end_date: date, the end date.
                duration: int, the duration between each date.
            
            Return:
                list: the time intervals.
        """
        time_delta = (end_date - start_date).days
        time_intervals = [(start_date + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, time_delta, duration)]
        if len(time_intervals) != 0 and time_intervals[-1] != end_date.strftime("%Y-%m-%d"):
            time_intervals.append(end_date.strftime("%Y-%m-%d"))
        return time_intervals

    def __get_step_time_series(self, date_time: date):
        """
            Get the step time series from the database.

            Args:
                date_time: date, the date of the time series.
            
            Return:
                UserStepTimeSeries: the step time series.
        """
        try:
            return UserStepTimeSeries.objects.get(
                user_profile=self.user_profile,
                date_time=date_time
            )
        except UserStepTimeSeries.DoesNotExist:
            return None
    
    def __get_heartrate_time_series(self, date_time: date):
        """
            Get the heartrate time series from the database.

            Args:
                date_time: date, the date of the time series.
            
            Return:
                UserHeartrateTimeSeries: the heartrate time series.
        """
        try:
            return UserHeartrateTimeSeries.objects.get(
                user_profile=self.user_profile,
                date_time=date_time
            )
        except UserHeartrateTimeSeries.DoesNotExist:
            return None

    def __get_sleep_time_series(self, date_time: date):
        """
            Get the sleep time series from the database.

            Args:
                date_time: date, the date of the time series.
            
            Return:
                UserSleepTimeSeries: the sleep time series.
        """
        try:
            return UserSleepTimeSeries.objects.get(
                user_profile=self.user_profile,
                date_time=date_time
            )
        except UserSleepTimeSeries.DoesNotExist:
            return None

    def __get_step_intraday_data(self, date_time: date):
        """
            Get the step intraday data from the database.

            Args:
                date_time: date, the date of the intraday data.
            
            Return:
                UserStepIntradayData: the step intraday data.
        """
        try:
            return UserStepIntradayData.objects.get(
                user_profile=self.user_profile,
                time_series=self.__get_step_time_series(date_time=date_time)
            )
        except UserStepIntradayData.DoesNotExist:
            return None

    def __get_heartrate_intraday_data(self, date_time: date):
        """
            Get the heartrate intraday data from the database.

            Args:
                date_time: date, the date of the intraday data.
            
            Return:
                UserHeartrateIntradayData: the heartrate intraday data.
        """
        try:
            return UserHeartrateIntradayData.objects.get(
                user_profile=self.user_profile,
                time_series=self.__get_heartrate_time_series(date_time=date_time)
            )
        except UserHeartrateIntradayData.DoesNotExist:
            return None

    def __generate_uuid(self, time):
        """
            Generate a unique id for the given time and username.

            Args:
                time: string, the time to generate the id for in %Y-%m-%d.

            Returns:
                string, the unique id.
        """
        return hashlib.md5("{}-{}".format(self.user.username, time).encode()).hexdigest()