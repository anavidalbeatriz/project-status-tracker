# Project Status Tracker

A web application that allows tech leads to update project status through AI-powered transcription processing.

## Live Deployment

- **Frontend**: [https://project-status-tracker-client.vercel.app](https://project-status-tracker-client.vercel.app) (Vercel)
- **Backend API**: [https://project-status-tracker-production.up.railway.app](https://project-status-tracker-production.up.railway.app) (Railway)
- **Database**: Neon PostgreSQL (Serverless)

## Project Structure

```
project-status-tracker-kis/
├── server/          # FastAPI backend
├── client/          # React frontend
├── REQUIREMENTS.md  # Project requirements
└── IMPLEMENTATION_PLAN.md  # Implementation plan
```

## Technology Stack

- **Backend**: Python/FastAPI
- **Frontend**: React
- **Database**: PostgreSQL
- **AI/ML**: OpenAI API
- **Authentication**: OAuth2

## Getting Started

### Prerequisites

- Python 3.9+
- Poetry - [Install Poetry](https://python-poetry.org/docs/#installation)
- Node.js 16+
- Docker Desktop - [Install Docker](https://www.docker.com/products/docker-desktop/) (for PostgreSQL database)

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Start PostgreSQL database with Docker:
```bash
docker-compose up -d
```

3. Install dependencies with Poetry:
```bash
poetry install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
poetry run alembic upgrade head
```

6. Start the development server:
```bash
poetry run uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm start
```

## Development

See `IMPLEMENTATION_PLAN.md` for detailed implementation phases and progress.

### MCP server for adding users

This repo includes a small MCP server that can create application users by email and auto-generate a password.

- **Location**: `mcp_add_user_server.py`
- **Dependencies**: Managed in the server's Poetry project (`server/pyproject.toml`). Install with:

  ```bash
  cd server
  poetry install
  ```

- **Configuration**:
  - Set `PROJECT_STATUS_API_BASE_URL` to your backend API URL  
    - Local example: `http://localhost:8000`  
    - Production example: `https://project-status-tracker-production.up.railway.app`
  - Optional: set `PORT` (default: `8080`) for the MCP server.

- **Run the MCP server** (from repo root, using the server's Poetry env):

  ```bash
  cd server && poetry run python ../mcp_add_user_server.py
  ```

It exposes a single MCP tool, `add_user(email, name=None)`, which:
- generates a secure random password
- calls `/api/v1/auth/register` on the backend
- returns the created user's basic info plus the generated password.

## License

[Add your license here]
