from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import password_validation
from django.core import exceptions
from user.models import Log

def get_tokens_for_user(user):
    """
        Get the token for authorization for current user

        Args:
            user: User, currnet user object

        Return:
            dict: refresh token and access token
    """
    token = RefreshToken.for_user(user)

    return {
        'refresh': str(token),
        'access': str(token.access_token),
    }

def logout_user(user):
    """
        Logout a user. Blacklists the refresh token

        Args:
            user: User, currnet user object

        Return:
            bool: True for successfully deleted the token, False otherwise
    """
    user_token = get_tokens_for_user(user)['refresh']
    try:
        token = RefreshToken(user_token)
        token.blacklist()
        return True
    except:
        return False

def password_validator(instance, password):
    """
        Password validator from Django

        Args:
            instance: User, current user object
            password: the password to set

        Return:
            dict: errors
    """
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
        """
            Args:
                user: User, current user object
                action: string, log detail
        """
        self.user = user
        self.action = action

    def warn(self):
        """
            Add a log entry to the database corresponding to the user

            level: warn
        """
        log = Log(user=self.user, action=self.action, level=self.WARNING)
        log.save()

    def info(self):
        """
            Add a log entry to the database corresponding to the user

            level: info
        """
        log = Log(user=self.user, action=self.action, level=self.INFO)
        log.save()

    def error(self):
        """
            Add a log entry to the database corresponding to the user

            level: error
        """
        log = Log(user=self.user, action=self.action, level=self.ERROR)
        log.save()
