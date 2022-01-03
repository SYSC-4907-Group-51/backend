from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import password_validation
from django.core import exceptions

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def logout_user(user_token):
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