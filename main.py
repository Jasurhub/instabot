import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database import Database
from handlers import user_router, admin_router

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Botni ishga tushirish funksiyasi"""
    if not config.bot_token or config.bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "XATOLIK: .env faylida BOT_TOKEN ko'rsatilmagan! "
            "Iltimos, @BotFather dan olingan tokenni .env fayliga kiriting."
        )
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    db = Database(config.db_path)
    await db.init_db()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash (Admin birinchi bo'lib tekshiriladi)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Eski kutilayotgan yangilanishlarni o'chirish (Drop pending updates)
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    logger.info(f"Admin ID: {config.admin_id}")
    if config.channel_id:
        logger.info(f"Hisobot kanali ID: {config.channel_id}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
