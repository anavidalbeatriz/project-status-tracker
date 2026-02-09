# API Endpoints Documentation

## Base URL

All API endpoints are prefixed with `/api/v1`

**Development:** `http://localhost:8000/api/v1`

## Authentication

Most endpoints require authentication using JWT Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

To get an access token, use the login endpoints below.

---

## Root Endpoints

### GET `/`
Get API information.

**URL:**
```
http://localhost:8000/api/v1/
```

**Response:**
```json
{
  "message": "API v1",
  "version": "1.0.0"
}
```

---

## Authentication Endpoints

### POST `/auth/register`
Register a new user.

**URL:**
```
http://localhost:8000/api/v1/auth/register
```

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 Bad Request` - Email already registered

---

### POST `/auth/login`
Login using OAuth2 password flow (form data).

**URL:**
```
http://localhost:8000/api/v1/auth/login
```

**Authentication:** Not required

**Request Body (form-data):**
```
username: user@example.com
password: securepassword
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Incorrect email or password

---

### POST `/auth/login/json`
Login using JSON body.

**URL:**
```
http://localhost:8000/api/v1/auth/login/json
```

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Incorrect email or password

---

### GET `/auth/me`
Get current authenticated user information.

**URL:**
```
http://localhost:8000/api/v1/auth/me
```

**Authentication:** Required (Bearer token)

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token

---

## User Management Endpoints

### GET `/users/`
Get all users (paginated).

**URL:**
```
http://localhost:8000/api/v1/users/
```

**With pagination:**
```
http://localhost:8000/api/v1/users/?skip=0&limit=100
```

**Authentication:** Required (Admin only)

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum number of records to return

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
  },
  {
    "id": 2,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not enough permissions (admin required)

---

### GET `/users/{user_id}`
Get a specific user by ID.

**URL (example with user_id=1):**
```
http://localhost:8000/api/v1/users/1
```

**Authentication:** Required
- Users can view their own profile
- Admins can view any user

**Path Parameters:**
- `user_id` (int) - User ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not enough permissions
- `404 Not Found` - User not found

---

### POST `/users/`
Create a new user.

**URL:**
```
http://localhost:8000/api/v1/users/
```

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "name": "New User",
  "role": "user"
}
```

**Response:** `201 Created`
```json
{
  "id": 3,
  "email": "newuser@example.com",
  "name": "New User",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 Bad Request` - Email already registered
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not enough permissions (admin required)

---

### PUT `/users/{user_id}`
Update a user.

**URL (example with user_id=1):**
```
http://localhost:8000/api/v1/users/1
```

**Authentication:** Required
- Users can update their own profile
- Admins can update any user
- Only admins can change user roles

**Path Parameters:**
- `user_id` (int) - User ID

**Request Body (all fields optional):**
```json
{
  "email": "updated@example.com",
  "name": "Updated Name",
  "role": "tech_lead",
  "password": "newpassword"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "updated@example.com",
  "name": "Updated Name",
  "role": "tech_lead",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not enough permissions or trying to change role without admin privileges
- `404 Not Found` - User not found

---

### DELETE `/users/{user_id}`
Delete a user.

**URL (example with user_id=1):**
```
http://localhost:8000/api/v1/users/1
```

**Authentication:** Required (Admin only)

**Path Parameters:**
- `user_id` (int) - User ID

**Response:** `204 No Content`

**Error Responses:**
- `400 Bad Request` - Cannot delete your own account
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not enough permissions (admin required)
- `404 Not Found` - User not found

---

## User Roles

The API supports three user roles:

- **`user`** - Regular user (default)
- **`tech_lead`** - Tech lead with elevated permissions
- **`admin`** - Administrator with full access

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
Validation errors (from Pydantic):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These interfaces allow you to:
- View all available endpoints
- See request/response schemas
- Test endpoints directly from the browser
- View authentication requirements

---

## Quick Reference - All URLs

### Root
- `GET http://localhost:8000/api/v1/`

### Authentication
- `POST http://localhost:8000/api/v1/auth/register`
- `POST http://localhost:8000/api/v1/auth/login`
- `POST http://localhost:8000/api/v1/auth/login/json`
- `GET http://localhost:8000/api/v1/auth/me`

### Users
- `GET http://localhost:8000/api/v1/users/`
- `GET http://localhost:8000/api/v1/users/{user_id}` (replace {user_id} with actual ID)
- `POST http://localhost:8000/api/v1/users/`
- `PUT http://localhost:8000/api/v1/users/{user_id}` (replace {user_id} with actual ID)
- `DELETE http://localhost:8000/api/v1/users/{user_id}` (replace {user_id} with actual ID)

---

## Example Usage

### 1. Register a new user
**URL:**
```
http://localhost:8000/api/v1/auth/register
```

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "name": "John Doe"
  }'
```

### 2. Login and get token
**URL:**
```
http://localhost:8000/api/v1/auth/login/json
```

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### 3. Get current user info
**URL:**
```
http://localhost:8000/api/v1/auth/me
```

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Get all users (admin only)
**URL:**
```
http://localhost:8000/api/v1/users/?skip=0&limit=10
```

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Project Management Endpoints

### GET `/projects/`
Get all projects (paginated with search).

**URL:**
```
http://localhost:8000/api/v1/projects/
```

**With pagination and search:**
```
http://localhost:8000/api/v1/projects/?skip=0&limit=100&search=project_name
```

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100, max: 100) - Maximum number of records to return
- `search` (string, optional) - Search by project name or client

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Project Alpha",
    "client": "Client A",
    "created_by": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token

---

### GET `/projects/{project_id}`
Get a specific project by ID.

**URL (example with project_id=1):**
```
http://localhost:8000/api/v1/projects/1
```

**Authentication:** Required (Bearer token)

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Project Alpha",
  "client": "Client A",
  "created_by": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null,
  "creator": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Project not found

---

### POST `/projects/`
Create a new project.

**URL:**
```
http://localhost:8000/api/v1/projects/
```

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "name": "Project Alpha",
  "client": "Client A"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Project Alpha",
  "client": "Client A",
  "created_by": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 Bad Request` - Project with this name already exists
- `401 Unauthorized` - Invalid or missing token

---

### PUT `/projects/{project_id}`
Update a project.

**URL (example with project_id=1):**
```
http://localhost:8000/api/v1/projects/1
```

**Authentication:** Required (Bearer token)

**Request Body (all fields optional):**
```json
{
  "name": "Updated Project Name",
  "client": "Updated Client Name"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "client": "Updated Client Name",
  "created_by": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Project with this name already exists
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Project not found

---

### DELETE `/projects/{project_id}`
Delete a project.

**URL (example with project_id=1):**
```
http://localhost:8000/api/v1/projects/1
```

**Authentication:** Required (Bearer token)

**Response:** `204 No Content`

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Project not found

**Note:** Deleting a project will also delete all associated project statuses and transcriptions (cascade delete).

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Passwords are hashed using bcrypt before storage
- JWT tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Email addresses must be valid and unique
- User roles are case-sensitive: `user`, `tech_lead`, `admin`
- Project names should be unique (validation enforced)
- Deleting a project cascades to delete related statuses and transcriptions