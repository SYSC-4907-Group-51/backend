from django.db import models
from user.models import User

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

    REQUIRED_FIELDS = ['user', 'user_profile']

    class Meta:
        ordering = ['user', '-created_at']

    def save_authorization_state_id(self, state_id):
        self.state_id = state_id
        self.save()

class UserDevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    devices = models.JSONField(default=dict)
    last_sync_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['user', 'devices']

    class Meta:
        ordering = ['user', '-created_at']

    def update_last_sync_time(self, last_sync_time):
        self.last_sync_time = last_sync_time
        self.save()
    
    def update_devices(self, devices):
        self.devices = devices
        self.save()

class UserStepTimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time_uuid = models.CharField(max_length=100)
    date_time = models.DateField()
    steps = models.PositiveIntegerField()
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user', 'date_time', 'steps']

    class Meta:
        ordering = ['user', 'date_time']

class UserHeartRateTimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time_uuid = models.CharField(max_length=100)
    date_time = models.DateField()
    resting_heart_rate = models.PositiveSmallIntegerField()
    heart_rate_zones = models.JSONField(default=dict)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['user', 'date_time', 'resting_heart_rate']

    class Meta:
        ordering = ['user', 'date_time']

class UserSleepTimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time_uuid = models.CharField(max_length=100)
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

    REQUIRED_FIELDS = ['user', 'date_time', 'minutes_asleep']

    class Meta:
        ordering = ['user', 'date_time']

class UserStepIntradayData(models.Model):
    time_series = models.OneToOneField(UserStepTimeSeries, on_delete=models.CASCADE)
    dataset = models.JSONField(default=dict)
    dataset_interval = models.PositiveSmallIntegerField()
    dataset_type = models.CharField(max_length=100)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['time_series', 'dataset', 'dataset_interval', 'dataset_type']

    class Meta:
        ordering = ['time_series']

class UserHeartRateIntradayData(models.Model):
    time_series = models.OneToOneField(UserHeartRateTimeSeries, on_delete=models.CASCADE)
    dataset = models.JSONField(default=dict)
    dataset_interval = models.PositiveSmallIntegerField()
    dataset_type = models.CharField(max_length=100)
    last_sync_time = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ['time_series', 'dataset', 'dataset_interval', 'dataset_type']

    class Meta:
        ordering = ['time_series']