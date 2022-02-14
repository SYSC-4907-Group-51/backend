# API Endpoint /visualize

## /create-key

### Method
`POST`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body

**Cannot create a key without permissions**

```json
{
    "notes": "3tet",
    "permissions": [
      true, // step_time_series
      true, // heartrate_time_series
      false, // sleep_time_series
      false, // step_intraday_data
      false // heartrate_intraday_data
    ]
}
```

### Response
#### Succeed
Status Code: `201 CREATED`

```json
{
  "key": 876421,
  "notes": "3tet",
  "permissions": [
    true, // step_time_series
    true, // heartrate_time_series
    false, // sleep_time_series
    false, // step_intraday_data
    false // heartrate_intraday_data
 ],
  "created_at": "2022-02-04T19:53:56.020945Z"
}
```
#### Fail

Case                                              | Status Code      | Body
--------------------------------------------------|------------------|-------------------------------------------
Unauthorized                                      | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
The length of the permission array is less than 5 | 400 BAD REQUEST  | `{"detail": "permissions must be 5 in length"}`
The permission array cotains 5 `false`s           | 400 BAD REQUEST  | `{"detail": "cannot create a key without permissions"}`
The permission array cotains non-boolean          | 400 BAD REQUEST  | `{"detail": "permissions must be boolean"}`
User has not yet authorized their Fitbit account  | 403 FORBIDDEN    | `{"detail": "user profile does not exist"}`
User has not tracker data                         | 403 FORBIDDEN    | `{"detail": "user sync status does not exist"}`
User has reached maximum allowable key limit      | 403 FORBIDDEN    | `{"detail": "Maximum allowable key limit is reached", "limit": <integer>}`


## /show-keys

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
    "key": 146171,
    "notes": "1",
    "permissions": [
      true,
      true,
      true,
      true,
      false
    ],
    "created_at": "2022-02-04T19:53:56.020945Z"
  },
  {
    "key": 662346,
    "notes": "1",
    "permissions": [
      true,
      true,
      true,
      true,
      true
    ],
    "created_at": "2022-02-04T19:53:52.075643Z"
  },
  ...
]
```
#### Fail

Case                                              | Status Code      | Body
--------------------------------------------------|------------------|-------------------------------------------
Unauthorized                                      | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`

## /delete-key

### Method
`DELETE`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
```json
{
    "key": 526500 // the key to delete
}
```

### Response
#### Succeed
Status Code: `200 OK`

#### Fail

Case             | Status Code      | Body
-----------------|------------------|-------------------------------------------
Unauthorized     | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`

## /view

### Method
`GET`

### Query
`?username=<user's username>&key=<user provided key>`

### Header
`N/A` 

### Body
`N/A`

### Response
#### Succeed
Status Code: `200 OK`

```json
{
  "access": "ey...", // for data access authorization
  "username": "test",
  "permissions": [
    true,
    true,
    true,
    false, // missing permission for step_intraday_data
    true
  ],
  "available_dates": {
    "step_time_series": [
      "2021-10-09",
      "2021-10-10",
      ...
    ],
    "heartrate_time_series": [
      "2021-10-09",
      "2021-10-10",
      ...
    ],
    "sleep_time_series": [
      "2021-10-10",
      "2021-10-11",
      ...
    ],
    "step_intraday_data": [], // empty here
    "heartrate_intraday_data": [
      "2021-10-09",
      "2021-10-10",
      ...
    ]
  }
}
```

or

```json
{
  "access": "ey...",
  "username": "test",
  "permissions": [
    true,
    true,
    true,
    true,
    true
  ],
  "available_dates": {
    "step_time_series": [
      "2021-10-09",
      "2021-10-10",
      ...
    ],
    "heartrate_time_series": [
      "2021-10-09",
      "2021-10-10",
      ...
    ],
    "sleep_time_series": [
      "2021-10-10",
      "2021-10-11",
      ...
    ],
    "step_intraday_data": [
      "2021-10-10",
      "2021-10-11",
      ...
    ],
    "heartrate_intraday_data": [
      "2021-10-09",
      "2021-10-10",
      ...
    ]
  }
}
```
#### Fail

Case                                  | Status Code      | Body
--------------------------------------|------------------|-------------------------------------------
`username` and `key` are not in query | 400 BAD REQUEST  | `{"detail": "Invalid request"}`
No such username                      | 400 BAD REQUEST  | `{"detail": "No such user"}`
No such key                           | 400 BAD REQUEST  | `{"detail": "No such key"}`

## /intraday

### Method
`GET`

### Header
Access token from the `/view` response

`X-Authorization: Bearer ey...` 

### Query
`?type=<data type: step, heartrate>&date=<date in YYYY-MM-DD>`

eg. `?type=heartrate&date=2022-01-01`

### Response
#### Succeed
Status Code: `200 OK`

```json
{
  "time_series": {
    "date": "2022-01-01",
    "resting_heartrate": 79,
    "heartrate_zones": [
      {
        "caloriesOut": 2313.87425,
        "max": 126,
        "min": 30,
        "minutes": 1418,
        "name": "Out of Range"
      },
      {
        "caloriesOut": 127.00550000000001,
        "max": 149,
        "min": 126,
        "minutes": 18,
        "name": "Fat Burn"
      },
      ...
    ]
  },
  "dataset": [
    {
      "time": "00:00:00",
      "value": 93
    },
    {
      "time": "00:01:00",
      "value": 98
    },
    ...
  ],
  "dataset_type": "minute",
  "dataset_interval": 1
}
```

