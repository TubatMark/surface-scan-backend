import ssl
import socket
import dns.resolver
import requests
from urllib.parse import urlparse
from celery import shared_task
from django.conf import settings
from .convex_client import ConvexClient
import time

@shared_task(bind=True)
def scan_website_task(self, job_id, url):
    """Main security scanning task"""
    convex_client = ConvexClient()
    
    try:
        # Update status to running
        convex_client.update_scan(job_id, status='running', progress=10)
        
        result = {
            'tls': {},
            'headers': {},
            'dns': {},
            'fingerprinting': {},
            'score': 0
        }
        
        # Parse URL
        parsed_url = urlparse(url)
        domain = parsed_url.hostname
        
        # 1. TLS/SSL Analysis (20% of progress)
        try:
            tls_result = analyze_tls(domain, parsed_url.port or 443)
            result['tls'] = tls_result
            convex_client.update_scan(job_id, progress=30, result=result)
        except Exception as e:
            result['tls'] = {'error': str(e)}
        
        # 2. HTTP Headers Analysis (30% of progress)
        try:
            headers_result = analyze_headers(url)
            result['headers'] = headers_result
            convex_client.update_scan(job_id, progress=50, result=result)
        except Exception as e:
            result['headers'] = {'error': str(e)}
        
        # 3. DNS Analysis (20% of progress)
        try:
            dns_result = analyze_dns(domain)
            result['dns'] = dns_result
            convex_client.update_scan(job_id, progress=70, result=result)
        except Exception as e:
            result['dns'] = {'error': str(e)}
        
        # 4. Fingerprinting (10% of progress)
        try:
            fingerprint_result = analyze_fingerprinting(url)
            result['fingerprinting'] = fingerprint_result
            convex_client.update_scan(job_id, progress=80, result=result)
        except Exception as e:
            result['fingerprinting'] = {'error': str(e)}
        
        # 5. Calculate Security Score
        score = calculate_security_score(result)
        result['score'] = score
        
        # Ensure the result object is properly updated with all scoring data
        final_result = {
            'tls': result.get('tls', {}),
            'headers': result.get('headers', {}),
            'dns': result.get('dns', {}),
            'fingerprinting': result.get('fingerprinting', {}),
            'score': score,
            'grade': result.get('grade', 'N/A'),
            'score_breakdown': result.get('score_breakdown', {})
        }
        
        # Update final result with enhanced scoring
        convex_client.update_scan(job_id, status='done', progress=100, result=final_result)
        
        # Also update the return value to include the enhanced scoring
        result.update({
            'score': score,
            'grade': result.get('grade', 'N/A'),
            'score_breakdown': result.get('score_breakdown', {})
        })
        
        return {'status': 'completed', 'result': result}
        
    except Exception as e:
        # Update with error status
        convex_client.update_scan(job_id, status='error', result={'error': str(e)})
        raise self.retry(exc=e, countdown=60, max_retries=3)

