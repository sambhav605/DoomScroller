"""
config.py
Centralized configuration for DoomScroller.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
CHROMA_PERSIST_DIR = BASE_DIR / "memory" / "chroma_data"

# --- Email ---
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", EMAIL_ADDRESS)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "587")

# --- LLM providers ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# --- RSS feeds ---
RSS_FEEDS = {
    "RONB Post": "https://ronbpost.com/feed",  # adjust to your actual dict
}

# --- Briefing settings ---
BRIEFING_LANGUAGE = os.getenv("BRIEFING_LANGUAGE", "English")
MIN_SUMMARY_LENGTH = 100
MAX_SIMILARITY = 0.97
MEMORY_RETENTION_DAYS = 7

# --- Validation ---
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise EnvironmentError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env")