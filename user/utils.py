from rest_framework_simplejwt.tokens import RefreshToken

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
