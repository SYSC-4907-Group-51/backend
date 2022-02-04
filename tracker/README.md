# API Endpoint /tracker

## /auth

### Method
`POST`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

### Response
Successful Status Code: `200 OK`

```json
{
  "authorization_url": "https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23BJ8J&scope=activity+heartrate+profile+settings+sleep&state=1DFJ19S47ODQwOTJH0uDwTQNu9mcbv" // authorization url, need the front-end to redirect
}
```

## /auth
It is used to redirect the user back to the front-end by Fitbit, user will not be able to access this url by get
### Method
`GET`

### Header
`N/A`

### Body
`N/A`

### Response
Response will use `Location` in header to redirect the user to the landing page of the front-end.

Successful Status Code: `301`

`N/A`

## /refresh
Refresh all tracker data
### Method
`PUT`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
All: `N/A`

or

Specific day:

```json
{
  "date": "<date in yyyy-mm-dd>"
}
```

### Response
Not finalized

Successful Status Code: `200 OK`

```json
{
  "detail": "Successed"
}
```

## /delete
Delete authorization
### Method
`DELETE`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

### Response
Not finalized

Successful Status Code: `200 OK`

```json
{
  "detail": "Successed"
}
```