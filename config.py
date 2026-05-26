# config.py — Central configuration for SMS Budget Tracker

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """All project settings in one place. No hardcoding anywhere else."""

    # ═══ Supabase ═══
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    # ═══ Ollama ═══
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = "llama3.1:8b"
    OLLAMA_TIMEOUT = 30

    # ═══ File Paths ═══
    EXCEL_FILE = "Ultimate Personal Budget Manager.xlsx"
    EXCEL_BACKUP = "Ultimate Personal Budget Manager_BACKUP.xlsx"
    CATEGORY_MAP_FILE = "CATEGORY_MAP.json"

    # ═══ Retry Settings ═══
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    RETRY_BACKOFF = 2

    # ═══ Circuit Breaker ═══
    CB_THRESHOLD = 5
    CB_TIMEOUT = 300

    # ═══ Listener ═══
    POLL_INTERVAL = 30

    # ═══ Categorization ═══
    FUZZY_MATCH_CUTOFF = 0.75

    # ═══ Timezone ═══
    TIMEZONE = "Asia/Kolkata"