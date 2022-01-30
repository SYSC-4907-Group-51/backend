from django.db import models
from user.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_profile = models.JSONField(default=dict)
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

    REQUIRED_FIELDS = ['user', 'last_sync_time']

    class Meta:
        ordering = ['user', '-created_at']

    def update_last_sync_time(self, last_sync_time):
        self.last_sync_time = last_sync_time
        self.save()
    
    def update_devices(self, devices):
        self.devices = devices
        self.save()