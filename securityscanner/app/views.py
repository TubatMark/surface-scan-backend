import uuid
import redis
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ScanRequestSerializer, ScanResponseSerializer
from .tasks import scan_website_task
from .convex_client import ConvexClient

# Redis connection for rate limiting
redis_client = redis.from_url(settings.CELERY_BROKER_URL)

@api_view(['POST'])
def scan_view(request):
    """Initiate a security scan for a website"""
    serializer = ScanRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    url = serializer.validated_data['url']
    
    # Rate limiting check
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    rate_limit_key = f"rate_limit:{client_ip}"
    
    try:
        current_requests = redis_client.get(rate_limit_key)
        if current_requests and int(current_requests) >= settings.RATE_LIMIT_PER_MINUTE:
            return Response(
                {'error': 'Rate limit exceeded. Maximum 5 scans per minute.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
    except Exception:
        # If Redis is down, continue without rate limiting
        pass
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Initialize scan in Convex
        convex_client = ConvexClient()
        convex_client.create_scan(job_id, url)
        
        # Start Celery task
        scan_website_task.delay(job_id, url)
        
        # Update rate limit counter
        try:
            redis_client.incr(rate_limit_key)
            redis_client.expire(rate_limit_key, 60)  # 1 minute
        except Exception:
            pass
        
        response_serializer = ScanResponseSerializer({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Scan initiated successfully'
        })
        
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to initiate scan: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def status_view(request, job_id):
    """Get the status of a scan job"""
    try:
        convex_client = ConvexClient()
        scan_data = convex_client.get_scan(job_id)
        
        if not scan_data:
            return Response(
                {'error': 'Scan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(scan_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get scan status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'OPTIONS'])
def cors_test(request):
    """Test endpoint for CORS debugging"""
    if request.method == 'OPTIONS':
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
    
    return Response({
        'status': 'ok',
        'message': 'CORS is working',
        'origin': request.META.get('HTTP_ORIGIN', 'unknown'),
        'method': request.method
    })
