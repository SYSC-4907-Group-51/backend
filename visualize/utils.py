import random
import datetime
import jwt
from visualize.models import Key
from datetime import datetime, timedelta
from django.conf import settings

def generate_key():
    key_length = settings.UTILS_CONSTANTS['KEY_LENGTH']
    key = random.randint(10 ** (key_length - 1), 10 ** (key_length) - 1)
    return key

def generate_authorization_key(username, permissions):
    token_dict = {
        'iat': datetime.now().timestamp(),
        'exp': (datetime.now() + timedelta(hours=settings.UTILS_CONSTANTS['AUTHORIZATION_KEY_EXP_TIME_IN_HOURS'], minutes=10)).timestamp(),
        'username': username,
        'permissions': permissions
    }
    headers = {
        'alg': "HS256",
    }
    key = jwt.encode(
            token_dict,
            settings.SECRET_KEY,
            algorithm="HS256",
            headers=headers
            )
    return key

def decode_authorization_key(authorization_key):
    parts = authorization_key.split()
    try:
        token_dict = jwt.decode(
            parts[1],
            settings.SECRET_KEY,
            algorithms=['HS256'],
            )
        return token_dict
    except Exception as e:
        raise e

def refresh_authorization_key(authorization_key):
    token_dict = decode_authorization_key(authorization_key)
    return generate_authorization_key(token_dict['username'], token_dict['permissions'])

def create_key(user, notes=None, permissions=[True, True, True, True, True]):
    re_generate_key_limit = settings.UTILS_CONSTANTS['RE_GENERATE_KEY_LIMIT']
    # check if user has reached the limit
    if Key.objects.filter(user=user).count() >= re_generate_key_limit:
        return -1
    key_gen = generate_key()
    is_re_generate_failed = False
    for i in range(re_generate_key_limit):
        if Key.objects.filter(key=key_gen, user=user).exists():
            # check if the genreated key is unused, if not, generate another key
            key_gen = generate_key()
            is_re_generate_failed = True
        else:
            break
    if is_re_generate_failed:
        return -1
    allow_step_time_series = permissions[0]
    allow_heartrate_time_series = permissions[1]
    allow_sleep_time_series = permissions[2]
    allow_step_intraday_data = permissions[3]
    allow_heartrate_intraday_data = permissions[4]
    key = Key.objects.create(key=key_gen, user=user, notes=notes, allow_step_time_series=allow_step_time_series, allow_heartrate_time_series=allow_heartrate_time_series, allow_sleep_time_series=allow_sleep_time_series, allow_step_intraday_data=allow_step_intraday_data, allow_heartrate_intraday_data=allow_heartrate_intraday_data)
    return key
