"""
Health check endpoint for Lambda
"""
import json
from typing import Any, Dict


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check handler for Lambda

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Health check response
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(
            {
                "status": "healthy",
                "service": "real-state-api",
                "environment": "production",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        ),
    }
