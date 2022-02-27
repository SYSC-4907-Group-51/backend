from tracker.models import UserProfile
from django.core import exceptions

def save_authorization_state_id(state_id, user):
    """
        Save state_id from python-fitbit to database

        Args:
            state_id: string from python-fitbit
            user: User, the requested user

        Return:
            UserProfile: the user fitbit profile
    """
    try:
        user_profile = UserProfile.objects.get(user=user)
    except exceptions.ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(
            user=user,
            state_id=state_id
        )
    else:
        user_profile.save_authorization_state_id(state_id)
    return user_profile

def get_user_with_state_id(state_id):
    """
        Return User object from the state_id

        Args:
            state_id: the state_id to math

        Return:
            User: the user entry
    """
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
