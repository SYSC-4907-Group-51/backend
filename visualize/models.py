from django.db import models
from user.models import User

# Create your models here.
class Key(models.Model):
    key = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    allow_step_time_series = models.BooleanField(default=False)
    allow_heartrate_time_series = models.BooleanField(default=False)
    allow_sleep_time_series = models.BooleanField(default=False)
    allow_step_intraday_data = models.BooleanField(default=False)
    allow_heartrate_intraday_data = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['key', 'user', 'notes']

    class Meta:
        ordering = ['-created_at']

    def get_permissions(self):
        return [
            self.allow_step_time_series,
            self.allow_heartrate_time_series,
            self.allow_sleep_time_series,
            self.allow_step_intraday_data,
            self.allow_heartrate_intraday_data
        ]

    def set_unavailable(self):
        self.is_available = False
        self.save()

class AuthorizationKey(models.Model):
    key = models.OneToOneField(Key, on_delete=models.CASCADE)
    authorization_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['key', 'authorization_key']

    class Meta:
        ordering = ['key', '-created_at']