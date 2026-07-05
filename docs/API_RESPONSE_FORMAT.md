# Standardized API Response Format

All API endpoints in DevSphere follow a consistent response format for both success and error responses using a generic `StandardResponse[T]` wrapper.

## Success Response Format

```json
{
  "message": "Operation completed successfully",
  "data": {
    "id": "123",
    "name": "Example",
    "created_at": "2024-03-24T10:30:00Z"
  },
  "status": "success"
}
```

### Fields:
- **message** (string, required): Human-readable success message describing the operation
- **data** (T, optional): The actual response data (generic type, can be object, array, string, null, etc.)
- **status** (string, required): Always "success" for successful responses

## Error Response Format

```json
{
  "message": "Email already in use",
  "data": null,
  "status": "error"
}
```

### Fields:
- **message** (string, required): Human-readable error message
- **data** (any, optional): Additional error details or context
- **status** (string, required): Always "error" for error responses

## HTTP Status Codes

| Status Code | Exception | Meaning |
|-------------|-----------|---------|
| 200 | N/A | Success |
| 400 | ValidationException | Bad request / validation error |
| 401 | AuthenticationException | Unauthorized / invalid credentials |
| 403 | PermissionDeniedException | Forbidden / insufficient permissions |
| 404 | NotFoundException | Resource not found |
| 500 | DevsphereException | Internal server error |

## Examples

### Create User (Success)
```bash
POST /api/v1/users/create-user
```

Response:
```json
{
  "message": "User created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "john_doe",
    "is_admin": false,
    "is_email_verified": false,
    "created_at": "2024-03-24T10:30:00Z",
    "updated_at": "2024-03-24T10:30:00Z"
  },
  "status": "success"
}
```

### Login (Success)
```bash
POST /api/v1/login
```

Response:
```json
{
  "message": "Tokens generated successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "status": "success"
}
```

### Get All Users (Success)
```bash
GET /api/v1/users/admin/get-user/all
Authorization: Bearer {access_token}
```

Response:
```json
{
  "message": "All users fetched successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "username": "john_doe",
      "is_admin": false,
      "is_email_verified": true,
      "created_at": "2024-03-24T10:30:00Z",
      "updated_at": "2024-03-24T10:30:00Z"
    }
  ],
  "status": "success"
}
```

### Create Blog (Success)
```bash
POST /api/v1/blogs/create-blog
Authorization: Bearer {access_token}
```

Response:
```json
{
  "message": "Blog created successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "My First Blog",
    "content": "Blog content here...",
    "author_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-03-24T10:30:00Z",
    "updated_at": "2024-03-24T10:30:00Z"
  },
  "status": "success"
}
```

### Validation Error (400)
```bash
POST /api/v1/users/create-user
```

Response:
```json
{
  "message": "Email already in use",
  "data": null,
  "status": "error"
}
```

### Authentication Error (401)
```bash
POST /api/v1/login
```

Response:
```json
{
  "message": "Invalid credentials",
  "data": null,
  "status": "error"
}
```

### Permission Error (403)
```bash
GET /api/v1/users/123
```

Response:
```json
{
  "message": "Only admins can access other users' details",
  "data": null,
  "status": "error"
}
```

### Not Found Error (404)
```bash
GET /api/v1/blogs/invalid-id
```

Response:
```json
{
  "message": "Blog not found",
  "data": null,
  "status": "error"
}
```

## Using the Response Helpers

### In Routers

Use the `success_response()` helper to wrap service responses:

```python
from app.core.response import success_response
from app.core.schemas import StandardResponse

@router.post("/create-user", response_model=StandardResponse[UserCreateResponse])
async def create_user(request: UserCreate, 
                      user_service: UserService = Depends(get_user_service)):
    response = await user_service.create_user(request)
    return success_response("User created successfully", response)
```

### Generic Response Type

The `StandardResponse[T]` is a generic Pydantic model that accepts any data type:

```python
# Single object response
@router.get("/get-user/{user_id}", response_model=StandardResponse[UserResponse])
async def get_user(...):
    return success_response("User fetched successfully", user_data)

# List response
@router.get("/admin/get-user/all", response_model=StandardResponse[list[UserResponse]])
async def get_all_users(...):
    return success_response("All users fetched successfully", users_list)

# Simple data response
@router.post("/logout", response_model=StandardResponse[dict])
async def logout(...):
    return success_response("Logged out successfully", {})
```

### Error Handling

Error responses are automatically handled by exception handlers. Services and routers should raise appropriate exceptions:

```python
from app.core.exception import ValidationException, NotFoundException

# Exception handling is automatic - returns error response
raise ValidationException("Email already in use")
raise NotFoundException("User")
```

## Async Task Tracking

When an operation triggers a background task (e.g., sending emails), the response includes task tracking information in the message or via separate endpoints:

```bash
GET /api/v1/users/task/status/{task_id}
```

Response:
```json
{
  "task_id": "51a828dd-f974-4e25-ab3d-e1eb51afd318",
  "status": "SUCCESS",
  "result": null,
  "error": null
}
```

## Implementation Guidelines

1. **Always use `success_response()` in routers** to wrap service responses
2. **Specify the generic type in `response_model`** - e.g., `StandardResponse[UserResponse]`
3. **Let exception handlers manage error responses** - don't manually create error responses
4. **Use appropriate generic types** - single objects, lists, or dicts based on the endpoint
5. **Keep messages clear and user-friendly** - they appear in client applications
