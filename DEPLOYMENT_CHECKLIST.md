# 🚀 Render Deployment Checklist

## Pre-Deployment Steps
- [ ] All new files committed to Git repository
- [ ] Repository pushed to GitHub/GitLab/Bitbucket
- [ ] Django secret key generated (don't use the default!)
- [ ] Frontend URLs known for CORS configuration

## Render Setup Steps
- [ ] Created Render account
- [ ] Created PostgreSQL database on Render
- [ ] Copied internal database URL
- [ ] Created web service connected to your repository

## Configuration Steps
- [ ] Set Root Directory to `backend`
- [ ] Set Build Command to `./build.sh`
- [ ] Set Start Command to `gunicorn main.wsgi:application`
- [ ] Added all required environment variables:
  - [ ] SECRET_KEY
  - [ ] DEBUG=False
  - [ ] DATABASE_URL
  - [ ] ALLOWED_HOSTS

## Post-Deployment Steps
- [ ] Test health endpoint: `https://your-app.onrender.com/api/health/`
- [ ] Test admin panel: `https://your-app.onrender.com/admin/`
- [ ] Test API docs: `https://your-app.onrender.com/api/docs/`
- [ ] Update frontend API URL
- [ ] Test frontend-backend connection

## Environment Variables Reference

### Required
```
SECRET_KEY=your-generated-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
ALLOWED_HOSTS=your-app.onrender.com
```

### Optional
```
FRONTEND_URL=https://your-frontend.vercel.app
LOAD_SAMPLE_DATA=true
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Quick Commands

Generate Django Secret Key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Test locally with production settings:
```bash
export DEBUG=False
export DATABASE_URL=sqlite:///db.sqlite3
python manage.py runserver
```