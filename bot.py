import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_database
from handlers.start import router as start_router
from handlers.ads import router as ads_router


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в файле .env")


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(ads_router)


async def main():
    init_database()

    print("Бот запускается...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())