# Setup Guide

This guide will help you set up the Project Status Tracker application for development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - [Install Poetry](https://python-poetry.org/docs/#installation)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Backend Setup (FastAPI)

### 1. Navigate to the server directory

```bash
cd server
```

### 2. Install dependencies with Poetry

Poetry will automatically create a virtual environment for you:

```bash
poetry install
```

This will install all dependencies defined in `pyproject.toml`.

### 3. Activate the Poetry shell (optional)

If you want to run commands in the Poetry virtual environment:

```bash
poetry shell
```

Alternatively, you can run commands using `poetry run`:

```bash
poetry run uvicorn main:app --reload
```

### 3. Set up environment variables

Create a `.env` file in the `server` directory:

```bash
# Copy the example file (if it exists)
cp .env.example .env
```

Or create a new `.env` file with the following content:

```env
# Database (Docker setup - default credentials)
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

**Important:** Replace the placeholder values with your actual configuration:
- `DATABASE_URL`: Update with your PostgreSQL credentials
- `SECRET_KEY`: Generate a secure random string for production
- `OPENAI_API_KEY`: Add your OpenAI API key when ready

### 4. Set up PostgreSQL database with Docker

Start PostgreSQL using Docker Compose:

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL 15 container
- Create the `project_tracker_db` database
- Expose PostgreSQL on port 5438
- Persist data in a Docker volume

To stop the database:
```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

**Note:** Make sure Docker Desktop is running before executing these commands.

### 5. Run database migrations

```bash
poetry run alembic upgrade head
```

### 6. Start the development server

```bash
poetry run uvicorn main:app --reload
```

Or if you're in the Poetry shell:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

## Frontend Setup (React)

### 1. Navigate to the client directory

```bash
cd client
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env` file in the `client` directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### 4. Start the development server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3002`

## Running Both Servers

To run both the backend and frontend simultaneously:

### Option 1: Separate Terminals

1. Terminal 1 (Backend):
```bash
cd server
poetry run uvicorn main:app --reload
```

Or activate Poetry shell first:
```bash
cd server
poetry shell
uvicorn main:app --reload
```

2. Terminal 2 (Frontend):
```bash
cd client
npm run dev
```

### Option 2: Using npm scripts (if configured)

You can create a root-level `package.json` with scripts to run both servers.

## Verification

1. **Backend Health Check:**
   - Visit `http://localhost:8000/health`
   - Should return: `{"status": "healthy"}`

2. **API Documentation:**
   - Visit `http://localhost:8000/docs`
   - Should show Swagger UI with API endpoints

3. **Frontend:**
   - Visit `http://localhost:3002`
   - Should show the Project Status Tracker homepage

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Verify the `DATABASE_URL` in `.env` is correct
- Check that the database exists

### Port Already in Use

- Backend (8000): Change the port in `uvicorn main:app --reload --port 8001`
- Frontend (3002): Vite will automatically use the next available port

### Module Not Found Errors

- Ensure Poetry dependencies are installed: `poetry install` (backend)
- Activate Poetry shell: `poetry shell` (backend)
- Or use `poetry run` before commands (backend)
- Run `npm install` again (frontend)

## Next Steps

Once setup is complete, you can proceed with:
- Phase 2: Authentication & User Management
- Phase 3: Project Management (CRUD Operations)
- Phase 4: AI Transcription Processing

See `IMPLEMENTATION_PLAN.md` for details.
