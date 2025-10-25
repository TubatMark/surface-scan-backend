from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomCorsMiddleware(MiddlewareMixin):
    """
    Custom CORS middleware to handle preflight requests and CORS headers
    """
    
    def process_request(self, request):
        """Handle preflight OPTIONS requests"""
        if request.method == 'OPTIONS':
            # Handle preflight request
            origin = request.META.get('HTTP_ORIGIN', '')
            
            # Check if origin is allowed
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            allow_all_origins = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
            
            if allow_all_origins or origin in allowed_origins:
                response = JsonResponse({'status': 'ok'})
                self._add_cors_headers(response, origin)
                return response
            else:
                return JsonResponse({'error': 'CORS not allowed'}, status=403)
        
        return None
    
    def process_response(self, request, response):
        """Add CORS headers to all responses"""
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Check if origin is allowed
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        allow_all_origins = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        
        if allow_all_origins or origin in allowed_origins:
            self._add_cors_headers(response, origin)
        
        return response
    
    def _add_cors_headers(self, response, origin):
        """Add CORS headers to response"""
        # Set Access-Control-Allow-Origin
        if getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
            response['Access-Control-Allow-Origin'] = '*'
        else:
            response['Access-Control-Allow-Origin'] = origin
        
        # Set other CORS headers
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        
        # Expose headers
        response['Access-Control-Expose-Headers'] = 'Content-Type, X-Requested-With'
        
        # Log CORS request for debugging
        if getattr(settings, 'CORS_DEBUG', False):
            logger.info(f"CORS request from origin: {origin}")
