"""Load settings from env vars."""
import os

from dotenv import load_dotenv

load_dotenv()

DEV_MODE: bool = bool(os.getenv("DEV_MODE", False))  # used for local development

DIR_ADDON = ""
if DEV_MODE:
    DIR_ADDON = "."

DATA_DIR = "/data"
FOLDERS_DIR = DIR_ADDON + os.path.join(DATA_DIR, "folders")
WORK_DIR = DIR_ADDON + os.path.join(DATA_DIR, "work")
# SCRIPTS_DIR = DIR_ADDON + os.path.join(DATA_DIR, "scripts")

DATABASE_URL = f"sqlite:///{DATA_DIR}/file-transfer-automation.db"

if DEV_MODE:
    DATABASE_URL = "sqlite:///test.db"

DATABASE_URL = str(os.getenv("DATABASE_URL", DATABASE_URL))

DISABLE_JOBS: bool = bool(os.getenv("DISABLE_JOBS", False))

SMTP_HOSTNAME = str(os.getenv("SMTP_HOSTNAME", "localhost"))
SMTP_USERNAME = str(os.getenv("SMTP_USERNAME", ""))
SMTP_PASSWORD = str(os.getenv("SMTP_PASSWORD", ""))
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 25))
SMTP_TLS: bool = bool(os.getenv("SMTP_TLS", False))
