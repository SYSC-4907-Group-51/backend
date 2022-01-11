from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import password_validation
from django.core import exceptions
from user.models import Log

def get_tokens_for_user(user):
    token = RefreshToken.for_user(user)

    return {
        'refresh': str(token),
        'access': str(token.access_token),
    }

def logout_user(user):
    user_token = get_tokens_for_user(user)['refresh']
    try:
        token = RefreshToken(user_token)
        token.blacklist()
        return True
    except:
        return False

def password_validator(instance, password):
    errors = dict()
    try:
        password_validation.validate_password(password=password, user=instance)
    except exceptions.ValidationError as e:
        errors['password'] = list(e.messages)
    else:
        instance.set_password(password)
    return errors

class Logger:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def warn(self):
        log = Log(user=self.user, action=self.action, level=self.WARNING)
        log.save()

    def info(self):
        log = Log(user=self.user, action=self.action, level=self.INFO)
        log.save()

    def error(self):
        log = Log(user=self.user, action=self.action, level=self.ERROR)
        log.save()
