import asyncio
from config import db, bot, dp

import router

# Запуск бота
async def main():
    # Подключаемся к БД
    await db.connect()
    await bot.delete_webhook(drop_pending_updates=True)

    print("Технический бот был запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())