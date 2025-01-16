import logging
import os
import uuid

import dotenv


dotenv.load_dotenv()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# TODO: Check required values

DEBUG: bool = bool(int(os.getenv("DEBUG", False)))

APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
DB_DATABASE: str = os.getenv("DB_DATABASE", "postgres")

GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET")

JWT_ACCESS_TOKEN_SECRET = os.getenv("JWT_ACCESS_TOKEN_SECRET", uuid.uuid4().hex)  # Random if not specified
ISSUE_TRACKER_SECRET = os.getenv("ISSUE_TRACKER_SECRET")

LIGHTNING_BASE_URL: str = os.getenv("LIGHTNING_BASE_URL")

BRANTA_API_KEY: str = os.getenv("BRANTA_API_KEY", "")
BRANTA_BASE_URL: str = os.getenv("BRANTA_BASE_URL", "")
