"""
WSGI config for ELD project - Production-ready
"""

import os
import sys
from pathlib import Path

# Add project to path
project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from django.core.wsgi import get_wsgi_application
from django.conf import settings

# Initialize Django
application = get_wsgi_application()

# Production middleware for serverless
class ServerlessMiddleware:
    """Middleware for Vercel serverless environment"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Set headers for serverless
        def custom_start_response(status, response_headers, exc_info=None):
            response_headers = [
                (name, value) for name, value in response_headers
                if name.lower() not in ['content-length', 'server']
            ]
            response_headers.append(('X-Powered-By', 'ELD-Simulator'))
            return start_response(status, response_headers, exc_info)
        
        return self.app(environ, custom_start_response)

# Wrap application with serverless middleware
application = ServerlessMiddleware(application)
