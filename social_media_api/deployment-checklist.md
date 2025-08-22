# Production Deployment Checklist

Use this checklist to ensure all steps are completed before deploying to production.

## Pre-Deployment Checklist

### Code Preparation
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] No DEBUG statements or test data
- [ ] SECRET_KEY properly configured
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Database settings configured for production
- [ ] Static files configuration verified
- [ ] All migrations created and tested

### Security Review
- [ ] DEBUG = False in production settings
- [ ] Secure SECRET_KEY generated and stored safely
- [ ] HTTPS/SSL configured
- [ ] Security headers enabled
- [ ] Database credentials secure
- [ ] No sensitive data in version control
- [ ] Input validation implemented
- [ ] CORS settings configured if needed

### Infrastructure
- [ ] Production server/hosting service ready
- [ ] Database server configured
- [ ] Domain name configured (if applicable)
- [ ] SSL certificate obtained
- [ ] Backup strategy implemented
- [ ] Monitoring tools configured

## Deployment Steps

### 1. Environment Setup
- [ ] Environment variables configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database created
- [ ] Static files directories created
- [ ] Log directories created with proper permissions

### 2. Database Migration
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Initial data loaded (if any)
- [ ] Database backup taken

### 3. Static Files
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Static files served correctly
- [ ] Media upload directories configured

### 4. Web Server Configuration
- [ ] Gunicorn configured and tested
- [ ] Nginx/reverse proxy configured
- [ ] SSL/HTTPS enabled
- [ ] Firewall rules configured

### 5. Application Testing
- [ ] Application starts without errors
- [ ] Admin interface accessible
- [ ] API endpoints responding correctly
- [ ] Authentication working
- [ ] Database operations working
- [ ] File uploads working (if applicable)

## Post-Deployment Checklist

### Immediate Verification
- [ ] Application accessible via domain/URL
- [ ] All API endpoints responding
- [ ] Admin interface working
- [ ] User registration/login working
- [ ] Database operations working
- [ ] Email functionality working (if configured)
- [ ] Error pages configured

### Performance and Monitoring
- [ ] Application performance acceptable
- [ ] Database queries optimized
- [ ] Logging configured and working
- [ ] Error monitoring set up
- [ ] Backup procedures tested
- [ ] SSL certificate validity verified

### Documentation
- [ ] Deployment documentation updated
- [ ] API documentation accessible
- [ ] Admin credentials documented securely
- [ ] Maintenance procedures documented
- [ ] Team notified of deployment

## Environment Variables Required

```bash
# Core Settings
DJANGO_ENVIRONMENT=production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database
DATABASE_URL=postgres://user:pass@host:port/db

# Optional
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=password
REDIS_URL=redis://localhost:6379/1
```

## Common Deployment Commands

### Heroku
```bash
heroku create app-name
heroku addons:create heroku-postgresql:mini
heroku config:set DJANGO_ENVIRONMENT=production
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Manual Server
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
gunicorn --config gunicorn.conf.py social_media_api.wsgi
```

## Emergency Procedures

### Rollback Steps
1. Deploy previous version
2. Rollback database migrations if needed
3. Clear cache if applicable
4. Verify application functionality

### Quick Fixes
- Check application logs first
- Verify environment variables
- Test database connectivity
- Check static file serving
- Verify external service connectivity

## Support Contacts

- **Development Team**: dev-team@company.com
- **DevOps/Infrastructure**: devops@company.com  
- **Emergency Contact**: emergency@company.com

---

**Note**: Always test deployment procedures in a staging environment first!
