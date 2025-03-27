from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from config import db
from functions.ticket.admin_commands.list_of_tickets.list_all_tickets import generate_buttons

router = Router()

@router.callback_query(lambda c: c.data.startswith('page_'))
async def cur_page(callback_query: CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    all_tic = await db.get_open_ticket()

    buttons = generate_buttons(all_tic['list'], page)
    await callback_query.message.edit_text(
        f'Список активных тикетов ({len(all_tic['list'])}):',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

    await callback_query.answer()
