import os
from pathlib import Path
from dotenv import load_dotenv

# Locate Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variable from .env file
load_dotenv(PROJECT_ROOT / ".env")

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI API KEY is missing. Check .env file")

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./database/tasks.db"
) 

# Reminder scheduler window
# Prefer the correct spelling but support the variable name
REMINDER_WINDOW_MINUTES = os.getenv(
    "REMINDER_WINDOW_MINUTES",
    os.getenv("REMAINDER_WINDOW_MINUTES")
)