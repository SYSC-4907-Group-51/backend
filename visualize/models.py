from django.db import models
from user.models import User

# Create your models here.
class Key(models.Model):
    key = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    allow_step_time_series = models.BooleanField(default=False)
    allow_heartrate_time_series = models.BooleanField(default=False)
    allow_sleep_time_series = models.BooleanField(default=False)
    allow_step_intraday_data = models.BooleanField(default=False)
    allow_heartrate_intraday_data = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['key', 'user', 'notes']

    class Meta:
        ordering = ['-created_at']

    def get_permissions(self):
        """
            Get the key permission array

            Return:
                list: permission array
                        0 -> step time series
                        1 -> heartrate time series
                        2 -> sleep time series
                        3 -> step intraday data
                        4 -> heartrate intraday data
        """
        return [
            self.allow_step_time_series,
            self.allow_heartrate_time_series,
            self.allow_sleep_time_series,
            self.allow_step_intraday_data,
            self.allow_heartrate_intraday_data
        ]
