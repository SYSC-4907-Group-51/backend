from tracker.models import UserProfile
from tracker.wrapper.fitbit_wrapper import FitbitRetriever
from datetime import datetime
from user.utils import Logger

def retrieve_all_user_data():
    user_profiles = UserProfile.objects.filter(is_authorized=True)
    for user_profile in user_profiles:
        if not user_profile.is_authorized:
            continue
        action = 'The tracker data for User {} is automatically updating.'.format(user_profile.user.username)
        Logger(user=user_profile.user, action=action).info()
        print(action + 'at {}'.format(datetime.today()))
        FitbitRetriever(user_profile=user_profile).retrieve_all()
