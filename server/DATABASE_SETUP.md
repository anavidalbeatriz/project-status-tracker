# PostgreSQL Database Setup Guide

## Option 1: Using Docker (Recommended)

### Prerequisites
- Docker Desktop installed and running

### Step 1: Start PostgreSQL Container

From the project root directory:

```bash
docker-compose up -d
```

This will:
- Pull the PostgreSQL 15 Alpine image (if not already present)
- Start a container named `project-tracker-db`
- Create the database `project_tracker_db`
- Expose PostgreSQL on port 5438 (mapped from container port 5432)
- Persist data in a Docker volume

### Step 2: Verify Database is Running

```bash
# Check container status
docker ps

# Check logs
docker logs project-tracker-db

# Test connection
docker exec -it project-tracker-db psql -U postgres -d project_tracker_db
```

### Step 3: Configure .env File

Create a `.env` file in the `server` directory:

```env
# Database (Docker setup)
DATABASE_URL=postgresql://postgres:postgres@localhost:5438/project_tracker_db

# Application
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3002,http://localhost:5173

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# File Upload
MAX_UPLOAD_SIZE=104857600
UPLOAD_DIR=uploads

# Environment
ENVIRONMENT=development
```

### Step 4: Run Migrations

```bash
cd server
poetry run alembic upgrade head
```

### Docker Commands

**Start database:**
```bash
docker-compose up -d
```

**Stop database (keeps data):**
```bash
docker-compose down
```

**Stop and remove all data:**
```bash
docker-compose down -v
```

**View logs:**
```bash
docker-compose logs -f postgres
```

**Access PostgreSQL CLI:**
```bash
docker exec -it project-tracker-db psql -U postgres -d project_tracker_db
```

**Reset database (remove all data and start fresh):**
```bash
docker-compose down -v
docker-compose up -d
```

## Option 2: Local PostgreSQL Installation

If you prefer to use a local PostgreSQL installation instead of Docker:

### Step 1: Install PostgreSQL

Download and install from: https://www.postgresql.org/download/windows/

### Step 2: Start PostgreSQL Service

**Using Services (Windows):**
1. Press `Win + R`, type `services.msc`, press Enter
2. Find "postgresql" service
3. Right-click and select "Start"
4. Set it to "Automatic" startup type if desired

**Using PowerShell (Run as Administrator):**
```powershell
# Find PostgreSQL service
Get-Service | Where-Object {$_.DisplayName -like "*PostgreSQL*"}

# Start the service (replace with actual service name)
Start-Service postgresql-x64-XX
```

### Step 3: Create the Database

```powershell
# Connect to PostgreSQL (replace with your postgres user password)
psql -U postgres -h localhost -p 5438

# Or if using default port 5432:
psql -U postgres -h localhost -p 5432
```

Once connected, run:
```sql
CREATE DATABASE project_tracker_db;
\q
```

### Step 4: Configure .env File

Update the `.env` file with your local PostgreSQL credentials:

```env
# Database - Update with your actual credentials
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5438/project_tracker_db

# ... rest of configuration
```

### Step 5: Run Migrations

```bash
cd server
poetry run alembic upgrade head
```

## Troubleshooting

### Docker Issues

**"Cannot connect to Docker daemon"**
- Make sure Docker Desktop is running
- Restart Docker Desktop if needed

**Port already in use**
- Another service is using port 5438
- Change the port mapping in `docker-compose.yml`: `"5439:5432"` (and update DATABASE_URL)

**Container won't start**
- Check logs: `docker-compose logs postgres`
- Verify Docker has enough resources allocated

### Connection Issues

**"Connection refused" Error**
- Docker container not running → `docker-compose up -d`
- Wrong port → Check DATABASE_URL matches docker-compose.yml port mapping
- Firewall blocking → Allow Docker through Windows Firewall

**"Authentication failed" Error**
- Wrong password → Default Docker password is `postgres`
- Update DATABASE_URL if you changed the password in docker-compose.yml

**"Database does not exist" Error**
- Database should be created automatically by Docker
- Check container logs: `docker logs project-tracker-db`

### Testing Database Connection

```bash
# Test from Python
cd server
poetry run python -c "from app.db.database import engine; engine.connect(); print('Database connection successful!')"
```

### Finding PostgreSQL Port (Local Installation)

Check PostgreSQL configuration file:
- Location: `C:\Program Files\PostgreSQL\XX\data\postgresql.conf`
- Look for: `port = 5432` (or your configured port)
