import os
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
API_BASE_URL = os.getenv("API_BASE_URL", "").strip().rstrip("/")

EMAIL = os.getenv("EMAIL", "").strip()
PASSWORD = os.getenv("PASSWORD", "").strip()

STORAGE_STATE_PATH = "storage/auth.json"
EXCEL_PROFILE_PATH = "data/update_profile_payload.xlsx"

DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", 3000))
UI_TIMEOUT = int(os.getenv("UI_TIMEOUT", 5000))
STEP_PAUSE = int(os.getenv("STEP_PAUSE", 200))
