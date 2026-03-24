# Standardized API Response Format

All API endpoints in DevSphere follow a consistent response format for both success and error responses.

## Success Response Format

```json
{
  "message": "Operation completed successfully",
  "data": {
    "id": "123",
    "name": "Example",
    "created_at": "2024-03-24T10:30:00Z"
  },
  "status": "success",
  "task_id": null
}
```

### Fields:
- **message** (string, required): Human-readable success message describing the operation
- **data** (any, optional): The actual response data (can be object, array, string, null, etc.)
- **status** (string, required): Always "success" for successful responses
- **task_id** (string, optional): Async task ID if the operation triggered a background task (e.g., sending emails)

## Error Response Format

```json
{
  "message": "Email already in use",
  "data": null,
  "status": "error",
  "task_id": null
}
```

### Fields:
- **message** (string, required): Human-readable error message
- **data** (any, optional): Additional error details or context
- **status** (string, required): Always "error" for error responses
- **task_id** (string, optional): Async task ID if applicable

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
  "status": "success",
  "task_id": "51a828dd-f974-4e25-ab3d-e1eb51afd318"
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
  "status": "success",
  "task_id": null
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
  "status": "error",
  "task_id": null
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
  "status": "error",
  "task_id": null
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
  "status": "error",
  "task_id": null
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
  "status": "error",
  "task_id": null
}
```

## Using the Response Helpers

### In Services

```python
from app.core.response import success_response, error_response

# Success response
return success_response(
    message="User created successfully",
    data=user_object,
    task_id="optional-task-id"
)

# Error response (typically handled by exception handlers)
return error_response(
    message="Something went wrong",
    data={"details": "Additional error info"}
)
```

### In Routers

Services return standardized responses. Extract the data for Pydantic validation:

```python
@router.post("/create-user", response_model=UserResponse)
async def create_user(request: UserCreate, user_service: UserService = Depends(get_user_service)):
    response = await user_service.create_user(request)
    # response["data"] contains the actual user object
    return UserResponse.model_validate(convert_user_to_dict(response["data"]))
```

## Async Task Tracking

When an operation triggers a background task (e.g., sending emails), the response includes a `task_id`:

```json
{
  "message": "User created successfully",
  "data": {...},
  "status": "success",
  "task_id": "51a828dd-f974-4e25-ab3d-e1eb51afd318"
}
```

Use the task ID to check the status:

```bash
GET /api/v1/users/task/status/51a828dd-f974-4e25-ab3d-e1eb51afd318
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

1. **Always use `success_response()` in services** for successful operations
2. **Let exception handlers manage error responses** - don't manually create error responses
3. **Extract `data` field in routers** before Pydantic validation
4. **Include `task_id` when dispatching events** that trigger background tasks
5. **Keep messages clear and user-friendly** - they appear in client applications
