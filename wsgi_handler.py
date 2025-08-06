"""
WSGI handler for serverless deployment
"""
import json
import os
from typing import Dict, Any

from mangum import Mangum
from app.main import app

# Create Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for FastAPI application
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    # Add CORS headers for preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    # Process the request through Mangum
    response = handler(event, context)
    
    # Add CORS headers to all responses
    if 'headers' not in response:
        response['headers'] = {}
    
    response['headers'].update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    })
    
    return response 