import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
from handlers.admin import router as admin_router
from handlers.user import router as user_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_health_server() -> None:
    """Render 'Web Service' portni tinglashni talab qiladi, shuning uchun
    oddiy HTTP server ishga tushiramiz. Bot polling rejimida ishlaydi."""
    port = int(os.getenv("PORT", "10000"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Bot ishlamoqda! ✅".encode("utf-8"))

        def log_message(self, format, *args) -> None:  # noqa: A002
            pass

    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


async def main() -> None:
    await db.init_db(config.DB_PATH)

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    me = await bot.get_me()
    dp["bot_username"] = me.username
    logger.info("Bot ishga tushdi: @%s", me.username)

    dp.include_router(admin_router)
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    asyncio.run(main())
