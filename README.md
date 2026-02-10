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

## License

[Add your license here]
