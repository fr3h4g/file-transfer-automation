"""Load settings from env vars."""
import os

from dotenv import load_dotenv

load_dotenv()

FOLDERS_DIR = "./data/folders"
WORK_DIR = "./data/work"
SCRIPTS_DIR = "./data/scripts"

MYSQL_HOST: str = str(os.getenv("MYSQL_HOST"))
MYSQL_USER: str = str(os.getenv("MYSQL_USER"))
MYSQL_PASS: str = str(os.getenv("MYSQL_PASS"))
MYSQL_DB: str = str(os.getenv("MYSQL_DB"))

DEV_MODE: bool = bool(os.getenv("DEV_MODE", False))  # used for local development

DIR_ADDON = ""
if DEV_MODE:
    DIR_ADDON = "."

FOLDERS_DIR = DIR_ADDON + "/data/folders"
WORK_DIR = DIR_ADDON + "/data/work"
SCRIPTS_DIR = DIR_ADDON + "/data/scripts"
