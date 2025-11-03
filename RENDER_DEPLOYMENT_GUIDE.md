# 🚀 Django Backend Deployment Guide for Render

## Prerequisites
- A Render account (sign up at https://render.com)
- Your Django project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step-by-Step Deployment Process

### 1. Prepare Your Repository
First, make sure all the new files are committed to your Git repository:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a Web Service on Render

1. **Login to Render Dashboard**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect Your Repository**
   - Choose "Build and deploy from a Git repository"
   - Connect your GitHub/GitLab/Bitbucket account
   - Select your GoBarberly repository

3. **Configure the Service**
   - **Name**: `gobarberly-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend` (since your Django app is in the backend folder)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn main.wsgi:application`

### 3. Add PostgreSQL Database

1. **Create Database**
   - In Render Dashboard, click "New +" → "PostgreSQL"
   - **Name**: `gobarberly-db`
   - **Database**: `gobarberly`
   - **User**: `gobarberly`
   - **Region**: Same as your web service
   - **Plan**: Start with Free tier

2. **Get Database URL**
   - After creation, copy the "Internal Database URL"
   - It looks like: `postgresql://user:password@hostname:port/database`

### 4. Environment Variables

In your web service settings, add these environment variables:

**Required Variables:**
```
SECRET_KEY=django-insecure-generate-a-new-secret-key-here-make-it-long-and-random
DEBUG=False
DATABASE_URL=postgresql://your-db-internal-url-from-step-3
ALLOWED_HOSTS=your-app-name.onrender.com
```

**Optional Variables (for email functionality):**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@gobarberly.com
FRONTEND_URL=https://your-frontend-url.com
```

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically start building and deploying
3. Monitor the build logs for any errors
4. Once deployed, your API will be available at: `https://your-app-name.onrender.com`

### 6. Test Your Deployment

Test these endpoints:
- `https://your-app-name.onrender.com/api/auth/health/` - Health check
- `https://your-app-name.onrender.com/api/docs/` - API documentation
- `https://your-app-name.onrender.com/admin/` - Django admin

### 7. Update Frontend Configuration

Update your frontend API base URL to point to your new Render deployment:

In your frontend `.env` file:
```
VITE_API_BASE_URL=https://your-app-name.onrender.com
```

## Common Issues and Solutions

### Build Failures

**Problem**: Build fails with package installation errors
**Solution**: Check that all dependencies are in requirements.txt

**Problem**: Database connection errors during build
**Solution**: Ensure DATABASE_URL is correctly set in environment variables

### Runtime Issues

**Problem**: 500 Internal Server Error
**Solution**: Check logs in Render dashboard, often related to missing environment variables

**Problem**: CORS errors from frontend
**Solution**: Add your frontend URL to CORS_ALLOWED_ORIGINS or set FRONTEND_URL environment variable

### Performance Optimization

1. **Static Files**: Whitenoise is configured to serve static files efficiently
2. **Database**: Consider upgrading to a paid database plan for production
3. **Caching**: Add Redis for caching if needed

## Security Checklist

- ✅ DEBUG=False in production
- ✅ Unique SECRET_KEY (never use the default)
- ✅ ALLOWED_HOSTS properly configured
- ✅ Database credentials secure
- ✅ CORS properly configured

## Monitoring and Maintenance

1. **Logs**: Check Render dashboard for application logs
2. **Database**: Monitor database usage in PostgreSQL dashboard
3. **Updates**: Use Git to deploy updates (automatic deployments on push)

## Free Tier Limitations

Render's free tier includes:
- Web service spins down after 15 minutes of inactivity
- Database limited to 1GB
- 750 hours per month

Consider upgrading for production use.

## Next Steps

1. Deploy your backend following this guide
2. Update frontend API configuration
3. Test all functionality
4. Set up monitoring and alerts
5. Consider custom domain setup

Your Django backend will be live at: `https://your-app-name.onrender.com` 🎉