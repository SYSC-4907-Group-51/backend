# API Endpoint /visualize

## /create-key

### Method
`POST`

### Header
Access token from the `/login` response

`Authorization: Bearer ey...` 

### Body
```json
{
    "notes": "123test" // Optional: user custom notes for the new key
}
```

### Response
Not finalized

Successful Status Code: `201 Created`

```json
{
  "key": 448754, // the key to share with healcare provider
  "notes": "123test" // the user note
}
```

## /show-keys

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
    "key": 275126,
    "notes": "123test",
    "created_at": "2022-01-10T20:35:16.405910-05:00"
  },
  {
    "key": 526500,
    "notes": "123test",
    "created_at": "2022-01-10T20:35:15.234238-05:00"
  },
  ...
]
```

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
Not finalized

Successful Status Code: `204 No Content`

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
Not finalized

Successful Status Code: `200 OK`

```json
{
  "key": 275126,
  "notes": "123test",
  "username": "test"
}
```