"""
Custom authentication views with SPECTACULAR documentation.
"""
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="Obtain JWT token",
    description="Authenticate user and obtain JWT access and refresh tokens.",
    tags=["Authentication"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Username or email"},
                "password": {"type": "string", "description": "User password"}
            },
            "required": ["username", "password"]
        }
    },
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "access": {"type": "string", "description": "JWT access token"},
                            "refresh": {"type": "string", "description": "JWT refresh token"}
                        }
                    }
                }
            }
        },
        401: {"description": "Invalid credentials"}
    },
    examples=[
        OpenApiExample(
            "Login example",
            summary="Example login request",
            description="Example of user login with credentials",
            value={
                "username": "user@example.com",
                "password": "your_password"
            }
        )
    ]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with documentation."""
    pass


@extend_schema(
    summary="Refresh JWT token",
    description="Refresh JWT access token using refresh token.",
    tags=["Authentication"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "description": "JWT refresh token"}
            },
            "required": ["refresh"]
        }
    },
    responses={
        200: {
            "description": "Token refresh successful",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "access": {"type": "string", "description": "New JWT access token"}
                        }
                    }
                }
            }
        },
        401: {"description": "Invalid refresh token"}
    },
    examples=[
        OpenApiExample(
            "Refresh example",
            summary="Example refresh request",
            description="Example of token refresh",
            value={
                "refresh": "your_refresh_token_here"
            }
        )
    ]
)
class CustomTokenRefreshView(TokenRefreshView):
    """Custom JWT token refresh view with documentation."""
    pass


@extend_schema(
    summary="Verify JWT token",
    description="Verify if JWT token is valid.",
    tags=["Authentication"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "JWT token to verify"}
            },
            "required": ["token"]
        }
    },
    responses={
        200: {
            "description": "Token is valid",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "token": {"type": "string", "description": "Verified token"}
                        }
                    }
                }
            }
        },
        401: {"description": "Invalid token"}
    },
    examples=[
        OpenApiExample(
            "Verify example",
            summary="Example token verification",
            description="Example of token verification",
            value={
                "token": "your_jwt_token_here"
            }
        )
    ]
)
class CustomTokenVerifyView(TokenVerifyView):
    """Custom JWT token verify view with documentation."""
    pass
