import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from config import ADMIN_ID

router = Router()

@router.message(Command('logs'))
async def get_logs(message: Message):
    uid = message.from_user.id

    if str(uid) == ADMIN_ID:
        filename = 'help_bot/logs/bot.log'
        if os.path.exists(filename):
            document = FSInputFile(filename)
            await message.answer_document(document=document)
        else:
            await message.answer(
                '❌ Неверный путь до файла логов или файла не существует'
            )