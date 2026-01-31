# Category Management System - Vercel Deployment Guide

## Vercel Deployment Steps

### 1. Prerequisites
- Vercel account
- Redis database URL (already configured in your .env)

### 2. Environment Variables
Add these to your Vercel project settings:

```
REDIS_URL=your_redis_url_here
JWT_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

### 3. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

#### Option B: Using GitHub Integration
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure environment variables
4. Deploy

### 4. Configuration Files

The following files have been optimized for Vercel:

- **vercel.json** - Vercel deployment configuration
- **runtime.txt** - Python version specification
- **Procfile** - Process configuration
- **.vercelignore** - Files to ignore during deployment

### 5. Key Optimizations Made

1. **Serverless Redis Connection**
   - Connection pooling enabled
   - Shorter timeouts (3 seconds)
   - Lazy initialization for cold starts
   - Health check intervals

2. **CORS Configuration**
   - Properly configured for cross-origin requests
   - Supports all necessary headers

3. **Error Handling**
   - Better error responses for API routes
   - Proper 404 and 500 handling

4. **Database Initialization**
   - Skipped on serverless (Vercel)
   - Data loads on-demand from Redis

### 6. Testing Deployment

After deployment, test these endpoints:
- `https://your-app.vercel.app/` - Home page
- `https://your-app.vercel.app/api/audiences/` - API endpoint
- `https://your-app.vercel.app/category-page` - Category page

### 7. Troubleshooting

If Add Audience button doesn't work:
1. Check browser console for errors
2. Verify REDIS_URL in Vercel environment variables
3. Check API endpoint responses
4. Ensure JWT_SECRET_KEY is set

### 8. Monitoring

Monitor your deployment:
- Vercel Dashboard: https://vercel.com/dashboard
- Function Logs: Check for Redis connection issues
- Error tracking: Monitor 500 errors
