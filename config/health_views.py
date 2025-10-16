"""
Health check views for monitoring API and documentation status.
"""
from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="API Health Check",
    description="Check if the API is running and accessible.",
    tags=["Health"],
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "healthy"},
                            "message": {"type": "string", "example": "API is running"},
                            "version": {"type": "string", "example": "1.0.0"}
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for API monitoring."""
    return Response({
        "status": "healthy",
        "message": "Mera API is running",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/api/docs/",
            "redoc": "/api/redoc/",
            "schema": "/api/schema/"
        }
    })


@extend_schema(
    summary="Documentation Health Check",
    description="Check if API documentation is accessible.",
    tags=["Health"],
    responses={
        200: {
            "description": "Documentation is accessible",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "healthy"},
                            "message": {"type": "string", "example": "Documentation is accessible"},
                            "endpoints": {
                                "type": "object",
                                "properties": {
                                    "swagger_ui": {"type": "string", "example": "/api/docs/"},
                                    "redoc": {"type": "string", "example": "/api/redoc/"},
                                    "schema": {"type": "string", "example": "/api/schema/"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def docs_health_check(request):
    """Health check endpoint for documentation."""
    return Response({
        "status": "healthy",
        "message": "API documentation is accessible",
        "endpoints": {
            "swagger_ui": "/api/docs/",
            "redoc": "/api/redoc/",
            "schema": "/api/schema/"
        },
        "features": [
            "Interactive API documentation",
            "JWT authentication examples",
            "Request/response schemas",
            "Error handling documentation"
        ]
    })
