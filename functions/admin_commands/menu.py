from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from config import ADMIN_ID, db

router = Router()

@router.message(Command('menu'))
async def all_tickets(message: Message):
    uid = message.from_user.id

    if str(uid) == ADMIN_ID:
        bt1 = InlineKeyboardButton(text='Открытые тикеты', callback_data='list-tickets')
        buttons = [[bt1]]
        await message.answer(
            'Панель администратора:',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
@router.callback_query(lambda c: c.data == 'menu')
async def all_tickets(callback_query: CallbackQuery):
    uid = callback_query.from_user.id

    if str(uid) == ADMIN_ID:
        bt1 = InlineKeyboardButton(text='Открытые тикеты', callback_data='list-tickets')
        buttons = [[bt1]]
        await callback_query.message.edit_text(
            'Панель администратора:',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    await callback_query.answer()