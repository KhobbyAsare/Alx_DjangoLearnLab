# Social Media API Deployment Guide

This document provides comprehensive instructions for deploying the Social Media API to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Options](#deployment-options)
5. [Heroku Deployment (Recommended)](#heroku-deployment-recommended)
6. [Manual Server Deployment](#manual-server-deployment)
7. [Post-Deployment](#post-deployment)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

- Python 3.11+
- Git
- A hosting service account (Heroku, AWS, DigitalOcean, etc.)
- PostgreSQL database (for production)
- Redis instance (optional, for caching)

## Project Structure

```
social_media_api/
├── social_media_api/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Development settings
│   │   └── production.py    # Production settings
│   └── ...
├── accounts/
├── posts/
├── notifications/
├── static/
├── staticfiles/
├── logs/
├── requirements.txt
├── Procfile
├── runtime.txt
├── gunicorn.conf.py
├── deploy.py
└── .env.example
```

## Environment Configuration

### Required Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Core Django Settings
DJANGO_ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-here-50-chars-minimum
DEBUG=False
ALLOWED_HOSTS=.herokuapp.com,yourdomain.com

# Database
DATABASE_URL=postgres://username:password@host:port/database_name

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Cache (Optional)
REDIS_URL=redis://localhost:6379/1
```

### Generate Secret Key

```python
import secrets
print(secrets.token_urlsafe(50))
```

## Deployment Options

### Option 1: Heroku (Recommended for beginners)
- Easy setup and deployment
- Automatic SSL certificates
- Built-in PostgreSQL and Redis add-ons
- Automatic scaling

### Option 2: Manual Server Deployment
- More control over configuration
- Cost-effective for high-traffic applications
- Requires more system administration knowledge

## Heroku Deployment (Recommended)

### Step 1: Install Heroku CLI

Download from [heroku.com/install](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Prepare Your Code

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit"

# Login to Heroku
heroku login
```

### Step 3: Create Heroku App

```bash
# Create a new Heroku app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Add Redis addon (optional)
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set DJANGO_ENVIRONMENT=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")

# View your environment variables
heroku config
```

### Step 4: Deploy

```bash
# Deploy to Heroku
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser (optional)
heroku run python manage.py createsuperuser

# Check logs
heroku logs --tail
```

### Step 5: Access Your App

```bash
heroku open
```

Your API will be available at: `https://your-app-name.herokuapp.com/`

## Manual Server Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Nginx
- PostgreSQL
- Python 3.11+
- Supervisor (for process management)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib supervisor

# Create application user
sudo adduser --system --group social_media_api
sudo mkdir -p /var/log/social_media_api
sudo chown social_media_api:social_media_api /var/log/social_media_api
```

### Step 2: Database Setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE social_media_api;
CREATE USER social_media_api WITH PASSWORD 'your-secure-password';
ALTER ROLE social_media_api SET client_encoding TO 'utf8';
ALTER ROLE social_media_api SET default_transaction_isolation TO 'read committed';
ALTER ROLE social_media_api SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE social_media_api TO social_media_api;
\q
```

### Step 3: Application Deployment

```bash
# Clone repository
sudo -u social_media_api git clone https://github.com/yourusername/social_media_api.git /home/social_media_api/app
cd /home/social_media_api/app

# Create virtual environment
sudo -u social_media_api python3 -m venv /home/social_media_api/venv
sudo -u social_media_api /home/social_media_api/venv/bin/pip install -r requirements.txt

# Set environment variables
sudo -u social_media_api tee /home/social_media_api/.env << EOF
DJANGO_ENVIRONMENT=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DATABASE_URL=postgres://social_media_api:your-secure-password@localhost/social_media_api
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
EOF

# Run migrations and collect static files
sudo -u social_media_api /home/social_media_api/venv/bin/python manage.py migrate
sudo -u social_media_api /home/social_media_api/venv/bin/python manage.py collectstatic --noinput
```

### Step 4: Supervisor Configuration

Create `/etc/supervisor/conf.d/social_media_api.conf`:

```ini
[program:social_media_api]
command=/home/social_media_api/venv/bin/gunicorn --config gunicorn.conf.py social_media_api.wsgi
directory=/home/social_media_api/app
user=social_media_api
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/social_media_api/gunicorn.log
```

### Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/social_media_api`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/social_media_api/app/staticfiles/;
    }
    
    location /media/ {
        alias /home/social_media_api/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/social_media_api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start social_media_api
```

### Step 6: SSL Certificate (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Post-Deployment

### 1. Create Admin User

```bash
# Heroku
heroku run python manage.py createsuperuser

# Manual server
sudo -u social_media_api /home/social_media_api/venv/bin/python manage.py createsuperuser
```

### 2. Test API Endpoints

Test key endpoints:
- `GET /api/accounts/profile/` - User profile
- `GET /api/posts/` - Posts list
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login

### 3. Set Up Monitoring

Configure monitoring for:
- Application errors
- Database performance
- Server resources
- API response times

## Monitoring and Maintenance

### Application Monitoring

1. **Error Tracking**: Use Sentry or similar service
2. **Performance**: Monitor API response times
3. **Database**: Track query performance
4. **Logs**: Centralized logging with ELK stack or similar

### Regular Maintenance

1. **Security Updates**: Keep dependencies updated
2. **Database Maintenance**: Regular backups and optimization
3. **Log Rotation**: Prevent log files from growing too large
4. **SSL Certificates**: Monitor expiration dates

### Backup Strategy

1. **Database Backups**: Daily automated backups
2. **Media Files**: Regular backup of uploaded content
3. **Configuration**: Version control for all config files

### Scaling Considerations

1. **Horizontal Scaling**: Add more app instances
2. **Database Scaling**: Read replicas for heavy read workloads
3. **Caching**: Implement Redis for frequently accessed data
4. **CDN**: Use CloudFront or similar for static files

## Troubleshooting

### Common Issues

#### 1. Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check STATIC_ROOT permissions
ls -la /path/to/staticfiles/
```

#### 2. Database Connection Issues

```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python manage.py dbshell
```

#### 3. Gunicorn Won't Start

```bash
# Check logs
tail -f /var/log/social_media_api/gunicorn.log

# Test gunicorn manually
gunicorn --config gunicorn.conf.py social_media_api.wsgi
```

#### 4. Nginx Configuration Issues

```bash
# Test nginx config
sudo nginx -t

# Check nginx error logs
tail -f /var/log/nginx/error.log
```

### Debug Mode

**NEVER** enable DEBUG in production. For troubleshooting:

1. Check logs first
2. Use Django's logging framework
3. Set up proper error monitoring

### Performance Issues

1. **Database Queries**: Use Django Debug Toolbar locally
2. **Caching**: Implement caching for frequently accessed data
3. **Database Indexes**: Add indexes for commonly queried fields

## Security Checklist

- [ ] DEBUG = False in production
- [ ] Unique SECRET_KEY for each environment
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Database credentials secure
- [ ] Regular security updates
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Logs monitored for suspicious activity

## Support and Updates

### Deployment Updates

```bash
# For Heroku
git push heroku main
heroku run python manage.py migrate

# For manual server
git pull origin main
sudo -u social_media_api /home/social_media_api/venv/bin/python manage.py migrate
sudo -u social_media_api /home/social_media_api/venv/bin/python manage.py collectstatic --noinput
sudo supervisorctl restart social_media_api
```

### Rollback Strategy

Always test in staging before production and have a rollback plan:

1. Database migrations rollback plan
2. Previous version deployment capability
3. Quick rollback procedures documented

---

## API Documentation

Once deployed, your API documentation will be available at:
- Development: `http://localhost:8000/api/`
- Production: `https://your-domain.com/api/`

## Environment URLs

- **Development**: `http://localhost:8000`
- **Staging**: `https://staging.your-domain.com`
- **Production**: `https://your-domain.com`

For additional support or questions about deployment, consult the Django deployment documentation or reach out to the development team.
