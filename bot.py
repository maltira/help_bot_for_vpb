import asyncio

from aiogram.types import BotCommand

from config import db, bot, dp

import router

async def set_commands():
    commands = [
        BotCommand(command="start", description="Начало работы | Get started"),
    ]
    await bot.set_my_commands(commands)

# Запуск бота
async def main():
    # Подключаемся к БД
    await db.connect()
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()

    print("Технический бот был запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())