# Deployment Guide

## Frontend Deployment to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier available)

### Steps:

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL`: `https://yourusername.pythonanywhere.com/api`
   - Click "Deploy"

3. **Update API URL**:
   - After backend deployment, update the environment variable with your actual PythonAnywhere URL

## Backend Deployment to PythonAnywhere

### Prerequisites
- PythonAnywhere account (free tier available)

### Steps:

1. **Upload files**:
   - Go to PythonAnywhere dashboard
   - Open "Files" tab
   - Upload all files from `backend/` directory to `/home/yourusername/mysite/`

2. **Install dependencies**:
   - Open "Consoles" tab
   - Start a Bash console
   - Run:
     ```bash
     cd mysite
     pip3.10 install --user -r requirements.txt
     ```

3. **Setup database**:
   ```bash
   cd mysite
   python3.10 -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
   python3.10 app.py  # This will seed the database
   ```

4. **Configure Web App**:
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Select Python 3.10
   - Set source code directory: `/home/yourusername/mysite`
   - Set WSGI configuration file: `/home/yourusername/mysite/wsgi.py`

5. **Update WSGI file**:
   - Edit `/home/yourusername/mysite/wsgi.py`
   - Replace `yourusername` with your actual username
   - Replace `mysite` with your actual directory name

6. **Set environment variables**:
   - In Web tab, go to "Environment variables"
   - Add:
     - `FLASK_ENV`: `production`
     - `SECRET_KEY`: `your-super-secret-key`
     - `JWT_SECRET_KEY`: `your-jwt-secret-key`
     - `CORS_ORIGINS`: `https://your-vercel-app.vercel.app`

7. **Enable HTTPS and reload**:
   - In Web tab, enable "Force HTTPS"
   - Click "Reload" button

## Post-Deployment

1. **Update frontend API URL**:
   - In Vercel dashboard, update `NEXT_PUBLIC_API_URL` to your PythonAnywhere URL
   - Redeploy frontend

2. **Test the application**:
   - Visit your Vercel URL
   - Login with: `admin@company.com` / `admin123`
   - Test all features

## Default Login Credentials

- **Admin**: admin@company.com / admin123
- **Manager**: manager@company.com / manager123  
- **Employee**: employee@company.com / employee123

## Troubleshooting

### Frontend Issues:
- Check browser console for errors
- Verify API URL in environment variables
- Check CORS settings in backend

### Backend Issues:
- Check PythonAnywhere error logs
- Verify all dependencies are installed
- Check database file permissions
- Verify WSGI configuration

### CORS Issues:
- Ensure frontend URL is added to CORS_ORIGINS
- Check that both HTTP and HTTPS versions are allowed
- Verify environment variables are set correctly