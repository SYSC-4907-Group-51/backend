from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        ordering = ['last_name']

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.TextField()
    level = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']