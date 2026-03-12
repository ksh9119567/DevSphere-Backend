# Authentication Flow Documentation

## Overview

DevSphere implements a **JWT-based authentication system** with Redis token storage, role-based access control, and comprehensive activity tracking. The system uses a dual-token approach (access tokens and refresh tokens) to balance security and user experience.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Authentication System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │   FastAPI    │      │   Security   │      │    Redis     │   │
│  │   Endpoints  │◄────►│   Module     │◄────►│   Storage    │   │
│  └──────────────┘      └──────────────┘      └──────────────┘   │
│         ▲                      ▲                     ▲          │
│         │                      │                     │          │
│  ┌──────┴──────┐      ┌────────┴────────┐   ┌────────┴────────┐ │
│  │   Auth      │      │   Token         │   │   Database      │ │
│  │   Service   │      │   Service       │   │   (PostgreSQL)  │ │
│  └─────────────┘      └─────────────────┘   └─────────────────┘ │
│         ▲                      ▲                      ▲         │
│         │                      │                      │         │
│  ┌──────┴──────────────────────┴──────────────────────┴────────┐│
│  │              Activity Tracking Middleware                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Authentication Service (`app/modules/auth/service.py`)

The core service handling authentication operations:

- **Login**: Validates credentials and creates tokens
- **Refresh**: Issues new tokens using refresh token
- **Logout**: Revokes tokens from Redis

### 2. Token Service (`app/services/token_service.py`)

Manages JWT token creation and validation:

- **Access Token**: Short-lived (30 minutes by default)
- **Refresh Token**: Long-lived (7 days by default)
- **Token Storage**: Both tokens stored in Redis with metadata
- **Token Verification**: Validates JWT signature and Redis presence

### 3. Security Module (`app/core/security.py`)

Provides security utilities:

- **Password Hashing**: Bcrypt via passlib
- **JWT Encoding/Decoding**: Using python-jose
- **Current User Dependency**: FastAPI dependency for protected endpoints
- **Token Validation**: Checks JWT validity and Redis presence

### 4. User Repository (`app/core/repositories/user_repository.py`)

Database operations for user management:

- User creation, retrieval, and updates
- Filters for active and non-deleted users
- Email-based user lookup

### 5. Redis Manager (`app/core/redis_manager.py`)

Manages Redis connection and token storage:

- Async Redis client initialization
- Token persistence with TTL
- Token retrieval and deletion

## Authentication Flow Diagrams

### User Registration Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/users/create-user
       │ {username, email, password, ...}
       ▼
┌──────────────────────────────────────┐
│   UserService.create_user()          │
├──────────────────────────────────────┤
│ 1. Hash password with bcrypt         │
│ 2. Create user in database           │
│ 3. Call AuthService.login()          │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   AuthService.login()                │
├──────────────────────────────────────┤
│ 1. Verify credentials                │
│ 2. Create access token (JWT)         │
│ 3. Create refresh token (JWT)        │
│ 4. Store both in Redis               │
└──────┬───────────────────────────────┘
       │
       ▼
┌───────────────────────┐
│   Client              │
│ Returns:              │
│ - access_token        │
│ - refresh_token       │
│ - token_type: "bearer"│
│ - user data           │
└───────────────────────┘
```

### Login Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/login
       │ {username: email, password}
       ▼
┌──────────────────────────────────────┐
│   AuthService.login()                │
├──────────────────────────────────────┤
│ 1. Query user by email               │
│ 2. Verify password with bcrypt       │
│    - If invalid: raise exception     │
│ 3. Gather user info:                 │
│    - user_id, is_admin,              │
│    - is_email_verified               │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   TokenService.create_access_token() │
├──────────────────────────────────────┤
│ 1. Create JWT payload:               │
│    - sub: email                      │
│    - exp: now + 30 minutes           │
│ 2. Encode with SECRET_KEY            │
│ 3. Store in Redis:                   │
│    Key: access_token:{email}         │
│    Value: {token, metadata}          │
│    TTL: 30 minutes                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   TokenService.create_refresh_token()│
├──────────────────────────────────────┤
│ 1. Create JWT payload:               │
│    - sub: email                      │
│    - exp: now + 7 days               │
│ 2. Encode with REFRESH_SECRET_KEY    │
│ 3. Store in Redis:                   │
│    Key: refresh_token:{email}        │
│    Value: {token, metadata}          │
│    TTL: 7 days                       │
└──────┬───────────────────────────────┘
       │
       ▼
┌───────────────────────┐
│   Client              │
│ Returns:              │
│ - access_token        │
│ - refresh_token       │
│ - token_type: "bearer"│
└───────────────────────┘
```

### Protected Endpoint Access Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ GET /api/v1/protected-endpoint
       │ Header: Authorization: Bearer {access_token}
       ▼
