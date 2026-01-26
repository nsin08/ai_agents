# Web Agent Chat Interface - Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2026-01-11  
**Target Environment**: Production (Linux/Docker)

---

## Quick Start (Development)

### Prerequisites
- **Python**: 3.11+ (backend)
- **Node.js**: 16+ (frontend)
- **npm**: 8+

### Local Development Setup

**1. Backend Setup**
```bash
cd web/backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend server (default: http://localhost:8000)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend Setup**
```bash
cd web/frontend

# Install dependencies
npm install

# Start development server (default: http://localhost:3000)
npm start
```

**3. Verify Setup**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs (Swagger UI)
- Health Check: http://localhost:8000/health

---

## Production Deployment

### Architecture Overview

```
┌─────────────┐
│   Nginx     │  (Reverse Proxy, SSL Termination)
│  :80, :443  │
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
  ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
  │ Backend │   │ Backend │   │ Backend │  (FastAPI, Uvicorn)
  │  :8001  │   │  :8002  │   │  :8003  │
  └─────────┘   └─────────┘   └─────────┘
       │              │              │
       └──────────────┴──────────────┘
                      │
              ┌───────▼────────┐
              │   Frontend     │  (React, Static Files)
              │  (via Nginx)   │
              └────────────────┘
```

### Option 1: Docker Compose (Recommended)

**File**: `web/docker-compose.yml`

```yaml
version: '3.8'

services:
  # Backend Service (3 replicas for HA)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://ollama:11434}
      - CORS_ORIGINS=https://yourdomain.com
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/build:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - app-network

  # Ollama (Optional - for local LLM inference)
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  ollama-data:
```

**Backend Dockerfile** (`web/backend/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Build** (before deploying):

```bash
cd web/frontend
npm run build
# Output: build/ directory with static files
```

**Nginx Configuration** (`web/nginx/nginx.conf`):

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Upstream backend servers (load balancing)
    upstream backend {
        least_conn;
        server backend:8000 max_fails=3 fail_timeout=30s;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Frontend (React static files)
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            expires 1h;
            add_header Cache-Control "public, must-revalidate, proxy-revalidate";
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            # WebSocket support (if needed)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Health Check (no auth required)
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
}
```

**Deploy Steps**:

```bash
# 1. Set environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
# ... other API keys

# 2. Build frontend
cd web/frontend
npm run build

# 3. Start services
cd web
docker-compose up -d

# 4. Check status
docker-compose ps
docker-compose logs -f backend

# 5. Verify deployment
curl https://yourdomain.com/health
```

---

### Option 2: Manual Deployment (VPS/Cloud)

**Backend Deployment** (Systemd service):

1. **Install Dependencies**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx certbot python3-certbot-nginx
```

2. **Setup Application**:
```bash
# Create app directory
sudo mkdir -p /opt/web-agent
cd /opt/web-agent

# Clone or copy code
# ... (copy backend files)

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Create Systemd Service** (`/etc/systemd/system/web-agent-backend.service`):
```ini
[Unit]
Description=Web Agent Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/web-agent/backend
Environment="PATH=/opt/web-agent/venv/bin"
Environment="OPENAI_API_KEY=sk-..."
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/web-agent/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Start Service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable web-agent-backend
sudo systemctl start web-agent-backend
sudo systemctl status web-agent-backend
```

5. **Frontend Deployment**:
```bash
# Build frontend
cd web/frontend
npm run build

