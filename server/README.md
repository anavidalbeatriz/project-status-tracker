# Project Status Tracker - Server

FastAPI backend for the Project Status Tracker application.

## Setup

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` (if it exists)
   - Or create a `.env` file with your configuration

4. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

5. Start the development server:
   ```bash
   poetry run uvicorn main:app --reload
   ```

## Project Structure

```
server/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core configuration and utilities
│   └── db/            # Database models and connection
├── alembic/           # Database migrations
├── main.py            # Application entry point
└── pyproject.toml     # Poetry configuration
```

## Development

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Adding Dependencies

To add a new dependency:
```bash
poetry add package-name
```

To add a development dependency:
```bash
poetry add --group dev package-name
```

## Note on poetry.lock

The `poetry.lock` file should be committed to the repository to ensure consistent dependency versions across all environments.
