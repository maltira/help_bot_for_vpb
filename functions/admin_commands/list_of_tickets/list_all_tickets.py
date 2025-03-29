import math
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import ADMIN_ID, db

router = Router()

ticket_per_page = 5
def generate_buttons(all_tic, page=1):
    start = (page-1)*ticket_per_page
    end = start + ticket_per_page
    if end > len(all_tic):
        end = len(all_tic)
    page_count = math.ceil(len(all_tic)/ticket_per_page)

    tickets_on_page = all_tic[start:end]

    buttons = []
    for ticket in tickets_on_page:
        buttons.append([InlineKeyboardButton(text=f'Тикет №{ticket['id']}',
                                             callback_data=f'goto-ticket_{ticket['id']}_{ticket['sender_id']}')])

    nav_buttons = []
    if page_count > 1 and page != 1:
        if page == page_count:
            nav_buttons.append(InlineKeyboardButton(text=f'⬅️ [{start-ticket_per_page+1}:{end-1}]', callback_data=f'page_{page-1}'))
        else: nav_buttons.append(InlineKeyboardButton(text=f'⬅️ [{start-ticket_per_page+1}:{end-ticket_per_page}]', callback_data=f'page_{page-1}'))

    if end < len(all_tic):
        nav_buttons.append(InlineKeyboardButton(text=f'[{start+ticket_per_page+1}:{end+ticket_per_page}] ➡️', callback_data=f'page_{page + 1}'))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text='В меню', callback_data='menu')])

    return buttons

@router.callback_query(lambda c: c.data == 'list-tickets')
async def all_tickets(callback_query: CallbackQuery):
    uid = callback_query.from_user.id

    if str(uid) == ADMIN_ID:
        back = InlineKeyboardButton(text='В меню', callback_data='menu')
        all_tic = await db.get_tickets('open')
        if all_tic['status']:
            if all_tic['list']:
                buttons = generate_buttons(all_tic['list'])
                await callback_query.message.edit_text(
                    f'Список активных тикетов ({len(all_tic['list'])}):',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )
            else:
                await callback_query.message.edit_text(
                    'Активных тикетов нет',
                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back]])
                )
        else:
            await callback_query.message.answer(
                f'Не удалось получить список тикетов: {all_tic['error']}',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back]])
            )
    await callback_query.answer()