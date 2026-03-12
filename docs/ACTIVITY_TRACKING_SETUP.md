# Activity Tracking - Setup Guide

## What Was Added

A complete activity tracking system that monitors all user interactions, requests, responses, and actions throughout the DevSphere application.

## Files Created

```
app/
├── core/
│   └── middleware.py                 # Activity tracking middleware
├── modules/
│   └── activity/
│       ├── __init__.py
│       ├── models.py                 # ActivityLog database model
│       ├── schemas.py                # Pydantic schemas
│       ├── service.py                # Business logic
│       └── router.py                 # API endpoints

docs/
└── ACTIVITY_TRACKING.md              # Implementation documentation
```

## What's Tracked

Every request to the application logs:
- **User**: Who made the request (user_id)
- **Endpoint**: Which API endpoint was called
- **Method**: HTTP method (GET, POST, PUT, PATCH, DELETE)
- **Status**: HTTP response status code
- **Client**: IP address and user agent
- **Payload**: Request and response bodies
- **Performance**: Response time in milliseconds
- **Timestamp**: When the request occurred
- **Action**: Human-readable description of what happened
- **Errors**: Error messages if the request failed

## Database Setup

The `ActivityLog` table is automatically created when the application starts. No manual setup required.

**Table Structure:**
```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
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

-- Performance Indexes
CREATE INDEX idx_user_timestamp ON activity_logs(user_id, timestamp);
CREATE INDEX idx_endpoint_timestamp ON activity_logs(endpoint, timestamp);
CREATE INDEX idx_status_timestamp ON activity_logs(status_code, timestamp);
```

## API Endpoints

All endpoints require authentication and are prefixed with `/api/v1/activities`:

### User Endpoints

| Endpoint | Method | Purpose | Access |
|----------|--------|---------|--------|
| `/user/{user_id}` | GET | Get activities for a user | User (own) or Admin (any) |

### Admin Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/all` | GET | Get all activities |
| `/endpoint` | GET | Get activities for specific endpoint |
| `/filter` | GET | Advanced filtering |
| `/stats` | GET | Activity statistics |

## Quick Start

### 1. Start the Application

```bash
python -m uvicorn app.main:app --reload
```

The middleware is automatically active. No additional configuration needed.

### 2. Get Authentication Token

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

### 3. View Your Activities

```bash
curl -X GET "http://localhost:8000/api/v1/activities/user/1" \
  -H "Authorization: Bearer <your_token>"
```

### 4. Admin: View All Activities

```bash
curl -X GET "http://localhost:8000/api/v1/activities/all" \
  -H "Authorization: Bearer <admin_token>"
```

## Common Queries

### Get Activities for a Specific User

```bash
curl -X GET "http://localhost:8000/api/v1/activities/user/1?limit=50" \
  -H "Authorization: Bearer <token>"
```

### Get Failed Requests (Status 500)

```bash
curl -X GET "http://localhost:8000/api/v1/activities/filter?status_code=500" \
  -H "Authorization: Bearer <admin_token>"
```

### Get Activities for a Specific Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/activities/endpoint?endpoint=/api/v1/blogs/create-blog" \
  -H "Authorization: Bearer <admin_token>"
```

### Get Activities in a Date Range

```bash
curl -X GET "http://localhost:8000/api/v1/activities/filter?start_date=2024-03-01T00:00:00&end_date=2024-03-09T23:59:59" \
  -H "Authorization: Bearer <admin_token>"
```

### Get Activity Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/activities/stats" \
  -H "Authorization: Bearer <admin_token>"
```

### Advanced Filtering

```bash
# Get all POST requests to /api/v1/blogs/create-blog that succeeded (201)
curl -X GET "http://localhost:8000/api/v1/activities/filter?endpoint=/api/v1/blogs/create-blog&method=POST&status_code=201&limit=100" \
  -H "Authorization: Bearer <admin_token>"

# Get all failed requests (500) from user 1 in the last 24 hours
curl -X GET "http://localhost:8000/api/v1/activities/filter?user_id=1&status_code=500&start_date=2024-03-08T10:30:00&limit=100" \
  -H "Authorization: Bearer <admin_token>"
```

## Configuration

### Exclude Endpoints from Tracking

Edit `app/core/middleware.py`:

```python
EXCLUDED_ENDPOINTS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/your-endpoint",  # Add here
}
```

### Disable Request/Response Body Logging

In `app/core/middleware.py`, modify the `dispatch` method to skip body capture:

```python
# Comment out or remove these sections:
# request_body = None
# response_body = None
```

## Logging Messages

The system logs at different levels:

### INFO Level
```
Activity logged: user_id=1, endpoint=/api/v1/blogs/create-blog, method=POST, status_code=201, response_time=45.23ms
Admin user@example.com is fetching all activities with limit=100, offset=0
Retrieved 50 activities
```

### DEBUG Level
```
Request completed: POST /api/v1/blogs/create-blog - Status: 201, Time: 45.23ms, User: 1
Database session created
```

### WARNING Level
```
User user@example.com attempted unauthorized access to user 2 activities
Failed to capture request body: <error>
```

### ERROR Level
```
Failed to log activity in middleware: <error details>
Failed to retrieve activities: <error details>
```

## Permissions

- **Unauthenticated users**: Cannot access any activity endpoints
- **Regular users**: Can view their own activities only
- **Admin users**: Can view all activities and use all endpoints

## Performance

- **Asynchronous logging**: Doesn't block requests
- **Indexed queries**: Fast lookups by user, endpoint, or status
- **Pagination**: Use `limit` and `offset` for large result sets
- **Response time tracking**: Measures actual request processing time

## Troubleshooting

### Activities Not Appearing

1. Check that you're authenticated with a valid token
2. Verify the endpoint isn't in `EXCLUDED_ENDPOINTS`
3. Check application logs for errors
4. Ensure database is running and accessible

### Slow Queries

1. Use pagination: `?limit=50&offset=0`
2. Filter by specific criteria: `?user_id=1&method=POST`
3. Use date ranges: `?start_date=...&end_date=...`

### High Database Usage

1. Implement data retention: Delete activities older than 90 days
2. Exclude more endpoints from tracking
3. Disable body logging for high-volume endpoints

## Using with jq for JSON Processing

### Parse and Filter Results

```bash
TOKEN="your_token_here"

# Get only the endpoint and status_code
curl -s -X GET "http://localhost:8000/api/v1/activities/user/1" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {endpoint, status_code}'

# Get activities with response time > 100ms
curl -s -X GET "http://localhost:8000/api/v1/activities/user/1" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | select(.response_time_ms > 100)'

# Count activities by endpoint
curl -s -X GET "http://localhost:8000/api/v1/activities/all" \
  -H "Authorization: Bearer $TOKEN" | jq 'group_by(.endpoint) | map({endpoint: .[0].endpoint, count: length})'

# Get average response time by endpoint
curl -s -X GET "http://localhost:8000/api/v1/activities/all" \
  -H "Authorization: Bearer $TOKEN" | jq 'group_by(.endpoint) | map({endpoint: .[0].endpoint, avg_time: (map(.response_time_ms) | add / length)})'
```

## Next Steps

1. **Monitor**: Check activity logs regularly for insights
2. **Analyze**: Use statistics endpoint to understand usage patterns
3. **Optimize**: Identify slow endpoints and optimize them
4. **Secure**: Review access logs for suspicious activity
5. **Archive**: Implement retention policy for old logs (optional)
