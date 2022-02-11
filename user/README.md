# API Endpoint /user

## /register

### Method
`POST`

### Header
`N/A`

### Body
```json
{
    "username": "test", // Requeired: username for login
    "password": "test123@", // Requeired: password for login
    "first_name": "test", // Requeired: user profile first name
    "last_name": "test", // Requeired: user profile last name
    "email": "test@exmaple.com" // Requeired: user email
}
```

### Response
#### Succeed
Status Code: `201 Created`

```json
{
  "username": "test", // username
  "first_name": "test", // first name
  "last_name": "test", // last name
  "email": "test@exmaple.com", // email
  "created_at": "2022-01-10T20:06:52.631583-05:00", // the time the user registered
  "updated_at": "2022-01-10T20:06:52.716159-05:00" // the time the user updated their profile
}
```

#### Fail

Case                            | Status Code      | Body
--------------------------------|------------------|-----------
Invalid username/passowrd/email | 400 BAD REQUEST  | `{<reasons>}`


## /login

### Method
`POST`

### Header
`N/A`

### Body
```json
{
    "username": "test", // Requeired: username for login
    "password": "test123@", // Requeired: password for login
}
```

#### Succeed
Status Code: `200 OK`

```json
{
  "username": "test", // username
  "first_name": "test", // first name
  "last_name": "test", // last name
  "email": "test@exmaple.com", // email
  "created_at": "2022-01-10T20:06:52.631583-05:00", // the time the user registered
  "updated_at": "2022-01-10T20:06:52.716159-05:00", // the time the user updated their profile
  "refresh": "ey...", // refresh token for a new access token
  "access": "ey..." // access token to be put in the header for subsequence acess and user identification
}
```

#### Fail

Case                      | Status Code      | Body
--------------------------|------------------|-------------------------------------------
Invalid username/passowrd | 400 BAD REQUEST  | `{"details": "Invalid username/password"}`
No such user              | 400 BAD REQUEST  | `{"details": "No such user"}`

## /logout

### Method
`POST`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

### Response
#### Succeed
Status Code: `200 OK`

```json
{
  "detail": "Successfully Logged out"
}
```
#### Fail

Case             | Status Code      | Body
-----------------|------------------|--------------------------------------------------------------
Unauthorized     | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
Failed to logout | 400 BAD REQUEST  | `{"details": "Unable to logout"}`

## /status

### Method
`GET`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

### Response
#### Succeed
Status Code: `200 OK`

```json
{
  "username": "test",
  "first_name": "test",
  "last_name": "test",
  "is_authorized": true, // true for connected and is able to update, false for either not connected or not able to update
  "devices": [
    {
      "battery": "High",
      "batteryLevel": 84,
      "deviceVersion": "Inspire 2",
      "features": [],
      "id": "1947549326",
      "lastSyncTime": "2022-02-03T11:45:47.000",
      "mac": "FFF541F8A4C8",
      "type": "TRACKER"
    },
    ...
  ],
  "last_sync_time": "2022-02-03T16:45:47Z",
  "profile_not_found": false // true for connected user account, false for not connected
}
```
#### Fail

Case         | Status Code      | Body
-------------|------------------|--------------------------------------------------------------
Unauthorized | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`

## /sync-status

### Method
`GET`

### Query
Optional: `?date=<date in yyyy-mm-dd>`

eg. `?date=2021-01-01`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

#### Succeed
Status Code: `200 OK`

No date:

```json
[
  {
    "date": "2021-10-09",
    "status": [
      true, // step_time_series
      true, // heartrate_time_series
      false, // sleep_time_series
      false, // step_intraday_data
      false // heartrate_intraday_data
    ]
  },
  {
    "date": "2021-10-10",
    "status": [
      true,
      true,
      true,
      false,
      false
    ]
  },
  ...
]
```

Specific date:

```json
[]
```

or

```json
[
  {
    "date": "2022-01-01",
    "sync_status": [
      true,
      true,
      true,
      true,
      false
    ]
  }
]
```

#### Fail

Case                                        | Status Code      | Body
--------------------------------------------|------------------|-------------------------------------------------
Unauthorized                                | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
Invalid `date` format                       | 400 BAD REQUEST  | `{"detail": "Invalid date format", "format": "YYYY-MM-DD"}`
User has not connected their Fitbit account | 400 BAD REQUEST  | `{"detail": "User has not yet authorized"}`

## /update

### Method
`PUT`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body

Any of followings:

```json
{
    "username": "test", // username for login
    "password": "test123@", // password for login
    "first_name": "test", // user profile first name
    "last_name": "test", // user profile last name
    "email": "test@exmaple.com" // user email
}
```

#### Succeed
Status Code: `200 OK`

```json
{
    "details": "Successfully updated",
    "username": "test", // username
    "first_name": "test", // user profile first name
    "last_name": "test", // user profile last name
    "email": "test@exmaple.com" // user email
}
```

#### Fail

Case                            | Status Code      | Body
--------------------------------|------------------|--------------------------------------------------------------
Unauthorized                    | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
Invalid username/passowrd/email | 400 BAD REQUEST  | `{<reasons>}`


## /delete

### Method
`DELETE`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
```json
{
    "password": "test123@" // Requeired: password for login
}
```

#### Succeed
Status Code: `200 OK`

```json
{
    "details": "Successfully deleted"
}
```

#### Fail

Case                    | Status Code      | Body
------------------------|------------------|--------------------------------------------------------------
Unauthorized            | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
Password does not match | 400 BAD REQUEST  | `{"detail": "Password does not match"}`

## /logs

### Method
`GET`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

### Response
#### Succeed
Status Code: `200 OK`

```json
[
  {
    "id": 40,
    "user": 4,
    "action": "User test updated: first_name, password",
    "created_at": "2022-01-10T20:25:49.738927-05:00"
  },
  {
    "id": 39,
    "user": 4,
    "action": "User test logged in successfully",
    "created_at": "2022-01-10T20:25:42.128372-05:00"
  },
  ...
]
```

#### Fail

Case         | Status Code      | Body
-------------|------------------|--------------------------------------------------------------
Unauthorized | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`

## /token-refresh

### Method
`GET`

### Header
`N/A` 

### Body
```json
{
    "refresh":"ey..." // Requeired: refresh token from the login response
}
```

### Response
#### Succeed
Status Code: `200 OK`

```json
{
  "access": "ey..." // new access token for subsequence accesses
}
```

#### Fail

Case                    | Status Code      | Body
------------------------|------------------|--------------------------------------------------------------
Invalid `refresh` token | 401 UNAUTHORIZED | `{"detail": "Token is invalid or expired", "code": "token_not_valid"}`