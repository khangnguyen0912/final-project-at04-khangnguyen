import os
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
API_BASE_URL = os.getenv("API_BASE_URL", "").strip().rstrip("/")

EMAIL = os.getenv("EMAIL", "").strip()
PASSWORD = os.getenv("PASSWORD", "").strip()

STORAGE_STATE_PATH = "storage/auth.json"
EXCEL_PROFILE_PATH = "data/update_profile_payload.xlsx"

DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", 5000))  # Max wait for API and common test actions (ms)
UI_TIMEOUT = int(os.getenv("UI_TIMEOUT", 5000))  # Max wait for UI actions like load/click/fill (ms)
STEP_PAUSE = int(os.getenv("STEP_PAUSE", 200))  # Small sleep between test steps (ms)
UI_SLOW_MO = int(os.getenv("UI_SLOW_MO", 1000))  # Delay each browser action to see behavior clearly (ms)
