"""
MCP server for creating users in the Project Status Tracker application.

This server exposes a single tool, `add_user`, which:
- accepts a user's email (and optional display name)
- generates a secure random password
- calls the backend API `/api/v1/auth/register` to create the user
- returns the created user's basic info and the generated password

Dependencies are in the server's Poetry project (server/pyproject.toml).
Run from repo root: cd server && poetry run python ../mcp_add_user_server.py

Configuration (environment variables):
- PROJECT_STATUS_API_BASE_URL: Base URL of the backend API.
    - Example (local): http://localhost:8000
    - Example (prod):  https://project-status-tracker-production.up.railway.app
- PORT (optional): Port for this MCP server to listen on (default: 8080)
"""

import logging
import os
import secrets
import string
import sys
from typing import Dict, Optional

import requests
from mcp.server.fastmcp import FastMCP


SERVER_NAME = "project-status-tracker-user-admin"

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(SERVER_NAME)


def _generate_password(length: int = 16) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits
    # You can add punctuation if you want stronger passwords:
    # alphabet += string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _get_api_base_url() -> str:
    """Get the backend API base URL from environment variables."""
    base_url = os.environ.get("PROJECT_STATUS_API_BASE_URL")
    if not base_url:
        raise RuntimeError(
            "PROJECT_STATUS_API_BASE_URL is not set. "
            "Set it to your backend API base URL, e.g. "
            "http://localhost:8000 or "
            "https://project-status-tracker-production.up.railway.app"
        )
    return base_url.rstrip("/")


port = int(os.environ.get("PORT", "8080"))
mcp = FastMCP(SERVER_NAME, logger=logger, port=port)


@mcp.tool()
def add_user(email: str, name: Optional[str] = None) -> Dict[str, str]:
    """
    Create a new user in Project Status Tracker with an auto-generated password.

    Args:
        email: User email address.
        name: Optional display name. If omitted, the local part of the email is used.

    Returns:
        A dict containing:
        - email: The user's email.
        - name: The user's name.
        - password: The generated password (store or share securely!).
        - id: The created user's ID (if returned by the API).

    Notes:
        This uses the public registration endpoint (`/api/v1/auth/register`),
        which creates users with the default `user` role.
    """
    logger.info("add_user tool called for email=%s", email)

    if not email or "@" not in email:
        raise ValueError("A valid email address is required.")

    if name is None:
        name = email.split("@", 1)[0]

    password = _generate_password()
    base_url = _get_api_base_url()

    payload = {
        "email": email,
        "password": password,
        "name": name,
    }

    url = f"{base_url}/api/v1/auth/register"
    logger.info("Calling backend registration endpoint: %s", url)

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as e:
        # Try to surface API error details if available
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        logger.error("Backend returned error: %s - %s", e, detail)
        raise RuntimeError(f"Backend error: {detail}") from e
    except requests.RequestException as e:
        logger.error("Request to backend failed: %s", e)
        raise RuntimeError(f"Failed to reach backend API: {e}") from e

    data = response.json()

    # Don't log the password here to avoid leaking credentials
    result: Dict[str, str] = {
        "email": email,
        "name": name,
        "password": password,
    }

    user_id = data.get("id")
    if user_id is not None:
        result["id"] = str(user_id)

    return result


if __name__ == "__main__":
    logger.info("Starting MCP server '%s' on port %s...", SERVER_NAME, port)
    try:
        mcp.run(transport="sse")
    except Exception as e:  # pragma: no cover - defensive logging
        logger.error("Server error: %s", e)
        sys.exit(1)
    finally:
        logger.info("MCP server '%s' terminated", SERVER_NAME)

