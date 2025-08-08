"""Middleware for request logging, security, and performance monitoring."""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, log_error, log_request_info, log_response_info

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log information.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response from next middleware or endpoint
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()
        log_request_info(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            log_response_info(
                request_id=request_id,
                status_code=response.status_code,
                duration=duration,
                content_length=response.headers.get("content-length"),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            log_error(
                error=e,
                context={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration": duration,
                },
            )

            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "message": "An unexpected error occurred",
                },
                headers={"X-Request-ID": request_id},
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"

        # Content Security Policy - Allow Swagger UI resources
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: https://fastapi.tiangolo.com; "
            "font-src 'self' data: https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(self, app, requests_per_minute: int = 60):
        """Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per client
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._request_counts = {}
        self._last_reset = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit and process request.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response from next middleware or endpoint
        """
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Reset counters if minute has passed
        current_time = time.time()
        if current_time - self._last_reset >= 60:
            self._request_counts.clear()
            self._last_reset = current_time

        # Check rate limit
        if client_ip in self._request_counts:
            if self._request_counts[client_ip] >= self.requests_per_minute:
                logger.warning("Rate limit exceeded", client_ip=client_ip)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.requests_per_minute} requests per minute",
                    },
                )
            self._request_counts[client_ip] += 1
        else:
            self._request_counts[client_ip] = 1

        return await call_next(request)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response from next middleware or endpoint
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate performance metrics
        duration = time.time() - start_time

        # Log slow requests
        if duration > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                "Slow request detected",
                path=str(request.url.path),
                method=request.method,
                duration=duration,
                status_code=response.status_code,
            )

        # Add performance headers
        response.headers["X-Processing-Time"] = f"{duration:.3f}s"

        return response


def setup_cors_middleware(app):
    """Setup CORS middleware.

    Args:
        app: FastAPI application
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_middleware(app):
    """Setup all middleware for the application.

    Args:
        app: FastAPI application
    """
    # Add middleware in order (last added is executed first)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # Setup CORS
    setup_cors_middleware(app)
