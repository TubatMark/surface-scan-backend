<<<<<<< HEAD
# Security Scanner Backend

Django REST API backend for the Surface-Level Website Security Scanner application.

## Overview

This backend provides a RESTful API for performing security scans on websites. It analyzes TLS/SSL certificates, HTTP security headers, DNS configuration, and server fingerprinting to generate a comprehensive security score.

## Features

- **Security Analysis**: TLS/SSL, HTTP headers, DNS, and server fingerprinting
- **Scoring System**: Weighted scoring algorithm (0-100 points) with letter grades
- **Real-time Processing**: Asynchronous task processing with Celery
- **Rate Limiting**: Prevents abuse with configurable rate limits
- **Data Storage**: Redis-based storage for scan results
- **RESTful API**: Clean JSON API endpoints

## Tech Stack

- **Django 4.2.7**: Web framework
- **Django REST Framework**: API framework
- **Celery**: Asynchronous task queue
- **Redis**: Message broker and data storage
- **Python 3.11**: Runtime environment

## API Endpoints

### POST `/api/scan/`
Initiates a security scan for a website.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "Scan initiated successfully"
}
```

### GET `/api/status/{job_id}/`
Retrieves the status and results of a scan.

**Response:**
```json
{
  "job_id": "uuid-string",
  "url": "https://example.com",
  "status": "done",
  "progress": 100,
  "result": {
    "tls": { ... },
    "headers": { ... },
    "dns": { ... },
    "fingerprinting": { ... },
    "score": 85,
    "grade": "B",
    "score_breakdown": { ... }
  },
  "createdAt": 1234567890
}
```

## Security Analysis Modules

### 1. TLS/SSL Analysis
- Certificate validity and expiry
- Protocol version and cipher suite
- Certificate issuer information

### 2. HTTP Headers Analysis
- Security headers detection (HSTS, CSP, X-Frame-Options, etc.)
- Missing security headers identification
- Security recommendations

### 3. DNS Analysis
- A, AAAA, MX, NS, TXT record lookup
- DNSSEC support detection
- DNS security assessment

### 4. Server Fingerprinting
- Web server identification
- Technology stack detection
- Server security assessment

## Scoring System

The security scoring system uses a weighted algorithm:

- **TLS Certificate**: 20 points
- **HSTS Header**: 15 points
- **CSP Header**: 15 points
- **Frame Options**: 10 points
- **DNSSEC**: 10 points
- **HTTPS Redirection**: 10 points
- **Server Fingerprint**: 10 points
- **Bonus Points**: Up to 6 points for additional headers

**Grade Scale:**
- A+: 90-100 points
- A: 80-89 points
- B: 70-79 points
- C: 60-69 points
- D: 50-59 points
- F: 0-49 points

## Development Setup

### Prerequisites
- Python 3.11+
- Redis server
- Docker (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd surface-scan/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CONVEX_URL` | Convex deployment URL | Optional |
| `CONVEX_DEPLOY_KEY` | Convex deploy key | Optional |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per IP | `5` |
| `SCAN_TIMEOUT` | Scan timeout in seconds | `10` |

### CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:3000` (React frontend)
- `http://127.0.0.1:3000`

## Project Structure

```
backend/
├── securityscanner/          # Django project
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py              # URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   └── celery.py            # Celery configuration
├── app/                     # Main application
│   ├── __init__.py
│   ├── views.py             # API views
│   ├── urls.py              # App URLs
│   ├── tasks.py             # Celery tasks
│   ├── serializers.py       # DRF serializers
│   └── convex_client.py     # Data storage client
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

## Testing

### Manual Testing

1. **Start the backend:**
   ```bash
   python manage.py runserver
   ```

2. **Test scan initiation:**
   ```bash
   curl -X POST http://localhost:8000/api/scan/ \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
   ```

3. **Check scan status:**
   ```bash
   curl http://localhost:8000/api/status/{job_id}/
   ```

### Automated Testing

Run the test suite:
```bash
python manage.py test
```

## Deployment

### Production Considerations

1. **Security:**
   - Set `DEBUG = False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Enable HTTPS

2. **Performance:**
   - Use production WSGI server (Gunicorn)
   - Configure Redis for production
   - Set up Celery workers
   - Enable caching

3. **Monitoring:**
   - Set up logging
   - Monitor Celery tasks
   - Track API usage

## Troubleshooting

### Common Issues

1. **Celery Connection Refused:**
   - Ensure Redis is running
   - Check `CELERY_BROKER_URL` configuration

2. **Rate Limit Exceeded:**
   - Wait for rate limit reset (1 minute)
   - Adjust `RATE_LIMIT_PER_MINUTE` setting

3. **Scan Timeout:**
   - Check network connectivity
   - Increase `SCAN_TIMEOUT` if needed

### Logs

View application logs:
```bash
# Docker
docker-compose logs backend
docker-compose logs celery

# Local development
python manage.py runserver --verbosity=2
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
=======
# surface-scan-backend
>>>>>>> origin/main