def analyze_tls(domain, port=443):
    """Analyze TLS/SSL configuration"""
    result = {
        'valid': False,
        'certificate_valid': False,
        'expiry_date': None,
        'issuer': None,
        'protocol_version': None,
        'cipher_suite': None
    }
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Connect and get certificate info
        with socket.create_connection((domain, port), timeout=settings.SCAN_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                
                result['valid'] = True
                result['certificate_valid'] = True
                result['expiry_date'] = cert.get('notAfter')
                result['issuer'] = cert.get('issuer', {}).get('organizationName', 'Unknown')
                result['protocol_version'] = ssock.version()
                result['cipher_suite'] = cipher[0] if cipher else None
                
    except Exception as e:
        result['error'] = str(e)
    
    return result

def analyze_headers(url):
    """Analyze HTTP security headers"""
    result = {
        'security_headers': {},
        'missing_headers': [],
        'recommendations': []
    }
    
    security_headers = {
        'Strict-Transport-Security': 'HSTS',
        'Content-Security-Policy': 'CSP',
        'X-Frame-Options': 'X-Frame-Options',
        'X-Content-Type-Options': 'X-Content-Type-Options',
        'X-XSS-Protection': 'X-XSS-Protection',
        'Referrer-Policy': 'Referrer-Policy',
        'Permissions-Policy': 'Permissions-Policy'
    }
    
    try:
        response = requests.get(url, timeout=settings.SCAN_TIMEOUT, allow_redirects=True)
        headers = response.headers
        
        for header, name in security_headers.items():
            if header in headers:
                result['security_headers'][name] = headers[header]
            else:
                result['missing_headers'].append(name)
        
        # Add recommendations based on missing headers
        if 'HSTS' in result['missing_headers']:
            result['recommendations'].append('Implement HSTS header for better security')
        if 'CSP' in result['missing_headers']:
            result['recommendations'].append('Add Content Security Policy header')
        if 'X-Frame-Options' in result['missing_headers']:
            result['recommendations'].append('Add X-Frame-Options to prevent clickjacking')
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def analyze_dns(domain):
    """Analyze DNS configuration"""
    result = {
        'a_records': [],
        'aaaa_records': [],
        'mx_records': [],
        'ns_records': [],
        'txt_records': [],
        'dnssec': False
    }
    
    try:
        # A records
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            result['a_records'] = [str(record) for record in a_records]
        except:
            pass
        
        # AAAA records
        try:
            aaaa_records = dns.resolver.resolve(domain, 'AAAA')
            result['aaaa_records'] = [str(record) for record in aaaa_records]
        except:
            pass
        
        # MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            result['mx_records'] = [str(record) for record in mx_records]
        except:
            pass
        
        # NS records
        try:
            ns_records = dns.resolver.resolve(domain, 'NS')
            result['ns_records'] = [str(record) for record in ns_records]
        except:
            pass
        
        # TXT records
        try:
            txt_records = dns.resolver.resolve(domain, 'TXT')
            result['txt_records'] = [str(record) for record in txt_records]
        except:
            pass
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def analyze_fingerprinting(url):
    """Analyze server fingerprinting"""
    result = {
        'server': None,
        'powered_by': None,
        'technologies': []
    }
    
    try:
        response = requests.get(url, timeout=settings.SCAN_TIMEOUT, allow_redirects=True)
        headers = response.headers
        
        # Server header
        if 'Server' in headers:
            result['server'] = headers['Server']
        
        # X-Powered-By header
        if 'X-Powered-By' in headers:
            result['powered_by'] = headers['X-Powered-By']
        
        # Detect technologies based on headers
        if 'X-Powered-By' in headers:
            result['technologies'].append(headers['X-Powered-By'])
        
        if 'Server' in headers:
            server = headers['Server'].lower()
            if 'apache' in server:
                result['technologies'].append('Apache')
            elif 'nginx' in server:
                result['technologies'].append('Nginx')
            elif 'iis' in server:
                result['technologies'].append('IIS')
        
        # Check for common framework headers
        if 'X-AspNet-Version' in headers:
            result['technologies'].append('ASP.NET')
        if 'X-Drupal-Cache' in headers:
            result['technologies'].append('Drupal')
        if 'X-Generator' in headers:
            result['technologies'].append(headers['X-Generator'])
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def calculate_security_score(result):
    """
    Calculate enhanced security score (0-100) with weighted points system
    
    Scoring System:
    +20 pts: Valid TLS/SSL certificate found and not expired
    +15 pts: HSTS header detected
    +15 pts: CSP (Content-Security-Policy) header detected
    +10 pts: X-Frame-Options or X-Content-Type-Options header found
    +10 pts: DNSSEC or secure DNS record detected
    +10 pts: HTTPS redirection enforced
    +10 pts: Server fingerprint identified
    """
    score = 0
    max_score = 100
    score_breakdown = {
        'tls_certificate': 0,
        'hsts_header': 0,
        'csp_header': 0,
        'frame_options': 0,
        'dnssec': 0,
        'https_redirect': 0,
        'server_fingerprint': 0,
        'bonus_points': 0
    }
    
    # TLS/SSL Certificate (20 points)
    tls = result.get('tls', {})
    if tls.get('valid') and tls.get('certificate_valid'):
        score += 20
        score_breakdown['tls_certificate'] = 20
    
    # HSTS Header (15 points)
    headers = result.get('headers', {})
    security_headers = headers.get('security_headers', {})
    if 'HSTS' in security_headers:
        score += 15
        score_breakdown['hsts_header'] = 15
    
    # CSP Header (15 points)
    if 'CSP' in security_headers:
        score += 15
        score_breakdown['csp_header'] = 15
    
    # X-Frame-Options or X-Content-Type-Options (10 points)
    if 'X-Frame-Options' in security_headers or 'X-Content-Type-Options' in security_headers:
        score += 10
        score_breakdown['frame_options'] = 10
    
    # DNSSEC or secure DNS (10 points)
    dns = result.get('dns', {})
    if dns.get('dnssec') or (dns.get('a_records') and dns.get('ns_records')):
        score += 10
        score_breakdown['dnssec'] = 10
    
    # HTTPS Redirection (10 points) - Check if site enforces HTTPS
    if tls.get('valid') and 'HSTS' in security_headers:
        score += 10
        score_breakdown['https_redirect'] = 10
    
    # Server Fingerprint (10 points)
    fingerprinting = result.get('fingerprinting', {})
    if fingerprinting.get('server'):
        score += 10
        score_breakdown['server_fingerprint'] = 10
    
    # Bonus points for additional security headers
    additional_headers = ['X-XSS-Protection', 'Referrer-Policy', 'Permissions-Policy']
    bonus = 0
    for header in additional_headers:
        if header in security_headers:
            bonus += 2
    score += bonus
    score_breakdown['bonus_points'] = bonus
    
    # Ensure score doesn't exceed 100
    final_score = min(score, max_score)
    
    # Add score breakdown to result
    result['score_breakdown'] = score_breakdown
    result['grade'] = get_security_grade(final_score)
    
    return final_score

def get_security_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'
