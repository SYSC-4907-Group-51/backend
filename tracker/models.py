from operator import is_
from django.db import models
from user.models import User
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_profile = models.JSONField(default=dict)
    user_account_id = models.CharField(max_length=100, default='')
    scope = models.JSONField(default=dict)
    state_id = models.CharField(max_length=30)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_authorized = models.BooleanField(default=False)
    is_retrieving = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['user', 'user_profile']

    class Meta:
        ordering = ['user', '-created_at']

    def save_authorization_state_id(self, state_id):
        """
            Save the state_id from python-fitbit

            Args:
                state_id: a random string
        """
        self.state_id = state_id
        self.save()

    def update_is_authorized(self, value):
        """
            Update authorization status

            Args:
                value: boolean, True for is authorized, False otherwise
        """
        self.is_authorized = value
        self.save()
    
    def update_user_profile(self, value):
        """
            Update user Fitbit profile

            Args:
                value: dict, user Fitbit profile
        """
        self.user_profile = value
        self.save()
    
    def update_retrieving_status(self, value):
        """
            Update data retrieving status

            Args:
                value: boolean, True for is retrieving or waiting, False 
                otherwise
        """
        self.is_retrieving = value
        self.save()
    
    def update_access_token(self, access_token):
        """
            Update user Fitbit access token

            Args:
                value: string, access token
        """
        self.access_token = access_token
        self.save()

    def update_refresh_token(self, refresh_token):
        """
            Update user Fitbit refresh token

            Args:
                value: string refresh token
        """
        self.refresh_token = refresh_token
        self.save()

    def update_expires_at(self, expires_at):
        """
            Update user Fitbit token expire time

            Args:
                value: datetime, expire date and time
        """
        self.expires_at = expires_at
        self.save()

    def update_scope(self, scope):
        """
            Update user Fitbit authorization scope

            Args:
                value: dict, user Fitbit authorization scope
        """
        self.scope = scope
        self.save()

    def update_user_account_id(self, user_account_id):
        """
            Update user Fitbit account id

            Args:
                value: string, user Fitbit account id
        """
        self.user_account_id = user_account_id
        self.save()

