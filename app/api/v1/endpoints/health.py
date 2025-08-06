"""
Health check endpoint for serverless deployment
"""
import json
from datetime import datetime
from typing import Dict, Any


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check handler for AWS Lambda
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Health check response
    """
    try:
        # Basic health check
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "real-state-search-api",
            "environment": "serverless",
            "region": "us-east-2"
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "GET,OPTIONS"
            },
            "body": json.dumps(health_status)
        }
        
    except Exception as e:
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
            "service": "real-state-search-api"
        }
        
        return {
            "statusCode": 503,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "GET,OPTIONS"
            },
            "body": json.dumps(error_response)
        } 