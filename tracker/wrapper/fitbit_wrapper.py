from tracker.wrapper.fitbit import fitbit

FITBIT = {
    "ID": "23BJ8J",
    "SECRET": "3dfa10d04abfa792e90d8316cccb9991",
    "DEFAULT_SCOPE": ["activity", "heartrate", "profile", "settings", "sleep"],
}

class FitbitWrapper:

    def __init__(
            self, 
            refresh_cb,
            access_token=None, 
            refresh_token=None,
            expires_at=None,
        ) -> None:
        self.fitbit_obj = fitbit.Fitbit(
            FITBIT["ID"], 
            FITBIT["SECRET"],
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_cb=refresh_cb,
        )

    def get_authorization_url(self) -> str:
        url, _ = self.fitbit_obj.client.authorize_token_url(scope=FITBIT["DEFAULT_SCOPE"])
        return url, self.fitbit_obj.client.session._state

    def get_token_dict(self, code: str) -> dict:
        self.fitbit_obj.client.fetch_access_token(code)
        return self.fitbit_obj.client.session.token
    
    def get_user_profile(self) -> dict:
        return self.fitbit_obj.user_profile_get()

    def get_devices(self) -> dict:
        return self.fitbit_obj.get_devices()
