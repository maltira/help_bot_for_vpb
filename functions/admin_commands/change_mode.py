import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import db, ADMIN_ID
router = Router()

# Обработчик команды /activate
@router.message(Command("activate"))
async def set_active_mode(message: Message):
    uid = message.from_user.id
    if str(uid) == ADMIN_ID:
        res = await db.set_bot_mode('activate')
        if res['status']:
            msg = await message.answer("Бот переведён в активный режим ✅")
        else:
            msg = await message.answer("Не удалось перевести бота в активный режим, проверьте логи")
        await asyncio.sleep(5)
        await msg.delete()

# Обработчик команды /tech
@router.message(Command("tech"))
async def set_tech_mode(message: Message):
    uid = message.from_user.id

    mes = ' '.join(message.text.split(' ')[1:])
    data = '🛟 Технические работы: ' + mes if mes else '🛟 Сервис на технических работах, скоро всё придёт в норму' # reason
    if str(uid) == ADMIN_ID:
        res = await db.set_bot_mode('tech')
        if res['status']:
            msg = await message.answer(data)
        else:
            msg = await message.answer("Не удалось перевести бота в тех. режим, проверьте логи")

        await asyncio.sleep(5)
        await msg.delete()