class UserDevice(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    devices = models.JSONField(default=dict)
    last_sync_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['user_profile', 'devices']

    class Meta:
        ordering = ['user_profile', '-created_at']

    def update_last_sync_time(self, last_sync_time):
        """
            Update user Fitbit last synchronzation time

            Args:
                value: datetime, last synchronzation time
        """
        self.last_sync_time = last_sync_time
        self.save()
    
    def update_devices(self, devices):
        """
            Update user Fitbit devices

            Args:
                value: dict, user Fitbit devices
        """
        self.devices = devices
        self.save()

class UserStepTimeSeries(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateField()
    steps = models.PositiveIntegerField()
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user_profile', 'date_time', 'steps']

    class Meta:
        ordering = ['user_profile', 'date_time']

    def update_steps(self, value):
        """
            Update user Fitbit daily steps

            Args:
                value: int, step count
        """
        self.steps = value
        self.save()

class UserHeartrateTimeSeries(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateField()
    resting_heartrate = models.PositiveSmallIntegerField()
    heartrate_zones = models.JSONField(default=dict)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user_profile', 'date_time', 'resting_heart_rate']

    class Meta:
        ordering = ['user_profile', 'date_time']
    
    def update_resting_heartrate(self, value):
        """
            Update user Fitbit daily resting heartrate

            Args:
                value: int, resting heartrate value
        """
        self.resting_heartrate = value
        self.save()
    
    def update_heartrate_zones(self, value):
        """
            Update user Fitbit daily heartrate zones

            Args:
                value: dict, user Fitbit daily heartrate zones
        """
        self.heartrate_zones = value
        self.save()

class UserSleepTimeSeries(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateField()
    duration = models.PositiveIntegerField()
    efficiency = models.PositiveSmallIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    minutes_after_wakeup = models.PositiveIntegerField()
    minutes_asleep = models.PositiveIntegerField()
    minutes_awake = models.PositiveIntegerField()
    minutes_to_fall_asleep = models.PositiveIntegerField()
    time_in_bed = models.PositiveIntegerField()
    levels = models.JSONField(default=dict)
    summary = models.JSONField(default=dict)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user_profile', 'date_time', 'minutes_asleep']

    class Meta:
        ordering = ['user_profile', 'date_time']
    
    def update_duration(self, value):
        """
            Update user Fitbit daily sleep duration

            Args:
                value: int, sleep duration in sec
        """
        self.duration = value
        self.save()
    
    def update_efficiency(self, value):
        """
            Update user Fitbit daily sleep efficiency

            Args:
                value: int, sleep efficiency value
        """
        self.efficiency = value
        self.save()

    def update_start_time(self, value):
        """
            Update user Fitbit daily sleep start time

            Args:
                value: datetime or string, start time
        """
        if type(value) is str:
            value = make_aware(datetime.fromisoformat(value))
        self.start_time = value
        self.save()

    def update_end_time(self, value):
        """
            Update user Fitbit daily sleep end time

            Args:
                value: datetime or string, end time
        """
        if type(value) is str:
            value = make_aware(datetime.fromisoformat(value))
        self.end_time = value
        self.save()

    def update_minutes_after_wakeup(self, value):
        """
            Update user Fitbit daily after wakeup minutes

            Args:
                value: int, after wakeup minutes
        """
        self.minutes_after_wakeup = value
        self.save()

    def update_minutes_asleep(self, value):
        """
            Update user Fitbit daily asleep minutes

            Args:
                value: int, asleep minutes
        """
        self.minutes_asleep = value
        self.save()

    def update_minutes_awake(self, value):
        """
            Update user Fitbit daily awake minutes

            Args:
                value: int, awake minutes
        """
        self.minutes_awake = value
        self.save()

    def update_minutes_to_fall_asleep(self, value):
        """
            Update user Fitbit daily to fall asleep minutes

            Args:
                value: int, to fall asleep minutes
        """
        self.minutes_to_fall_asleep = value
        self.save()

    def update_time_in_bed(self, value):
        """
            Update user Fitbit daily time in bed minutes

            Args:
                value: int, time in bed minutes
        """
        self.time_in_bed = value
        self.save() 

    def update_levels(self, value):
        """
            Update user Fitbit daily sleep level

            Args:
                value: list, sleep levels
        """
        self.levels = value
        self.save()

    def update_summary(self, value):
        """
            Update user Fitbit daily sleep summary

            Args:
                value: dict, sleep summary
        """
        self.summary = value
        self.save()

class UserStepIntradayData(models.Model):
    """
        Links to corresponding time series that matches the date
    """
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    time_series = models.OneToOneField(UserStepTimeSeries, on_delete=models.CASCADE)
    dataset = models.JSONField(default=dict)
    dataset_interval = models.PositiveSmallIntegerField()
    dataset_type = models.CharField(max_length=100)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user_profile', 'time_series', 'dataset', 'dataset_interval', 'dataset_type']

    class Meta:
        ordering = ['user_profile', 'time_series']

    def update_dataset(self, value):
        """
            Update user Fitbit intraday steps

            Args:
                value: list, intraday step detail
        """
        self.dataset = value
        self.save()

class UserHeartrateIntradayData(models.Model):
    """
        Links to corresponding time series that matches the date
    """
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    time_series = models.OneToOneField(UserHeartrateTimeSeries, on_delete=models.CASCADE)
    dataset = models.JSONField(default=dict)
    dataset_interval = models.PositiveSmallIntegerField()
    dataset_type = models.CharField(max_length=100)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user_profile', 'time_series', 'dataset', 'dataset_interval', 'dataset_type']

    class Meta:
        ordering = ['user_profile', 'time_series']
    
    def update_dataset(self, value):
        """
            Update user Fitbit intraday steps

            Args:
                value: list, intraday step detail
        """
        self.dataset = value
        self.save()

class UserSyncStatus(models.Model):
    """
        Links to each type of data of the date
    """
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateField()
    step_time_series = models.OneToOneField(UserStepTimeSeries, on_delete=models.SET_NULL, null=True)
    heartrate_time_series = models.OneToOneField(UserHeartrateTimeSeries, on_delete=models.SET_NULL, null=True)
    sleep_time_series = models.OneToOneField(UserSleepTimeSeries, on_delete=models.SET_NULL, null=True)
    step_intraday_data = models.OneToOneField(UserStepIntradayData, on_delete=models.SET_NULL, null=True)
    heartrate_intraday_data = models.OneToOneField(UserHeartrateIntradayData, on_delete=models.SET_NULL, null=True)

    REQUIRED_FIELDS = ['user_profile', 'uuid', 'date_time']

    class Meta:
        ordering = ['user_profile', 'date_time']

    def get_sync_status(self):
        """
            Get the sync status array

            Return:
                list: permission array
                        0 -> step time series
                        1 -> heartrate time series
                        2 -> sleep time series
                        3 -> step intraday data
                        4 -> heartrate intraday data
        """
        status = [True, True, True, True, True]
        if self.step_time_series is None:
            status[0] = False
        if self.heartrate_time_series is None:
            status[1] = False
        if self.sleep_time_series is None:
            status[2] = False
        if self.step_intraday_data is None:
            status[3] = False
        if self.heartrate_intraday_data is None:
            status[4] = False
        return status
    
    def get_step_time_series_status(self):
        """
            Get step time series sync status

            Return:
                bool: True for is available, False otherwise
        """
        if self.step_time_series is None:
            return False
        return True

    def get_heartrate_time_series_status(self):
        """
            Get heartrate time series sync status

            Return:
                bool: True for is available, False otherwise
        """
        if self.heartrate_time_series is None:
            return False
        return True

    def get_sleep_time_series_status(self):
        """
            Get sleep time series sync status

            Return:
                bool: True for is available, False otherwise
        """
        if self.sleep_time_series is None:
            return False
        return True 

    def get_step_intraday_data_status(self):
        """
            Get step intraday data sync status

            Return:
                bool: True for is available, False otherwise
        """
        if self.step_intraday_data is None:
            return False
        return True

    def get_heartrate_intraday_data_status(self):
        """
            Get heartrate intraday data sync status

            Return:
                bool: True for is available, False otherwise
        """
        if self.heartrate_intraday_data is None:
            return False
        return True
