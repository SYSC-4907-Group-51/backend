from tracker.models import UserProfile
from django.core import exceptions

def save_authorization_state_id(state_id, user):
    obj, created = UserProfile.objects.update_or_create(user=user, state_id=state_id)
    return created

def get_user_with_state_id(state_id):
    return_dict = dict()
    try:
        user = UserProfile.objects.get(state_id=state_id).user
    except exceptions.ObjectDoesNotExist as e:
        return_dict['error'] = list(e.messages)
    else:
        # if no user_profile found, return error
        if not user:
            return_dict['error'].append('No user found')
        return_dict['user'] = user
    return return_dict