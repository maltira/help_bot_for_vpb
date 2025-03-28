from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_ID, db

router = Router()

@router.callback_query(lambda c: c.data.startswith('goto-ticket_'))
async def all_tickets(callback_query: CallbackQuery):
    uid = callback_query.from_user.id

    if str(uid) == ADMIN_ID:
        ticket_id = int(callback_query.data.split('_')[1])
        bt1 = InlineKeyboardButton(text='◀️ Назад', callback_data='list-tickets')
        bt2 = InlineKeyboardButton(text="Закрыть тикет", callback_data=f'close-ticket_{ticket_id}')
        n = '0' * (5 - len(str(ticket_id))) + str(ticket_id)
        ticket = await db.get_ticket(ticket_id)

        if ticket['status']:
            ticket = ticket['ticket']
            bt3 = InlineKeyboardButton(text="Начать диалог", callback_data=f'create-dialog_{ticket_id}_{ticket['sender_id']}')
            await callback_query.message.edit_text(
                f'*Тикет №{n}*\n'
                f'```\n{ticket['message']}\n```'
                f'От пользователя: {ticket['sender_id']} [ссылка](tg://user?id={ticket['sender_id']})\n\n'
                f'🟢 Статус: {ticket['status']}\n\n'
                f'📅 Дата создания: {ticket['created_at']}',
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt3],[bt2], [bt1]])
            )
        else:
            await callback_query.message.edit_text(
                f'Не удалось получить тикет: {ticket['error']}',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]])
            )



