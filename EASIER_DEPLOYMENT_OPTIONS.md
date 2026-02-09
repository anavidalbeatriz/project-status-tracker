# Easier Deployment Options - Project Status Tracker

This guide covers simpler alternatives to AWS for deploying your application. These options require less infrastructure management and are ideal for getting started quickly.

## 🚀 Recommended: Railway (Easiest Overall)

**Railway** is the simplest option - it automatically detects your stack and handles most configuration.

### Why Railway?
- ✅ Automatic deployments from Git
- ✅ Built-in PostgreSQL database
- ✅ Environment variable management
- ✅ Free tier available
- ✅ No infrastructure management needed
- ✅ Automatic HTTPS

### Deployment Steps

#### 1. Backend Deployment

1. **Sign up at [railway.app](https://railway.app)**
2. **Create New Project** → "Deploy from GitHub repo"
3. **Select your repository**
4. **Add PostgreSQL Database:**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway automatically provides connection string

5. **Configure Environment Variables:**
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-key
   STORAGE_TYPE=local
   CORS_ORIGINS=https://your-frontend-url.railway.app
   ```

6. **Set Build Command:**
   ```
   cd server && poetry install --no-dev && poetry run alembic upgrade head
   ```

7. **Set Start Command:**
   ```
   cd server && poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

8. **Deploy!** Railway will automatically build and deploy.

#### 2. Frontend Deployment

1. **Create New Service** in the same project
2. **Deploy from GitHub** (select client folder or create separate repo)
3. **Set Build Command:**
   ```
   npm install && npm run build
   ```

4. **Set Start Command:**
   ```
   npx serve -s dist -l $PORT
   ```

5. **Add Environment Variable:**
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api/v1
   ```

**Cost:** Free tier includes $5/month credit, then ~$5-10/month

---

## 🎯 Option 2: Render (Very Easy)

**Render** offers a great free tier and simple deployment.

### Backend on Render

1. **Sign up at [render.com](https://render.com)**
2. **New → Web Service**
3. **Connect GitHub repository**
4. **Configure:**
   - **Name:** `project-status-backend`
   - **Environment:** Python 3
   - **Build Command:** `cd server && pip install poetry && poetry install --no-dev && poetry run alembic upgrade head`
   - **Start Command:** `cd server && poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add PostgreSQL Database:**
   - New → PostgreSQL
   - Copy connection string

6. **Environment Variables:**
   ```
   DATABASE_URL=<from PostgreSQL service>
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-key
   STORAGE_TYPE=local
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```

### Frontend on Render

1. **New → Static Site**
2. **Connect repository**
3. **Build Command:** `cd client && npm install && npm run build`
4. **Publish Directory:** `client/dist`
5. **Add Environment Variable:**
   ```
   VITE_API_URL=https://your-backend.onrender.com/api/v1
   ```

**Cost:** Free tier available (spins down after inactivity), then $7/month per service

---

## ⚡ Option 3: Vercel (Frontend) + Supabase (Database) + Railway/Render (Backend)

**Best for:** Maximum simplicity with best-in-class services.

### Frontend on Vercel

1. **Sign up at [vercel.com](https://vercel.com)**
2. **Import Git Repository**
3. **Root Directory:** `client`
4. **Build Command:** `npm run build`
5. **Output Directory:** `dist`
6. **Environment Variable:**
   ```
   VITE_API_URL=https://your-backend-url/api/v1
   ```

**Vercel automatically:**
- Provides HTTPS
- Handles CDN
- Deploys on every push
- Free tier is generous

### Database on Supabase

1. **Sign up at [supabase.com](https://supabase.com)**
2. **Create New Project**
3. **Get Connection String:**
   - Settings → Database → Connection String
   - Format: `postgresql://postgres:[password]@[host]:5432/postgres`

4. **Run Migrations:**
   ```bash
   cd server
   export DATABASE_URL=your-supabase-connection-string
   poetry run alembic upgrade head
   ```

**Cost:** Free tier includes 500MB database, then $25/month

---

## 🐳 Option 4: Fly.io (Container-Based)

**Fly.io** is great if you want Docker-based deployment without AWS complexity.

### Setup

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up:** `fly auth signup`

3. **Create `fly.toml` for backend:**
   ```toml
   # server/fly.toml
   app = "project-status-backend"
   primary_region = "iad"

   [build]
     dockerfile = "Dockerfile"

   [env]
     PORT = "8000"

   [[services]]
     internal_port = 8000
     protocol = "tcp"

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

4. **Deploy:**
   ```bash
   cd server
   fly launch
   fly secrets set DATABASE_URL=your-db-url SECRET_KEY=your-key
   fly deploy
   ```

**Cost:** Free tier includes 3 shared VMs, then pay-as-you-go

---

## 🌐 Option 5: Heroku (Classic, Still Easy)

**Heroku** is the classic easy deployment platform.

### Backend on Heroku

1. **Install Heroku CLI**
2. **Login:** `heroku login`
3. **Create app:** `heroku create project-status-backend`
4. **Add PostgreSQL:** `heroku addons:create heroku-postgresql:mini`
5. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-key
   heroku config:set OPENAI_API_KEY=your-key
   heroku config:set STORAGE_TYPE=local
   heroku config:set CORS_ORIGINS=https://your-frontend.herokuapp.com
   ```

6. **Create `Procfile` in server folder:**
   ```
   web: cd server && poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

7. **Create `requirements.txt`:**
   ```bash
   cd server
   poetry export -f requirements.txt --output requirements.txt --without-hashes
   ```

8. **Deploy:**
   ```bash
   git push heroku main
   heroku run alembic upgrade head
   ```

### Frontend on Heroku

1. **Create app:** `heroku create project-status-frontend`
2. **Add buildpack:** `heroku buildpacks:set heroku/nodejs`
3. **Add static buildpack:** `heroku buildpacks:add https://github.com/heroku/heroku-buildpack-static`
4. **Create `static.json` in client folder:**
   ```json
   {
     "root": "dist",
     "clean_urls": true,
     "routes": {
       "/**": "index.html"
     }
   }
   ```

5. **Deploy:** `git push heroku main`

**Cost:** No free tier anymore, starts at $5/month per dyno

---

## 📊 Comparison Table

| Platform | Ease of Use | Free Tier | Cost (Paid) | Best For |
|----------|-------------|-----------|-------------|----------|
| **Railway** | ⭐⭐⭐⭐⭐ | ✅ $5 credit | $5-10/mo | Overall easiest |
| **Render** | ⭐⭐⭐⭐ | ✅ (with limits) | $7/mo/service | Good free tier |
| **Vercel** | ⭐⭐⭐⭐⭐ | ✅ Generous | Free-20/mo | Frontend only |
| **Supabase** | ⭐⭐⭐⭐ | ✅ 500MB DB | $25/mo | Database |
| **Fly.io** | ⭐⭐⭐ | ✅ 3 VMs | Pay-as-you-go | Docker lovers |
| **Heroku** | ⭐⭐⭐⭐ | ❌ | $5+/mo | Classic option |

---

## 🎯 Recommended Stack for Easiest Deployment

**For absolute simplicity:**

1. **Frontend:** Vercel (automatic, free, fast)
2. **Backend:** Railway (automatic, includes DB)
3. **File Storage:** Railway volumes (local) or S3 (if needed)

**Total setup time:** ~30 minutes
**Monthly cost:** $0-10 (depending on usage)

---

## 🚀 Quick Start: Railway (Recommended)

### Complete Setup in 5 Steps

1. **Backend:**
   - Go to railway.app
   - New Project → Deploy from GitHub
   - Select repo → Add PostgreSQL
   - Add environment variables
   - Deploy!

2. **Frontend:**
   - New Service in same project
   - Deploy from GitHub (client folder)
   - Set `VITE_API_URL` to backend URL
   - Deploy!

3. **Database:**
   - Already included! Just run migrations:
   ```bash
   railway run alembic upgrade head
   ```

4. **Done!** Your app is live with HTTPS.

---

## 📝 Environment Variables Template

Use this template for any platform:

```bash
# Database (provided by platform or Supabase)
DATABASE_URL=postgresql://...

# Security
SECRET_KEY=generate-a-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-...

# Storage
STORAGE_TYPE=local  # or "s3" for AWS S3

# CORS (update with your frontend URL)
CORS_ORIGINS=https://your-frontend-domain.com

# AWS S3 (if using S3 storage)
AWS_S3_BUCKET=your-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

---

## 🔧 Platform-Specific Notes

### Railway
- Automatically handles Poetry
- Provides PostgreSQL addon
- Generous free tier
- Best for: Full-stack apps

### Render
- Free tier spins down after inactivity
- Good for: Production apps with consistent traffic
- PostgreSQL included

### Vercel
- Best-in-class frontend hosting
- Automatic preview deployments
- Edge network (very fast)
- Best for: Frontend only

### Supabase
- PostgreSQL with real-time features
- Built-in auth (if you want to use it)
- Good free tier
- Best for: Database needs

---

## 🆘 Troubleshooting

### Common Issues

1. **Database migrations fail:**
   - Make sure `DATABASE_URL` is set correctly
   - Run migrations manually: `railway run alembic upgrade head`

2. **CORS errors:**
   - Update `CORS_ORIGINS` with your frontend URL
   - Include protocol (https://)

3. **Build fails:**
   - Check build commands match your project structure
   - Ensure all dependencies are in `pyproject.toml` or `package.json`

4. **Port binding:**
   - Use `$PORT` environment variable (provided by platform)
   - Backend: `--port $PORT`
   - Frontend: Most platforms handle this automatically

---

## 📚 Next Steps

1. Choose a platform (Railway recommended)
2. Deploy backend
3. Deploy frontend
4. Configure environment variables
5. Run database migrations
6. Test your deployment!

Need help with a specific platform? Each has excellent documentation and support.
