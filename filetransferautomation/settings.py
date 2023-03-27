"""Load settings from env vars."""
import os

from dotenv import load_dotenv

load_dotenv()

WORK_DIR = "./work"
DATA_DIR = "./data"

MYSQL_HOST: str = str(os.getenv("MYSQL_HOST"))
MYSQL_USER: str = str(os.getenv("MYSQL_USER"))
MYSQL_PASS: str = str(os.getenv("MYSQL_PASS"))
MYSQL_DB: str = str(os.getenv("MYSQL_DB"))
