import random
from visualize.models import Key

KEY_LENGTH = 6
RE_GENERATE_KEY_LIMIT = 10

def generate_key():
    key = random.randint(10 ** (KEY_LENGTH - 1), 10 ** (KEY_LENGTH) - 1)
    return key

def create_key(user, notes=None):
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
    key = Key.objects.create(key=key_gen, user=user, notes=notes)
    return key

def delete_key(key):
    key.delete()
    return True