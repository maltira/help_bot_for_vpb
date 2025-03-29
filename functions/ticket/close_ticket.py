from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import db, ADMIN_ID
from functions.ticket.log_ticket import log_ticket_message

router = Router()

# Обработчик колбека /close-ticket
@router.callback_query(lambda c: c.data.startswith('close-ticket_'))
async def close_ticket(callback_query: CallbackQuery):
    uid = callback_query.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        bt1 = InlineKeyboardButton(text="◀️ Главное меню", callback_data='start')
        ticket_id = callback_query.data.split('_')[1]
        res = await db.close_ticket(callback_query.from_user.id, int(ticket_id))

        n = '0' * (5 - len(ticket_id)) + ticket_id
        if res['status']:

            res = await callback_query.message.edit_text(
                f'✅ *Тикет №{n}*\n'
                'Вы успешно закрыли тикет, если возникнут другие вопросы — создайте новый тикет',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]]),
                parse_mode='Markdown'
            )
            log_ticket_message(n, res)
        else:
            bt2 = InlineKeyboardButton(text="❌ Закрыть тикет", callback_data=f'close-ticket_{ticket_id}')
            await callback_query.message.edit_text(
                'Не удалось закрыть тикет по непредвиденной ошибке, скоро в чат напишет специалист и закроет его!',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1], [bt2]]),
                parse_mode='Markdown'
            )
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()


