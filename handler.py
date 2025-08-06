"""
AWS Lambda handler for serverless deployment.

This module provides the entry point for AWS Lambda functions
when deploying the FastAPI application using Serverless Framework.
"""

import json
import logging
from typing import Any, Dict

from mangum import Adapter

from app.main import app

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Mangum adapter for FastAPI
adapter = Adapter(app)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    This function is the entry point for AWS Lambda and handles
    HTTP requests through the Mangum adapter.
    
    Args:
        event: AWS Lambda event containing HTTP request data
        context: AWS Lambda context object
        
    Returns:
        Dict containing HTTP response data
    """
    try:
        logger.info(f"Processing request: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', 'UNKNOWN')}")
        
        # Use Mangum to handle the request
        response = adapter(event, context)
        
        logger.info(f"Request processed successfully: {response.get('statusCode', 'UNKNOWN')}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        # Return error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }),
        } 