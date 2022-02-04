import random
import secrets
from visualize.models import Key
from datetime import datetime, timedelta

KEY_LENGTH = 6
RE_GENERATE_KEY_LIMIT = 10

def generate_key():
    key = random.randint(10 ** (KEY_LENGTH - 1), 10 ** (KEY_LENGTH) - 1)
    return key

def generate_authorization_key():
    key = secrets.token_urlsafe(64)
    return key

def generate_expired_at():
    expired_at = datetime.now() + timedelta(hours=1)
    return expired_at

def create_key(user, notes=None, permissions=[False, False, False, False, False]):
    # check if user has reached the limit
    if Key.objects.filter(user=user).count() >= RE_GENERATE_KEY_LIMIT:
        return -1
    key_gen = generate_key()
    is_re_generate_failed = False
    for i in range(RE_GENERATE_KEY_LIMIT):
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

def delete_key(key):
    # TODO: run task to delete key 
    key.set_unavailable()
    return True