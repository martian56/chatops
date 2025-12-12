# Authentication

ChatOps uses JWT tokens for user authentication and API keys for agent authentication.

## User Authentication (JWT)

### Registration

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "password_confirm": "password123",
  "full_name": "Full Name"
}
```

**Response**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name"
  },
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password123
```

**Response**:
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

### Using Access Token

Include the access token in the `Authorization` header:

```http
GET /api/v1/servers
Authorization: Bearer jwt_access_token
```

### Refresh Token

Access tokens expire after 30 minutes. Use the refresh token to get a new access token:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "jwt_refresh_token"
}
```

**Response**:
```json
{
  "access_token": "new_jwt_access_token",
  "token_type": "bearer"
}
```

## Agent Authentication (API Keys)

### Creating an API Key

1. Log into the web interface
2. Navigate to a server
3. Go to the "API Keys" tab
4. Click "Create API Key"
5. Copy the key immediately (only shown once)

### Using API Key

Agents authenticate via WebSocket by sending an authentication message:

```json
{
  "type": "auth",
  "api_key": "your-api-key-here"
}
```

The API responds with:

```json
{
  "type": "auth_success",
  "server_id": "server-uuid",
  "message": "Connected successfully"
}
```

## Token Expiration

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

## Security Best Practices

1. **Never commit tokens or API keys** to version control
2. **Use HTTPS** in production
3. **Rotate API keys** regularly
4. **Store tokens securely** in the frontend (localStorage or httpOnly cookies)
5. **Revoke compromised keys** immediately

## Next Steps

- [REST Endpoints](rest-endpoints.md)
- [WebSocket API](websocket-api.md)
- [API Keys](api-keys.md)