┌──────────────────────────────────────┐
│   ActivityTrackingMiddleware         │
├──────────────────────────────────────┤
│ 1. Extract token from header         │
│ 2. Log request details               │
│ 3. Pass to next middleware           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   get_current_user() Dependency      │
├──────────────────────────────────────┤
│ 1. Decode JWT with SECRET_KEY        │
│    - If invalid: raise 401           │
│ 2. Extract email from payload        │
│ 3. Check Redis for token:            │
│    - Key: access_token:{email}       │
│    - If not found: raise 401         │
│ 4. Verify token matches stored token │
│    - If mismatch: raise 401          │
│ 5. Query user from database          │
│    - If not found: raise 401         │
│ 6. Return User object                │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   Endpoint Handler                   │
├──────────────────────────────────────┤
│ Receives current_user object         │
│ Processes request                    │
│ Returns response                     │
└──────┬───────────────────────────────┘
       │
       ▼
┌─────────────────┐
│   Client        │
│ Returns:        │
│ - Response data │
│ - Status: 200 OK│
└─────────────────┘
```

### Token Refresh Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/refresh
       │ Form: refresh_token={refresh_token}
       ▼
┌──────────────────────────────────────┐
│   AuthService.refresh()              │
├──────────────────────────────────────┤
│ 1. Validate refresh_token provided   │
│ 2. Call verify_and_refresh_token()   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   TokenService.verify_and_refresh()  │
├──────────────────────────────────────┤
│ 1. Decode refresh token with         │
│    REFRESH_SECRET_KEY                │
│    - If invalid: raise 401           │
│ 2. Extract email from payload        │
│ 3. Query Redis for stored token:     │
│    - Key: refresh_token:{email}      │
│    - If not found: raise 401         │
│ 4. Parse stored token data           │
│ 5. Verify token matches              │
│    - If mismatch: raise 401          │
│ 6. DELETE old access token from Redis│
│ 7. DELETE old refresh token from Redis
│ 8. Create NEW access token           │
│ 9. Create NEW refresh token          │
│ 10. Store both in Redis              │
└──────┬───────────────────────────────┘
       │
       ▼
┌───────────────────────┐
│   Client              │
│ Returns:              │
│ - new_access_token    │
│ - new_refresh_token   │
│ - token_type: "bearer"│
└───────────────────────┘
```

### Logout Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/logout
       │ Header: Authorization: Bearer {access_token}
       ▼
┌──────────────────────────────────────┐
│   get_current_user() Dependency      │
├──────────────────────────────────────┤
│ Validates token (same as protected   │
│ endpoint access)                     │
│ Returns User object                  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   AuthService.logout()               │
├──────────────────────────────────────┤
│ 1. Delete access token from Redis:   │
│    Key: access_token:{email}         │
│ 2. (Optional) Delete refresh token:  │
│    Key: refresh_token:{email}        │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────┐
│   Client             │
│ Returns:             │
│ - Status: 200 OK     │
│ - Message: Logged out│
└──────────────────────┘
```

## Token Structure

### Access Token (JWT)

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "user@example.com",
  "exp": 1710158400,
  "iat": 1710156600
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  SECRET_KEY
)
```

### Redis Storage Format

**Access Token Entry:**
```
Key: access_token:user@example.com
Value: {
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_email": "user@example.com",
  "created_at": "2026-03-11T10:30:00.000000+00:00",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_admin": false,
  "is_email_verified": true
}
TTL: 1800 seconds (30 minutes)
```

**Refresh Token Entry:**
```
Key: refresh_token:user@example.com
Value: {
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_email": "user@example.com",
  "created_at": "2026-03-11T10:30:00.000000+00:00",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_admin": false,
  "is_email_verified": true
}
TTL: 604800 seconds (7 days)
```

## Configuration

### Environment Variables

```env
# JWT Configuration
SECRET_KEY=your-secret-key-for-access-tokens
REFRESH_SECRET_KEY=your-secret-key-for-refresh-tokens
ALGORITHM=HS256

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

## Security Features

### 1. Password Security
- Passwords hashed with bcrypt (salted and iterated)
- Never stored in plain text
- Verified using constant-time comparison

### 2. Token Security
- JWT tokens signed with SECRET_KEY
- Tokens stored in Redis (stateful)
- Token revocation possible via Redis deletion
- Separate keys for access and refresh tokens

### 3. Token Validation
- JWT signature verification
- Token presence check in Redis
- Token expiration validation
- Token mismatch detection

### 4. Session Management
- Dual-token system reduces exposure of long-lived tokens
- Access tokens short-lived (30 minutes)
- Refresh tokens longer-lived (7 days)
- Old tokens invalidated on refresh

### 5. Activity Tracking
- All requests logged with user identification
- IP address tracking
- Request/response body capture
- Performance metrics (response time)

### 6. Role-Based Access Control
- Admin flag stored in token metadata
- Admin-only endpoints protected
- User-specific resource access

## Error Handling

### Authentication Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Invalid credentials | 401 | Wrong email/password | Verify credentials |
| Token expired | 401 | Access token TTL exceeded | Use refresh token |
| Invalid token | 401 | Malformed JWT | Re-login |
| Token not found | 401 | User logged out | Re-login |
| User not found | 401 | User deleted/inactive | Contact admin |
| Permission denied | 403 | Not admin for admin endpoint | Use admin account |

### Exception Classes

```python
# Base exception
DevsphereException

