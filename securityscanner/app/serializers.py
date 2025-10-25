from rest_framework import serializers

class ScanRequestSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    
    def validate_url(self, value):
        """Validate URL and check for security concerns"""
        import re
        from urllib.parse import urlparse
        
        # Basic URL validation
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        
        parsed = urlparse(value)
        
        # Reject IP addresses
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, parsed.hostname):
            raise serializers.ValidationError("IP addresses are not allowed")
        
        # Reject localhost and private IPs
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            raise serializers.ValidationError("Localhost addresses are not allowed")
        
        # Check for private IP ranges
        if parsed.hostname:
            try:
                import ipaddress
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private:
                    raise serializers.ValidationError("Private IP addresses are not allowed")
            except (ValueError, ipaddress.AddressValueError):
                # Not an IP address, continue
                pass
        
        return value

class ScanResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
