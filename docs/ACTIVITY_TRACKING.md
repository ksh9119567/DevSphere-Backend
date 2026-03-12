# Activity Tracking - Implementation Guide

## Overview

The DevSphere project includes a comprehensive activity tracking system that monitors all user interactions, requests, responses, and actions performed within the application. This system provides detailed insights into user behavior, system performance, and security auditing.

## How Activity Tracking Works

### Request Flow

1. **Request Arrives** → `ActivityTrackingMiddleware` intercepts the HTTP request
2. **Extract Metadata** → Middleware extracts:
   - User ID from JWT token
   - Client IP address (with proxy support via X-Forwarded-For)
   - User agent from headers
   - HTTP method and endpoint path
   - Request body (for POST/PUT/PATCH)
3. **Process Request** → Endpoint handler executes the business logic
4. **Capture Response** → Middleware captures:
   - HTTP status code
   - Response body
   - Response time in milliseconds
   - Action description (auto-generated)
5. **Log Activity** → Asynchronously stores activity in database without blocking the request
6. **Return Response** → Response is returned to client with tracking headers

### Middleware Implementation

The `ActivityTrackingMiddleware` class in `app/core/middleware.py`:

```python
class ActivityTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Check if endpoint should be excluded
        # 2. Extract user info from JWT token
        # 3. Capture request metadata
        # 4. Call next middleware/endpoint
        # 5. Capture response metadata
        # 6. Log activity asynchronously
        # 7. Add tracking headers to response
```

**Key Features:**
- Non-blocking asynchronous logging
- Automatic user extraction from JWT tokens
- IP address tracking with proxy support
- Request/response body capture
- Response time measurement
- Excluded endpoints configuration

### Database Model

The `ActivityLog` model stores:
- User context (user_id, IP, user agent)
- Request details (endpoint, method, body)
- Response details (status code, body, time)
- Metadata (timestamp, action description, errors)

**Indexes for Performance:**
- `idx_user_timestamp` - Fast user activity queries
- `idx_endpoint_timestamp` - Fast endpoint analysis
- `idx_status_timestamp` - Fast status code filtering

### Service Layer

The `ActivityService` class provides:
- `log_activity()` - Store activity in database
- `get_all_activities()` - Retrieve all activities with pagination
- `get_user_activities()` - Get activities for specific user
- `get_endpoint_activities()` - Get activities for specific endpoint
- `get_filtered_activities()` - Advanced filtering with multiple criteria
- `get_activity_stats()` - Get activity statistics

### API Router

The `ActivityRouter` exposes endpoints:
- **User Endpoints**: `/user/{user_id}` - Users view own, admins view any
- **Admin Endpoints**: `/all`, `/endpoint`, `/filter`, `/stats` - Admin only

**Access Control:**
- All endpoints require JWT authentication
- Admin-only endpoints check `is_admin` flag
- User endpoints enforce user-specific access

### Logging Throughout the App

**Middleware Logging:**
```
INFO - Activity logged: user_id=1, endpoint=/api/v1/blogs/create-blog, method=POST, status_code=201, response_time=45.23ms
DEBUG - Request completed: POST /api/v1/blogs/create-blog - Status: 201, Time: 45.23ms, User: 1
```

**Service Logging:**
```
INFO - Retrieved 50 activities
INFO - Retrieved 10 activities for user_id=1
ERROR - Failed to log activity in middleware: <error details>
```

**Router Logging:**
```
INFO - Admin user@example.com is fetching all activities with limit=100, offset=0
WARNING - User user@example.com attempted unauthorized access to user 2 activities
```

### Integration Points

**In app/main.py:**
```python
from app.core.middleware import ActivityTrackingMiddleware

app = FastAPI(title="DevSphere", lifespan=lifespan)
app.add_middleware(ActivityTrackingMiddleware)
```

**In app/api/v1/router.py:**
```python
from app.modules.activity.router import router as activity_router

router.include_router(activity_router)
```

### Performance Optimizations

1. **Asynchronous Logging** - Doesn't block request processing
2. **Database Indexes** - Composite indexes for common queries
3. **Pagination** - Supports limit/offset for large result sets
4. **Response Time Tracking** - Measures actual request processing time
5. **Excluded Endpoints** - Skips documentation and health checks

### Security Implementation

1. **JWT Authentication** - All endpoints require valid token
2. **Authorization Checks** - Admin-only endpoints and user-specific access
3. **IP Tracking** - Captures client IP with proxy support
4. **User Agent Tracking** - Records browser/client information
5. **Error Logging** - Captures error messages for auditing

## Architecture

### Components

1. **ActivityTrackingMiddleware** (`app/core/middleware.py`)
   - Intercepts all HTTP requests and responses
   - Extracts user information from JWT tokens
   - Captures request/response metadata
   - Logs activity asynchronously to avoid blocking requests

2. **ActivityLog Model** (`app/modules/activity/models.py`)
   - SQLAlchemy ORM model for storing activity logs
   - Indexed fields for efficient querying
   - Stores comprehensive request/response information

3. **ActivityService** (`app/modules/activity/service.py`)
   - Business logic for activity logging and retrieval
   - Provides filtering and statistical capabilities
   - Handles database operations

4. **Activity Router** (`app/modules/activity/router.py`)
   - REST API endpoints for accessing activity logs
   - Admin-only endpoints for comprehensive access
   - User-specific endpoints with permission checks

## Database Schema

### ActivityLog Table

```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY (user.id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    request_body TEXT,
    response_body TEXT,
    response_time_ms FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_description VARCHAR(255),
    error_message TEXT
);

-- Indexes for performance
CREATE INDEX idx_user_timestamp ON activity_logs(user_id, timestamp);
CREATE INDEX idx_endpoint_timestamp ON activity_logs(endpoint, timestamp);
CREATE INDEX idx_status_timestamp ON activity_logs(status_code, timestamp);
```

## Tracked Information

Each activity log entry captures:

| Field | Description | Example |
|-------|-------------|---------|
| `user_id` | ID of the user performing the action | 1 |
| `endpoint` | API endpoint accessed | `/api/v1/blogs/create-blog` |
| `method` | HTTP method used | `POST` |
| `status_code` | HTTP response status code | 201 |
| `ip_address` | Client IP address | `192.168.1.100` |
| `user_agent` | Client user agent string | `Mozilla/5.0...` |
| `request_body` | Request payload (JSON) | `{"title": "My Blog"}` |
| `response_body` | Response payload (JSON) | `{"id": 1, "title": "My Blog"}` |
| `response_time_ms` | Request processing time in milliseconds | 45.23 |
| `timestamp` | When the request was made | `2024-03-09 10:30:45` |
| `action_description` | Human-readable action summary | `Created /api/v1/blogs/create-blog` |
| `error_message` | Error details if request failed | `Validation error: title required` |


