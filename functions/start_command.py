from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from config import ADMIN_ID, db

router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: Message):
    uid = message.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        username = message.from_user.username
        bt1 = InlineKeyboardButton(text="📄 Создать тикет", callback_data='create-ticket')
        bt2 = InlineKeyboardButton(text="FAQ", callback_data='faq')
        bt3 = InlineKeyboardButton(text="Мои обращения", callback_data='my-tickets')

        await message.answer(
            f'🤝 <b>{username}, привет! На связи бот технической поддержки!</b>\n\nЕсли у тебя возникли вопросы или появилась проблема, связаная с использованием VPN-сервиса, создай тикет (обращение):',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1],[bt3],[bt2]]),
            parse_mode='HTML'
        )
    else:
        await message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')


# Обработчик колбека start
@router.callback_query(lambda c: c.data == 'start')
async def start_callback(callback_query: CallbackQuery):
    uid = callback_query.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        username = callback_query.from_user.username
        bt1 = InlineKeyboardButton(text="📄 Создать тикет", callback_data='create-ticket')
        bt2 = InlineKeyboardButton(text="FAQ", callback_data='faq')
        bt3 = InlineKeyboardButton(text="Мои обращения", callback_data='my-tickets')

        await callback_query.message.edit_text(
            f'🤝 <b>{username}, привет! На связи бот технической поддержки!</b>\n\n'
            'Если у тебя возникли вопросы или появилась проблема, связаная с использованием VPN-сервиса, создай тикет (обращение)\n\n'
            'Перед созданием обращения ознакомься с инструкциями и решениями основных возможных ошибок <b>на странице FAQ</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1],[bt3],[bt2]]),
            parse_mode='HTML'
        )
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()