# Copy to nginx root
sudo cp -r build/* /var/www/html/
```

6. **Configure Nginx** (see `nginx.conf` above, place in `/etc/nginx/sites-available/web-agent`):
```bash
sudo ln -s /etc/nginx/sites-available/web-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

7. **SSL Certificate** (Let's Encrypt):
```bash
sudo certbot --nginx -d yourdomain.com
sudo certbot renew --dry-run
```

---

## Environment Variables

### Required (Backend)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` | If using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` | If using Anthropic |
| `GOOGLE_API_KEY` | Google AI API key | `AIza...` | If using Google |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | `...` | If using Azure |
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint | `https://....openai.azure.com/` | If using Azure |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | If using Ollama |

### Optional (Backend)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` | `["https://yourdomain.com"]` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_TURNS` | Default max agent turns | `3` | `5` |
| `TIMEOUT_SECONDS` | Default timeout | `30` | `60` |

### Frontend (Build-time)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://api.yourdomain.com` |

**Set in** `.env.production` before `npm run build`:
```bash
REACT_APP_API_URL=https://api.yourdomain.com
```

---

## Monitoring & Logging

### Health Checks

- **Endpoint**: `/health`
- **Expected Response**: `{"status": "healthy"}`
- **Monitoring Frequency**: Every 30 seconds

### Logging

**Backend Logs** (Docker):
```bash
docker-compose logs -f backend
```

**Backend Logs** (Systemd):
```bash
sudo journalctl -u web-agent-backend -f
```

**Nginx Access Logs**:
```bash
tail -f /var/log/nginx/access.log
```

**Nginx Error Logs**:
```bash
tail -f /var/log/nginx/error.log
```

### Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| Response Time (p95) | <2s | Scale backend if >2s |
| Error Rate | <1% | Investigate logs |
| CPU Usage | <70% | Scale horizontally |
| Memory Usage | <80% | Optimize or scale |
| API Rate Limits | <90% | Implement caching |

---

## Scaling Considerations

### Horizontal Scaling (Multiple Backend Instances)

**Docker Compose**:
```yaml
backend:
  # ...
  deploy:
    replicas: 5  # Increase from 3 to 5
```

**Manual**:
- Run multiple Uvicorn workers: `--workers 8`
- Deploy multiple instances behind load balancer (nginx)

### Caching Strategy

**Redis for Session Data** (future enhancement):
```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

**Backend Integration**:
```python
# In memory → Redis migration
import redis
cache = redis.Redis(host='redis', port=6379, db=0)
```

---

## Security Best Practices

### API Keys
- ✅ **Never commit API keys** to version control
- ✅ Use environment variables or secrets management (AWS Secrets Manager, HashiCorp Vault)
- ✅ Rotate keys quarterly

### HTTPS
- ✅ Always use HTTPS in production (TLS 1.2+)
- ✅ Use strong ciphers (no MD5, no SSLv3)
- ✅ Enable HSTS headers

### CORS
- ✅ Restrict origins to known domains
- ✅ Avoid wildcard (`*`) in production

### Rate Limiting (TODO)
- Consider implementing per-IP rate limits (nginx limit_req_zone)

---

## Troubleshooting

### Backend won't start
**Symptoms**: `uvicorn: command not found`  
**Solution**: Activate virtual environment first
```bash
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows
```

### API returns 502 Bad Gateway
**Symptoms**: Nginx can't reach backend  
**Solution**: Check backend is running
```bash
curl http://localhost:8000/health
docker-compose ps backend
```

### CORS errors in browser
**Symptoms**: `blocked by CORS policy`  
**Solution**: Update `CORS_ORIGINS` environment variable
```python
# In main.py
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
```

### High latency (>5s responses)
**Symptoms**: Slow API responses  
**Solution**: Check provider API keys and network latency
```bash
# Test provider directly
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Out of memory
**Symptoms**: Backend crashes, OOM errors  
**Solution**: Increase container memory limits
```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G  # Increase from default
```

---

## Rollback Procedure

**Docker Compose**:
```bash
# Rollback to previous version
docker-compose down
git checkout <previous-tag>
docker-compose up -d
```

**Manual**:
```bash
sudo systemctl stop web-agent-backend
cd /opt/web-agent
git checkout <previous-tag>
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start web-agent-backend
```

---

## Maintenance

### Regular Tasks

| Task | Frequency | Command |
|------|-----------|---------|
| Update dependencies | Monthly | `pip install --upgrade -r requirements.txt` |
| Review logs | Weekly | `docker-compose logs --tail=1000 backend` |
| Check disk space | Weekly | `df -h` |
| Renew SSL certs | Automatic | `certbot renew` (cron) |
| Backup config | Weekly | `tar -czf config-backup.tar.gz .env docker-compose.yml` |

---

## Support & Contact

**Documentation**: See `web/README.md` and `.context/tasks-57-*/` for detailed guides  
**Issues**: Create issue in GitHub repository  
**Logs**: Always include backend logs and error messages in bug reports

---

**Last Updated**: 2026-01-11  
**Version**: 1.0.0  
**Maintainer**: Development Team
