import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_DIR = BASE_DIR / "auth"
REPORTS_DIR = BASE_DIR / "reports"

BASE_URL = os.getenv("BASE_URL", "https://www.pinterest.com").rstrip("/")
EMAIL = os.getenv("PINTEREST_EMAIL", "")
PASSWORD = os.getenv("PINTEREST_PASSWORD", "")
BOARD_NAME = os.getenv("PINTEREST_BOARD", "")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))

HAS_CREDENTIALS = bool(EMAIL and PASSWORD)
