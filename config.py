import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
YOOKASSA_PROVIDER_TOKEN = os.getenv("YOOKASSA_PROVIDER_TOKEN")

if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в файле .env")