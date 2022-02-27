import random
import datetime
import jwt
from visualize.models import Key
from datetime import datetime, timedelta
from django.conf import settings

def generate_key(user):
    """
        Used by Patient
        Generate a key for current User

        Args:
            user: current User object

        Return
            string: key to share. If -1, the generation process failed
    """
    def gen_key():
        """
            Generate a random key, the length is defined in the settings `KEY_LENGTH`

            Return:
                string: key to share
        """
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
    """
        Used by Healthcare Provider
        Generate a JWT for accessing patient data

        Args:
            username: the username of the patient
            permissions: the permissions of the JWT

        Return:
            string: JWT for accessing the data
    """
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
    """
        Used by Healthcare Provider
        Decode a JWT for validating access

        Args:
            authorization_key: JWT to decode

        Return:
            dict: the payload in JWT, see `token_dict`@generate_authorization_key
    """
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
    """
        Used by Healthcare Provider
        Get a new JWT with existing an existing JWT

        Args:
            authorization_key: existing JWT

        Return:
            string: new JWT
    """
    token_dict = decode_authorization_key(authorization_key)
    return generate_authorization_key(token_dict['username'], token_dict['permissions'])
