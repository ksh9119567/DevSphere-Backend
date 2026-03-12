# Redis Token Inspection Script

## Overview

The `inspect_redis_data.py` script is a utility tool designed to inspect and retrieve all access and refresh tokens stored in Redis along with their associated metadata. This is useful for debugging authentication issues, monitoring active sessions, and understanding token lifecycle management.

## Purpose

This script helps you:
- View all active access tokens and refresh tokens in Redis
- Check token metadata (user email, user ID, admin status, email verification status)
- Monitor token expiration times (TTL - Time To Live)
- Identify expired or invalid tokens
- Debug authentication and session-related issues

## How It Works

### Token Storage Structure

Tokens are stored in Redis with the following key patterns:
- **Access Tokens**: `access_token:{user_email}`
- **Refresh Tokens**: `refresh_token:{user_email}`

Each token is stored as a JSON object containing:
```json
{
  "token": "jwt_token_string",
  "user_email": "user@example.com",
  "created_at": "2026-03-11T10:30:00.000000+00:00",
  "user_id": 123,
  "is_admin": false,
  "is_email_verified": true
}
```

### Script Functions

#### `format_ttl(seconds)`
Converts TTL (Time To Live) in seconds to a human-readable format:
- Less than 60 seconds: `"45s"`
- Less than 1 hour: `"5m 30s"`
- 1 hour or more: `"2h 15m"`
- Expired: `"Expired"`

#### `get_all_tokens()`
Async function that:
1. Queries Redis for all keys matching `access_token:*` and `refresh_token:*` patterns
2. Retrieves TTL for each token
3. Parses JSON token data
4. Returns structured data with all tokens and metadata
5. Handles JSON parsing errors gracefully

#### `display_tokens()`
Async function that:
1. Calls `get_all_tokens()` to fetch token data
2. Formats and displays the data in a readable report format
3. Shows summary statistics (total access and refresh tokens)
4. Lists each token with its metadata and TTL

#### `delete_all_tokens()`
Async function that:
1. Queries Redis for all access and refresh tokens
2. Displays a warning with the count of tokens to be deleted
3. Requires user confirmation (must type "DELETE")
4. Deletes all matching tokens from Redis
5. Displays a success message with deletion count
6. Handles errors gracefully

#### `main()`
Entry point that handles command-line arguments:
- `inspect`: Display all tokens (default)
- `delete`: Delete all tokens with confirmation
- `help`: Show help message

#### `print_help()`
Displays available commands and usage examples

## Usage

### Prerequisites

Ensure your environment is properly configured:
1. Redis server is running and accessible
2. `.env` file contains valid `REDIS_URL` (defaults to `redis://localhost:6379`)
3. Python dependencies are installed (redis, python-dotenv)

### Running the Script

The script supports multiple commands via command-line arguments:

#### Display All Tokens (Default)
```bash
python scripts/inspect_redis_data.py
# or explicitly:
python scripts/inspect_redis_data.py inspect
```

#### Delete All Tokens
```bash
python scripts/inspect_redis_data.py delete
```

This command will:
1. Count all access and refresh tokens in Redis
2. Display a warning showing how many tokens will be deleted
3. Prompt you to type "DELETE" to confirm
4. Delete all tokens if confirmed
5. Show a success message with deletion count

**Warning**: This action logs out all users and cannot be undone.

#### Show Help
```bash
python scripts/inspect_redis_data.py help
```

### Output Example

```
================================================================================
REDIS TOKEN INSPECTION REPORT
================================================================================

SUMMARY:
  Total Access Tokens: 2
  Total Refresh Tokens: 2

--------------------------------------------------------------------------------
ACCESS TOKENS:
--------------------------------------------------------------------------------

[1] Key: access_token:user@example.com
    User Email: user@example.com
    User ID: 1
    Is Admin: False
    Email Verified: True
    Created At: 2026-03-11T10:30:00.000000+00:00
    TTL: 25m 30s

[2] Key: access_token:admin@example.com
    User Email: admin@example.com
    User ID: 2
    Is Admin: True
    Email Verified: True
    Created At: 2026-03-11T10:35:00.000000+00:00
    TTL: 20m 15s

--------------------------------------------------------------------------------
REFRESH TOKENS:
--------------------------------------------------------------------------------

[1] Key: refresh_token:user@example.com
    User Email: user@example.com
    User ID: 1
    Is Admin: False
    Email Verified: True
    Created At: 2026-03-11T10:30:00.000000+00:00
    TTL: 6d 23h 45m

[2] Key: refresh_token:admin@example.com
    User Email: admin@example.com
    User ID: 2
    Is Admin: True
    Email Verified: True
    Created At: 2026-03-11T10:35:00.000000+00:00
    TTL: 6d 23h 40m

================================================================================
```

## Common Use Cases

### 1. Check Active Sessions
Run the script to see all currently active user sessions and their token expiration times.

### 2. Debug Authentication Issues
If a user reports authentication problems, use this script to verify:
- Whether their token exists in Redis
- If the token has expired
- If their user metadata is correctly stored

### 3. Monitor Token Expiration
Check TTL values to understand when tokens will expire and plan for token refresh operations.

### 4. Verify Admin Status
Confirm which users have admin privileges by checking the `Is Admin` field.

### 5. Troubleshoot Token Mismatches
If you suspect token corruption or mismatches, this script helps identify malformed token data.

### 6. Clear All Sessions
Use the delete command to log out all users at once:
```bash
python scripts/inspect_redis_data.py delete
```
This is useful for:
- Emergency security incidents
- Clearing stale sessions after a deployment
- Testing authentication flows
- Resetting the system to a clean state

## Error Handling

The script handles the following scenarios:

- **Redis Connection Failure**: Displays error message if Redis is unreachable
- **JSON Parsing Errors**: Shows "Failed to parse token data" for corrupted tokens
- **No Tokens Found**: Displays "No access tokens found" or "No refresh tokens found"
- **Missing Metadata**: Shows "N/A" for missing fields in token data

## Integration with Development Workflow

### Docker Environment
If running with Docker Compose:
```bash
# Inspect tokens
docker-compose exec backend python scripts/inspect_redis_data.py inspect

# Delete all tokens
docker-compose exec backend python scripts/inspect_redis_data.py delete
```

### Local Development
Ensure Redis is running locally:
```bash
redis-cli ping  # Should return PONG
python scripts/inspect_redis_data.py inspect
```

## Related Documentation

- See `ACTIVITY_TRACKING.md` for user activity tracking
- See `SETUP.md` for environment configuration
- See `app/core/security.py` for token creation and validation logic

## Troubleshooting

**Issue**: "Failed to initialize Redis client"
- **Solution**: Verify Redis is running and `REDIS_URL` in `.env` is correct

**Issue**: "No tokens found"
- **Solution**: This is normal if no users are currently logged in. Log in a user first

**Issue**: Script hangs or times out
- **Solution**: Check Redis connection and network connectivity

## Future Enhancements

Potential improvements to this script:
- Export token data to CSV/JSON file
- Filter tokens by user email or date range
- Delete specific tokens or all expired tokens
- Real-time token monitoring with refresh intervals
