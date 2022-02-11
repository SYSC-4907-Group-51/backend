import random
import datetime
import jwt
from visualize.models import Key
from datetime import datetime, timedelta
from django.conf import settings

def generate_key(user):
    def gen_key():
        key_length = settings.UTILS_CONSTANTS['KEY_LENGTH']
        key = random.randint(10 ** (key_length - 1), 10 ** (key_length) - 1)
        return key
    re_generate_key_limit = settings.UTILS_CONSTANTS['RE_GENERATE_KEY_LIMIT']
    if Key.objects.filter(user=user).count() >= re_generate_key_limit:
        return -1
    key_gen = gen_key()
    is_re_generate_failed = False
    for i in range(re_generate_key_limit):
        if Key.objects.filter(key=key_gen, user=user).exists():
            # check if the genreated key is unused, if not, generate another key
            key_gen = gen_key()
            is_re_generate_failed = True
        else:
            break
    if is_re_generate_failed:
        return -1
    return key_gen

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
