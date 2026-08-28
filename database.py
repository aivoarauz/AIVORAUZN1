import datetime

import aiosqlite

DB_PATH = "bot_database.db"

# Bot birinchi marta ishga tushganda o'rnatiladigan standart sozlamalar.
# Bularning barchasi keyinchalik admin panel orqali o'zgartirilishi mumkin.
DEFAULT_SETTINGS = {
    "gemini_price": "50000",
    "channel_price": "100000",
    "channel_link": "https://t.me/+CBYCD-u8N7cwMDcy",
    "card_number": "8600 1234 5678 9012",
    "card_holder": "ISM FAMILIYA",
    "help_username": "@ABDRFV_11",
    "required_channel": "@aivora_uz",
    "gemini_info": (
        "Obunaga nimalar kiradi?🤔\n\n"
        "✅ Gemini Pro — matn yozish, tarjima qilish, dasturlash, tahlil va "
        "kundalik ishlar uchun kuchli AI yordamchi. 🧠✨\n\n"
        "⭐ Antigravity — kod yozish, kodni tahlil qilish va murakkab "
        "dasturlash vazifalari uchun. 💻⚙️\n\n"
        "✅ Flow — AI yordamida video yaratish. 🎬 Har oy 1000 ta kredit "
        "beriladi. 🎁\n\n"
        "🟠 Nano Banana — rasmlar yaratish va ularni AI yordamida "
        "tahrirlash. 🎨🖌\n\n"
        "✅️ Veo 3 — yuqori sifatli va realistlik AI videolar yaratish. 📷🚀\n\n"
        "✅ NotebookLM — PDF, Word va boshqa hujjatlar bilan ishlash, "
        "konspekt tuzish va savollarga javob olish. 📚🗒\n\n"
        "✅ 5 TB xotira ⬇️\n\n"
        "Kimlar uchun? 👇\n\n"
        "👨‍🎓 Talabalar\n"
        "🖥 Dasturchilar\n"
        "🖌 Dizaynerlar\n"
        "📈 Marketologlar va SMM mutaxassislari\n"
        "🎥 Kontent yaratuvchilar\n"
        "📱Amerika Yutubda AI Videolar Qilib Pul Ishlaydiganlar uchun✅\n"
        "🚀 AI imkoniyatlaridan maksimal foydalanishni istagan har bir kishi."
    ),
    "instruction_text": (
        "📖 Bot bilan ishlash yo'riqnomasi:\n\n"
        "1️⃣ 💎 Gemini Pro sotib olish — Gemini Pro obunasini sotib olish "
        "uchun bosing, nechta dona kerakligini tanlang va to'lovni amalga "
        "oshiring.\n"
        "2️⃣ 🎬 AI Videolar kanali — yopiq kanalga qo'shilish uchun to'lov "
        "qiling.\n"
        "3️⃣ To'lovni amalga oshirgach \"✅ To'lov qildim\" tugmasini "
        "bosing.\n"
        "4️⃣ Admin to'lovingizni tekshirib tasdiqlaydi va sizga kerakli "
        "havolani yuboradi.\n"
        "5️⃣ 👥 Referal dasturi orqali do'stlaringizni taklif qilib, "
        "sovg'alar yutib oling.\n\n"
        "Savollaringiz bo'lsa 🆘 Yordam tugmasi orqali admin bilan "
        "bog'laning."
    ),
    "referral_template": (
        "🎉 Tabriklaymiz!\n\n👤 Foydalanuvchi: {user}\n"
        "Siz botga {count} ta odam qo'shdingiz!"
    ),
}


async def init_db(path: str) -> None:
    """Ma'lumotlar bazasini ishga tushiradi va standart sozlamalarni yozadi."""
    global DB_PATH
    DB_PATH = path
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                referrer_id INTEGER,
                referral_count INTEGER DEFAULT 0,
                joined_at TEXT
            )"""
        )
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product TEXT,
                quantity INTEGER,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )"""
        )
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )"""
        )
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                text TEXT,
                created_at TEXT
            )"""
        )
        await conn.commit()
        for key, value in DEFAULT_SETTINGS.items():
            await conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        await conn.commit()


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

async def get_setting(key: str) -> str:
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cur.fetchone()
        if row:
            return row[0]
        return DEFAULT_SETTINGS.get(key, "")


async def set_setting(key: str, value: str) -> None:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await conn.commit()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def add_user(user_id: int, username: str, full_name: str, referrer_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO users "
            "(user_id, username, full_name, referrer_id, referral_count, joined_at) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (user_id, username, full_name, referrer_id,
             datetime.datetime.utcnow().isoformat()),
        )
        await conn.commit()


async def increment_referral(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT referral_count FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cur.fetchone()
        return row["referral_count"] if row else 0


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("SELECT user_id FROM users")
        rows = await cur.fetchall()
        return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

async def create_order(user_id: int, product: str, quantity: int, amount: int) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "INSERT INTO orders (user_id, product, quantity, amount, status, created_at) "
            "VALUES (?, ?, ?, ?, 'pending', ?)",
            (user_id, product, quantity, amount,
             datetime.datetime.utcnow().isoformat()),
        )
        await conn.commit()
        return cur.lastrowid


async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def update_order_status(order_id: int, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id)
        )
        await conn.commit()


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

async def add_comment(user_id: int, username: str, text: str) -> None:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO comments (user_id, username, text, created_at) "
            "VALUES (?, ?, ?, ?)",
            (user_id, username, text, datetime.datetime.utcnow().isoformat()),
        )
        await conn.commit()


async def get_comments(limit: int = 15):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM comments ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT COUNT(*) AS c FROM users")
        users = (await cur.fetchone())["c"]

        cur = await conn.execute(
            "SELECT COUNT(*) AS c FROM orders WHERE product='gemini' AND status='completed'"
        )
        gemini_sold = (await cur.fetchone())["c"]

        cur = await conn.execute(
            "SELECT COUNT(*) AS c FROM orders WHERE product='channel' AND status='completed'"
        )
        channel_sold = (await cur.fetchone())["c"]

        cur = await conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS s FROM orders WHERE status='completed'"
        )
        income = (await cur.fetchone())["s"]

        return {
            "users": users,
            "gemini_sold": gemini_sold,
            "channel_sold": channel_sold,
            "income": income,
        }
