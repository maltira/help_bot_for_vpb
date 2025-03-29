from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import db, ADMIN_ID

router = Router()

@router.callback_query(lambda c: c.data == 'my-tickets')
async def my_tickets(callback_query: CallbackQuery):
    uid = callback_query.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        data = await db.get_open_ticket(uid)
        buttons = []
        if data['status']:
            data = data['list']
            if data:
                icon = '✅ ' if data['status'] == 'closed' else ''
                buttons.append([InlineKeyboardButton(text=icon + f'Тикет №{data['id']}', callback_data=f'show-ticket_{data['id']}')])
                buttons.append([InlineKeyboardButton(text='◀️ Назад', callback_data='start')])
                await callback_query.message.edit_text(
                    f'Здесь отображаются все твои *активные тикеты:*',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                    parse_mode='Markdown'
                )
            else:
                buttons.append([InlineKeyboardButton(text='◀️ Назад', callback_data='start')])
                await callback_query.message.edit_text(
                    'Пока что ты не создал ни единого тикета ⚡',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                )
        else:
            buttons.append([InlineKeyboardButton(text='◀️ Назад', callback_data='start')])
            await callback_query.message.edit_text(
                '❌ Непредвиденная ошибка при получении списка тикетов, если проблема повторяется, напиши специалисту @sselanium',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            )
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('show-ticket_'))
async def show_ticket(callback_query: CallbackQuery):
    ticket_id = callback_query.data.split('_')[1]
    uid = callback_query.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        data = await db.get_ticket(uid)
        if data['status']:
            data = data['ticket']
            if data is not None:
                buttons = [[InlineKeyboardButton(text='Закрыть тикет', callback_data=f'close-ticket_{ticket_id}')],
                           [InlineKeyboardButton(text='◀️ Назад', callback_data='my-tickets')]]
                await callback_query.message.edit_text(
                    f'*Тикет №{data['id']}*\n'
                    f'```\n{data['message']}\n```\n'
                    f'🟢 Статус: *{data['status']}*',
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )
            else:
                buttons = [[InlineKeyboardButton(text='◀️ Назад', callback_data='my-tickets')]]
                await callback_query.message.edit_text(
                    f'Не удалось получить данные по тикету',
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )
        else:
            buttons = [[InlineKeyboardButton(text='◀️ Назад', callback_data='start')]]
            await callback_query.message.edit_text(
                '❌ Непредвиденная ошибка при получении списка тикетов, если проблема повторяется, напиши специалисту @sselanium',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            )
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()