# How to Get and Use Authentication Token

## Step 1: Register a User (if you haven't already)

**Endpoint:** `POST http://localhost:8000/api/v1/auth/register`

**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "securepassword",
  "name": "Admin User"
}
```

This will create a user with role `user` by default.

## Step 2: Login to Get Token

**Endpoint:** `POST http://localhost:8000/api/v1/auth/login/json`

**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzA3MjM0NTYwfQ.xxxxx",
  "token_type": "bearer"
}
```

**Copy the `access_token` value!**

## Step 3: Use Token in Protected Endpoints

For any endpoint that requires authentication, add the token to the Authorization header:

**Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzA3MjM0NTYwfQ.xxxxx
```

## In Postman

### Option 1: Using the Collection (Recommended)
1. Run the **"Login (JSON)"** request
2. The token will be automatically saved to the environment variable `{{access_token}}`
3. All other requests will automatically use this token

### Option 2: Manual Setup
1. Go to the request that needs authentication (e.g., "Get All Users")
2. Click on the **Authorization** tab
3. Select **Type: Bearer Token**
4. Paste your token in the **Token** field

### Option 3: Using Headers
1. Go to the **Headers** tab
2. Add a new header:
   - **Key:** `Authorization`
   - **Value:** `Bearer YOUR_TOKEN_HERE`

## Creating an Admin User

The `/users/` endpoint requires admin role. To create an admin user, you have two options:

### Option 1: Direct Database Update (Quick)
Connect to your PostgreSQL database and update the user role:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

### Option 2: Use the Create User Endpoint (Requires Admin)
If you already have an admin user, you can create new admin users via:
- `POST /api/v1/users/` (requires admin token)

**Request Body:**
```json
{
  "email": "newadmin@example.com",
  "password": "securepassword",
  "name": "New Admin",
  "role": "admin"
}
```

## Token Expiration

Tokens expire after **30 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`).

If you get a 401 error, your token may have expired. Simply login again to get a new token.

## Testing Token

You can test if your token is valid by calling:

**Endpoint:** `GET http://localhost:8000/api/v1/auth/me`

**Header:**
```
Authorization: Bearer YOUR_TOKEN
```

If successful, it will return your user information.
