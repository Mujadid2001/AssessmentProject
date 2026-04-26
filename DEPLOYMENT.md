# ELD Simulator Deployment Guide - Vercel + Neon

## Architecture Overview
- **Frontend**: React + Vite deployed on Vercel
- **Backend**: Django REST API deployed on Vercel Serverless  
- **Database**: PostgreSQL (Neon.tech)
- **Domain**: Single unified domain (e.g., eld-simulator.vercel.app)

## Pre-Deployment Checklist

### 1. Environment Variables Setup
Create these environment variables in Vercel dashboard (Settings → Environment Variables):

**Backend Variables:**
- `DEBUG=False`
- `SECRET_KEY=[Generate a strong random key]`
- `ALLOWED_HOSTS=*.vercel.app`
- `DATABASE_URL=[Your Neon.tech PostgreSQL URL]`
- `CORS_ALLOWED_ORIGINS=https://your-domain.vercel.app`

**Frontend Variables:**
- `REACT_APP_API_URL=https://your-domain.vercel.app/api`

### 2. Neon.tech Setup
1. Go to https://console.neon.tech
2. Create a new project and database
3. Copy the connection string (format: postgresql://user:password@host/dbname?sslmode=require)
4. Add to DATABASE_URL in Vercel

### 3. Generate SECRET_KEY
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Deployment Steps

### Step 1: Connect GitHub Repository
1. Push code to GitHub
2. Go to Vercel.com
3. Import project from GitHub
4. Select repository

### Step 2: Configure Vercel Project
1. Choose framework: "Other"
2. Set build command: `npm run build`
3. Set output directory: `frontend/dist`
4. Add environment variables (see Pre-Deployment Checklist)

### Step 3: Configure Database
1. Run migrations on Neon:
   ```bash
   DATABASE_URL="your-neon-url" python manage.py migrate
   ```

### Step 4: Deploy
1. Push to main branch
2. Vercel auto-deploys
3. Monitor deployment at Vercel dashboard

## Verification

### Test Backend API
```bash
curl https://your-domain.vercel.app/api/drivers/
```

### Test Frontend
```bash
https://your-domain.vercel.app
```

### Test HOS Engine
Use the frontend trip form to generate logs and verify they appear correctly.

## Troubleshooting

### "CORS Error"
- Check CORS_ALLOWED_ORIGINS includes your Vercel domain
- Rebuild and redeploy

### "Database Connection Failed"
- Verify DATABASE_URL is correct
- Check Neon.tech status
- Run migrations if needed

### "Static Files Not Found"
- Verify vite.config.js build output is set to `dist`
- Check frontend/package.json build script

## Monitoring

### View Logs
1. Vercel Dashboard → Deployments → View Logs
2. Backend logs show WSGI application output
3. Frontend logs show build output

### Performance
- Use Vercel Analytics dashboard
- Monitor Neon query logs
- Check API response times

## Rolling Back
If deployment fails:
1. Go to Vercel Dashboard
2. Navigate to Deployments
3. Click previous successful deployment
4. Click "Rollback to this Deployment"

## Next Steps
- Configure custom domain (if desired)
- Set up CI/CD pipeline
- Add monitoring/alerting
- Configure backups for Neon database
