from django.db import models
from user.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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