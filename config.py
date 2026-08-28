import os

from dotenv import load_dotenv

load_dotenv()

# Bot token @BotFather dan olinadi
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Adminlarning Telegram ID raqamlari (vergul bilan ajratilgan)
# Masalan: ADMIN_IDS=123456789,987654321
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",")
    if x.strip().isdigit()
]

# Ma'lumotlar bazasi fayli manzili
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN aniqlanmagan! .env fayliga yoki Render environment "
        "sozlamalariga BOT_TOKEN qiymatini kiriting."
    )

if not ADMIN_IDS:
    print(
        "⚠️  OGOHLANTIRISH: ADMIN_IDS aniqlanmagan! "
        "Admin panel hech kim uchun ishlamaydi. "
        ".env fayliga ADMIN_IDS=123456789 kabi qiymat kiriting."
    )
