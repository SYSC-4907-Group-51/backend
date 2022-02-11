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
#### Succeed
Status Code: `201 CREATED`

```json
{
  "authorization_url": "https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23BJ8J&scope=activity+heartrate+profile+settings+sleep&state=1DFJ19S47ODQwOTJH0uDwTQNu9mcbv" // authorization url, need the front-end to redirect
}
```
#### Fail

Case         | Status Code      | Body
-------------|------------------|-----
Unauthorized | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`

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

#### Succeed
Status Code: `302 FOUND`
Location: `TODO`
`N/A`

#### Fail
Case                                     | Status Code | Location
-----------------------------------------|-------------|-----------------
No `state` and/or `code` in query        | 302 FOUND   | `/invaliderror`
User did not select all scopes on Fitbit | 302 FOUND   | `/mismatcherror`
`code` from Fitbit is not valid          | 302 FOUND   | `/invaliderror`
`state` is not valid                     | 302 FOUND   | `/invaliderror`

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
#### Succeed
Status Code: `202 ACCEPTED`

```json
{
  "detail": "Successed"
}
```
#### Fail
Case                                           | Status Code      | Body
-----------------------------------------------|------------------|------------------------------------------
Unauthorized                                   | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
User's Fitbit authorization is no longer valid | 403 FORBIDDEN | `{"details": "User is no longer authorized"}`
A retrieving task is already queued            | 403 FORBIDDEN | `{"details": "A retreiving task is already waiting or running."}`


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
#### Succeed
Status Code: `200 OK`

```json
{
  "detail": "Successed"
}
```
#### Fail
Case                                      | Status Code      | Body
------------------------------------------|------------------|------------------------------------------
Unauthorized                              | 401 UNAUTHORIZED | `{"detail": "Given token not valid for any token type", ...}`
User have available keys in their account | 403 FORBIDDEN    | `{"details": "Keys are still in use, authorization cannot be deleted!"}`