"""
Middleware to track user activities

This module defines a middleware to track user activities.
"""

import logging
import time
import json

from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
from urllib.parse import parse_qs

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import AsyncSessionLocal
from app.modules.activity.service import ActivityService
from app.modules.activity.schemas import ActivityLogCreate
from app.core.security import oauth2_scheme

logger = logging.getLogger(__name__)

# Endpoints to exclude from activity logging
EXCLUDED_ENDPOINTS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
}

# Public endpoints that don't require authentication (no token extraction)
PUBLIC_ENDPOINTS = {
    "/api/v1/login",
    # "/api/v1/refresh-token",
    "/api/v1/users/create-user",
}


class ActivityTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track all user activities"""

    async def dispatch(
            self, request: Request, call_next: Callable
        ) -> Response:
        
        # Skip excluded endpoints
        if request.url.path in EXCLUDED_ENDPOINTS:
            return await call_next(request)

        start_time = time.time()
        
        # Extract request info
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        endpoint = request.url.path
        
        # Capture request body for POST/PUT/PATCH
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_body = body.decode("utf-8") if body else None
            except Exception as e:
                logger.warning(f"Failed to capture request body: {str(e)}")
        
        # Extract user info
        user_email = None
        if endpoint not in PUBLIC_ENDPOINTS:
            # For authenticated endpoints, extract from JWT token
            user_email = await self._extract_user_email(request)
        else:
            # For public endpoints, try to extract email from request body
            user_email = await self._extract_user_email_from_body(
                endpoint, request_body
            )
        
        # Call the next middleware/endpoint
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Capture response body
        response_body = None
        if response.status_code < 500:
            try:
                response_body = response.body.decode("utf-8") if response.body else None
            except Exception as e:
                logger.warning(f"Failed to capture response body: {str(e)}")

        # Log activity asynchronously
        try:
            async with AsyncSessionLocal() as db:
                activity_service = ActivityService(db)
                activity_data = ActivityLogCreate(
                    user_email=user_email,
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_body=request_body,
                    response_body=response_body,
                    response_time_ms=response_time_ms,
                    action_description=self._get_action_description(method, endpoint),
                )
                await activity_service.log_activity(
                    request=activity_data,
                )
        except Exception as e:
            logger.error(f"Failed to log activity in middleware: {str(e)}")
            # Don't raise - let the request continue even if logging fails

        # Add response headers for tracking
        response.headers["X-Response-Time"] = str(response_time_ms)
        response.headers["X-Tracked"] = "true"

        logger.debug(
            f"Request completed: {method} {endpoint} - "
            f"Status: {response.status_code}, Time: {response_time_ms:.2f}ms, User: {user_email}"
        )

        return response

    async def _extract_user_email(
            self, request: Request
        ) -> Optional[str]:
        
        """Extract user email from JWT token in request"""
        try:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            
            # Try to convert to int if it's a user ID
            try:
                return str(user_email)
            except (ValueError, TypeError):
                return None
        except Exception as e:
            logger.debug(f"Failed to extract user email from token: {str(e)}")
            return None

    async def _extract_user_email_from_body(
            self, endpoint: str, request_body: Optional[str]
        ) -> Optional[str]:
        
        """Extract user email from request body for public endpoints"""
        if not request_body:
            return None
        
        try:
            # Try parsing as JSON first (for JSON payloads)
            try:
                body_data = json.loads(request_body)
                # Look for 'email' or 'username' field
                email = body_data.get("email") or body_data.get("username")
                if email:
                    return str(email)
            except json.JSONDecodeError:
                # If not JSON, try form-urlencoded (Postman form-data sends this way)
                body_data = parse_qs(request_body)
                email = body_data.get("email", [None])[0] or body_data.get("username", [None])[0]
                if email:
                    return str(email)
        except Exception as e:
            logger.debug(f"Failed to extract user email from request body in {endpoint}: {str(e)}")
        
        return None

    def _get_client_ip(
            self, request: Request
        ) -> str:
        
        """Extract client IP address from request"""
        if request.client:
            return request.client.host
        
        # Check for X-Forwarded-For header (proxy)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        
        return "unknown"

    def _get_action_description(
            self, method: str, endpoint: str
        ) -> str:
        
        """Generate human-readable action description"""
        method_map = {
            "GET": "Retrieved",
            "POST": "Created",
            "PUT": "Updated",
            "PATCH": "Modified",
            "DELETE": "Deleted",
        }
        
        action = method_map.get(method, "Accessed")
        return f"{action} {endpoint}"
