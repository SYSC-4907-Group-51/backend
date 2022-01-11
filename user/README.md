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
Not finalized

Successful Status Code: `201 Created`

```json
{
  "id": 4, // user id
  "username": "test", // username
  "first_name": "test", // first name
  "last_name": "test", // last name
  "email": "test@exmaple.com", // email
  "created_at": "2022-01-10T20:06:52.631583-05:00", // the time the user registered
  "updated_at": "2022-01-10T20:06:52.716159-05:00" // the time the user updated their profile
}
```

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

### Response
Not finalized

Successful Status Code: `200 OK`

```json
{
  "id": 4, // user id
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

## /logout

### Method
`POST`

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
  "detail": "Successfully Logged out"
}
```

## /status

### Method
`GET`

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
  "id": 4, // user id
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

### Response
Not finalized

Successful Status Code: `204 No Content`

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

### Response
Not finalized

Successful Status Code: `204 No Content`

## /logs

### Method
`GET`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
`N/A`

### Response
Not finalized

Successful Status Code: `200 OK`

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
Not finalized

Successful Status Code: `200 OK`

```json
{
  "access": "ey..." // new access token for subsequence accesses
}
```