# Specific exceptions
AuthenticationException("Invalid credentials")
NotFoundException("User")
PermissionDeniedException("Permission denied")
ValidationException("Email already in use")
```

## API Endpoints

### Authentication Endpoints

#### 1. Login
```
POST /api/v1/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Register
```
POST /api/v1/users/create-user
Content-Type: application/json

{
  "username": "john_doe",
  "email": "user@example.com",
  "password": "password123",
  "profile_image": "https://...",
  "profile_bio": "Bio text"
}

Response (200):
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "user@example.com",
    "is_admin": false,
    "is_email_verified": false
  },
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

#### 3. Refresh Token
```
POST /api/v1/refresh
Content-Type: application/x-www-form-urlencoded

refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 4. Logout
```
POST /api/v1/logout
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Logged out successfully"
}
```

## Protected Endpoints

Any endpoint requiring authentication uses the `get_current_user` dependency:

```python
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}
```

The `current_user` object contains:
- `id`: User UUID
- `username`: Username
- `email`: Email address
- `is_admin`: Admin flag
- `is_email_verified`: Email verification status
- `is_active`: Active status
- `is_deleted`: Deletion status

## Admin-Only Endpoints

```python
@router.get("/admin")
async def admin_endpoint(current_user: User = Depends(get_current_admin_user)):
    return {"message": "Admin only"}
```

The `get_current_admin_user` dependency checks `is_admin` flag and raises 403 if false.

## Token Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Token Lifecycle                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CREATION                                                │
│     └─► Login/Register ──► JWT created ──► Stored in Redis  │
│                                                             │
│  2. ACTIVE                                                  │
│     └─► Token valid ──► Used for requests ──► Validated     │
│                                                             │
│  3. REFRESH (Optional)                                      │
│     └─► Before expiry ──► Old tokens deleted ──► New tokens │
│                                                             │
│  4. EXPIRATION                                              │
│     └─► TTL reached ──► Auto-deleted from Redis             │
│                                                             │
│  5. REVOCATION (Manual)                                     │
│     └─► Logout ──► Deleted from Redis ──► Invalid           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### For Developers

1. **Always use `get_current_user` dependency** for protected endpoints
2. **Store tokens securely** on client (httpOnly cookies recommended)
3. **Refresh tokens proactively** before expiration
4. **Handle 401 errors** by redirecting to login
5. **Log authentication events** for security auditing
6. **Never expose SECRET_KEY** in code or logs

### For Clients

1. **Store access token** in memory or httpOnly cookie
2. **Store refresh token** in secure storage (httpOnly cookie)
3. **Include access token** in Authorization header: `Bearer {token}`
4. **Refresh token** 5 minutes before expiration
5. **Clear tokens** on logout
6. **Handle token expiration** gracefully

### For Operations

1. **Monitor Redis** for token storage
2. **Rotate SECRET_KEY** periodically
3. **Monitor failed login attempts** for security
4. **Clear stale tokens** using inspection script
5. **Backup Redis** for session persistence
6. **Monitor token refresh rates** for anomalies

## Troubleshooting

### Issue: "Could not validate credentials"

**Causes:**
- Invalid token format
- Token expired
- Token not in Redis
- User deleted/inactive

**Solution:**
- Re-login to get new tokens
- Check Redis connection
- Verify user exists in database

### Issue: "Refresh token expired or revoked"

**Causes:**
- Refresh token TTL exceeded (7 days)
- Token manually deleted
- User logged out

**Solution:**
- Re-login to get new tokens
- Check token expiration time

### Issue: "Permission denied"

**Causes:**
- User not admin
- Accessing admin-only endpoint

**Solution:**
- Use admin account
- Check user permissions

### Issue: "User not found"

**Causes:**
- User deleted
- User inactive
- Email changed

**Solution:**
- Verify user exists
- Check user status in database

## Related Documentation

- See `REDIS_TOKEN_INSPECTION.md` for token inspection and debugging
- See `ACTIVITY_TRACKING.md` for activity logging details
- See `SETUP.md` for environment configuration