#### Fail

Case                                             | Status Code      | Body
-------------------------------------------------|------------------|-------------------------------------------
Unauthorized                                     | 401 UNAUTHORIZED | `{"detail": "Authentication credentials were not provided."}`
`type` and `date` are not in query               | 400 BAD REQUEST  | `{"detail": "Invalid type or date"}`
Invalid `date` format                            | 400 BAD REQUEST  | `{"detail": "Invalid date format", "format": "YYYY-MM-DD"}`
No such user                                     | 400 BAD REQUEST  | `{"detail": "No such user"}`
No data for requested `date`                     | 400 BAD REQUEST  | `{"detail": "No data for <date in YYYY-MM-DD>"}`
No permission or no data for requested `type`    | 403 FORBIDDEN    | `{"detail": "No permission or no data available"}`
No such `type`                                   | 403_FORBIDDEN    | `{"detail": "Invalid type", 'types': ["step", "heartrate"]}`

## /time-series

### Method
`GET`

### Header
Access token from the `/view` response

`X-Authorization: Bearer ey...` 

### Query
`?type=<data type: step, heartrate, sleep>&start_date=<date in YYYY-MM-DD>&end_date=<date in YYYY-MM-DD>`

eg. `?type=sleep&start_date=2022-01-01&end_date=2022-01-02`

### Response
#### Succeed
Status Code: `200 OK`

```json
[
  {
    "date": "2022-01-01",
    "start_time": "2022-01-01T06:55:30Z",
    "end_time": "2022-01-01T13:30:00Z",
    "duration": 23640000,
    "efficiency": 84,
    "minutes_after_wakeup": 0,
    "minutes_asleep": 330,
    "minutes_awake": 64,
    "minutes_to_fall_asleep": 0,
    "time_in_bed": 394,
    "levels": [
      {
        "dateTime": "2022-01-01T01:55:30.000",
        "level": "wake",
        "seconds": 1170
      },
      {
        "dateTime": "2022-01-01T02:15:00.000",
        "level": "light",
        "seconds": 720
      },
      ...
    ],
    "summary": {
      "deep": {
        "count": 3,
        "minutes": 80,
        "thirtyDayAvgMinutes": 91
      },
      "light": {
        "count": 29,
        "minutes": 168,
        "thirtyDayAvgMinutes": 181
      },
      "rem": {
        "count": 8,
        "minutes": 82,
        "thirtyDayAvgMinutes": 89
      },
      "wake": {
        "count": 26,
        "minutes": 64,
        "thirtyDayAvgMinutes": 57
      }
    }
  },
  {
    "date": "2022-01-02",
    "start_time": "2022-01-02T07:04:00Z",
    "end_time": "2022-01-02T13:04:30Z",
    "duration": 21600000,
    "efficiency": 86,
    "minutes_after_wakeup": 0,
    "minutes_asleep": 304,
    "minutes_awake": 56,
    "minutes_to_fall_asleep": 0,
    "time_in_bed": 360,
    "levels": [
      {
        "dateTime": "2022-01-02T02:04:00.000",
        "level": "light",
        "seconds": 1470
      },
      {
        "dateTime": "2022-01-02T02:28:30.000",
        "level": "deep",
        "seconds": 2370
      },
      ...
    ],
    "summary": {
      "deep": {
        "count": 3,
        "minutes": 88,
        "thirtyDayAvgMinutes": 91
      },
      "light": {
        "count": 24,
        "minutes": 160,
        "thirtyDayAvgMinutes": 180
      },
      "rem": {
        "count": 4,
        "minutes": 56,
        "thirtyDayAvgMinutes": 88
      },
      "wake": {
        "count": 23,
        "minutes": 56,
        "thirtyDayAvgMinutes": 57
      }
    }
  },
  ...
]
```
#### Fail

Case                                                                             | Status Code      | Body
---------------------------------------------------------------------------------|------------------|-----------
Unauthorized                                                                     | 401 UNAUTHORIZED | `{"detail": "Authentication credentials were not provided."}`
`type` and `start_date` are not in query                                         | 400 BAD REQUEST  | `{"detail": "Invalid type or start_date or end_date"}`
Invalid `start_date` or `end_date` format                                        | 400 BAD REQUEST  | `{"detail": "Invalid date format", "format": "YYYY-MM-DD"}`
No such user                                                                     | 400 BAD REQUEST  | `{"detail": "No such user"}`
No data available                                                                | 400 BAD REQUEST  | `{"detail": "No data available"}`
No data available for requested `type` between `start_date` and `end_date` range | 400 BAD REQUEST  | `{"detail": "No data in between <start_date> and <end_date>"}`
No permission for requested `type`                                               | 403 FORBIDDEN    | `{"detail": "No permission"}`
No such `type`                                                                   | 403_FORBIDDEN    | `{"detail": "Invalid type", 'types': ["step", "heartrate", "sleep"]}`

## /refresh-authorization-key

### Method
`PUT`

### Header
Access token from the `/view` response

`X-Authorization: Bearer ey...` 

### Body
`N/A`

### Response
#### Succeed
Status Code: `201 CREATED`

```json
{
  "access": "ey...", // new access key
}
```

#### Fail

Case                                                                             | Status Code      | Body
---------------------------------------------------------------------------------|------------------|-----------
Unauthorized                                                                     | 401 UNAUTHORIZED | `{"detail": "Authentication credentials were not provided."}`