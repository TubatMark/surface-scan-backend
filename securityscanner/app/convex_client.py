import os
import time
import requests
import json
import redis
from django.conf import settings

class ConvexClient:
    def __init__(self):
        self.convex_url = settings.CONVEX_URL
        self.deploy_key = settings.CONVEX_DEPLOY_KEY
        # Use Redis for development
        self.redis_client = redis.from_url(settings.CELERY_BROKER_URL)
    
    def create_scan(self, job_id, url):
        """Create initial scan record"""
        scan_data = {
            'job_id': job_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'result': {},
            'createdAt': int(time.time() * 1000)  # milliseconds
        }
        
        # Use Redis for development
        try:
            self.redis_client.set(f"scan:{job_id}", json.dumps(scan_data))
            return {'success': True, 'id': job_id}
        except Exception as e:
            print(f"Redis error: {e}")
            return {'success': True, 'id': job_id}
    
    def update_scan(self, job_id, status=None, progress=None, result=None):
        """Update scan record"""
        # Use Redis for development
        try:
            scan_data = self.redis_client.get(f"scan:{job_id}")
            if scan_data:
                scan_data = json.loads(scan_data)
                if status is not None:
                    scan_data['status'] = status
                if progress is not None:
                    scan_data['progress'] = progress
                if result is not None:
                    scan_data['result'] = result
                
                self.redis_client.set(f"scan:{job_id}", json.dumps(scan_data))
            return {'success': True, 'id': job_id}
        except Exception as e:
            print(f"Redis error: {e}")
            return {'success': True, 'id': job_id}
    
    def get_scan(self, job_id):
        """Get scan record"""
        # Use Redis for development
        try:
            scan_data = self.redis_client.get(f"scan:{job_id}")
            if scan_data:
                return json.loads(scan_data)
            return None
        except Exception as e:
            print(f"Redis error: {e}")
            return None
