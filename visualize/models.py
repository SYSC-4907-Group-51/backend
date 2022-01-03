from django.db import models
from user.models import User

# Create your models here.
class Key(models.Model):
    key = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    REQUIRED_FIELDS = ['key', 'user', 'notes']

    class Meta:
        ordering = ['-created_at']