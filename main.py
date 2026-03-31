import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers_user import router as user_router
from handlers_admin import router as admin_router

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        logging.error("Iltimos, .env faylida BOT_TOKEN va ADMIN_ID ni o'rnating.")
        return
        
    # Database ni initsializatsiya qilish
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(user_router)
    dp.include_router(admin_router)
    
    logging.info("Bot is starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
