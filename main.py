import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import router
from database.db import init_database


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found in .env")


async def main():
    # Создаём/проверяем базу данных
    init_database()

    # Создаём Telegram-бота
    bot = Bot(token=TOKEN)

    # Создаём диспетчер
    dp = Dispatcher()

    # Подключаем обработчики
    dp.include_router(router)

    print("Tonavio is running...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())