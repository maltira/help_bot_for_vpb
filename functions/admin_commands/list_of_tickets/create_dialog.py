import asyncio
from datetime import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMIN_ID, bot, db
from functions.ticket.log_ticket import log_ticket_message

router = Router()

class MessageState(StatesGroup):
    waiting_for_admin = State()

listen_ticket = None

# Будем ловить все сообщения от пользователя
@router.callback_query(lambda c: c.data.startswith('create-dialog_'))
async def all_tickets(callback_query: CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id

    if str(uid) == ADMIN_ID:
        ticket_id = int(callback_query.data.split('_')[1])
        sender_id = int(callback_query.data.split('_')[2])
        bt1 = InlineKeyboardButton(text='◀️ Назад', callback_data=f'goto_{ticket_id}_{sender_id}')
        bt2 = InlineKeyboardButton(text="Закрыть тикет", callback_data=f'close_{ticket_id}')

        await callback_query.message.edit_text(
            f'*Вы перешли в диалог ТИКЕТА №{ticket_id}*\n\n'
            f'Напишите что-то, в ответ будут приходить сообщения пользователя: ',
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt2], [bt1]])
        )
        global listen_ticket
        listen_ticket = ticket_id
        await state.update_data(sender_id=sender_id, ticket_id=ticket_id)
        await state.set_state(MessageState.waiting_for_admin)
    await callback_query.answer()


# Обработчик сообщения от админа
@router.message(MessageState.waiting_for_admin)
async def wait_message(message: Message, state: FSMContext):
    data = await state.get_data()
    sender_id = data.get('sender_id')
    ticket_id = data.get('ticket_id')

    n = '0' * (5 - len(str(ticket_id))) + str(ticket_id)
    log_ticket_message(n, message)

    if message.photo:
        await bot.send_photo(sender_id, message.photo[-1].file_id, caption=message.caption or '')
    elif message.video:
        await bot.send_video(sender_id, message.video.file_id, caption=message.caption or '')
    elif message.document:
        await bot.send_document(sender_id, message.document.file_id, caption=message.caption or '')
    elif message.sticker:
        await bot.send_sticker(sender_id, message.sticker.file_id)
    else:
        await bot.send_message(chat_id=sender_id, text=message.text)



# Ловим сообщения от пользователей
@router.message(lambda c: not c.text.startswith('/'))
async def wait_message_user(message: Message):
    uid = message.from_user.id
    ticket = await db.get_ticket(uid)
    if ticket['status'] and ticket['ticket']:
        ticket = ticket['ticket']
        n = '0' * (5 - len(str(ticket['id']))) + str(ticket['id'])
        log_ticket_message(n, message) # логируем все сообщения пользователей с открытыми тикетами
        if ticket['id'] == listen_ticket: # админу отправляем только те сообщения, в чате тикета которого он сидит
            if message.photo:
                await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=message.caption or '')
            elif message.video:
                await bot.send_video(ADMIN_ID, message.video.file_id, caption=message.caption or '')
            elif message.document:
                await bot.send_document(ADMIN_ID, message.document.file_id, caption=message.caption or '')
            elif message.sticker:
                await bot.send_sticker(ADMIN_ID, message.sticker.file_id)
            else:
                await bot.send_message(ADMIN_ID, message.text)


# Обработчки сообщения закрытия тикета от админа
@router.callback_query(lambda c: c.data.startswith('close_'))
async def close(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    sender_id = data.get('sender_id')
    bt1 = InlineKeyboardButton(text="Меню", callback_data='menu')
    res = await db.close_ticket(sender_id, int(ticket_id))

    n = '0' * (5 - len(str(ticket_id))) + str(ticket_id)
    if res['status']:
        await state.clear()
        global listen_ticket
        listen_ticket = None
        await bot.send_message(
            chat_id=sender_id,
            text=f'Ваш тикет №{n} был закрыт администратором',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Главное меню', callback_data='start')]])
        )
        res = await callback_query.message.edit_text(
            f'✅ *Тикет №{n}*\n'
            'Вы успешно закрыли тикет',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]]),
            parse_mode='Markdown'
        )
        log_ticket_message(n, res)
    else:
        bt2 = InlineKeyboardButton(text="❌ Закрыть тикет", callback_data=f'close_{ticket_id}')
        await callback_query.message.edit_text(
            'Не удалось закрыть тикет по непредвиденной ошибке',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1], [bt2]]),
            parse_mode='Markdown'
        )

    await callback_query.answer()

# Обработчик сообщения кнопки НАЗАД от админа
@router.callback_query(lambda c: c.data.startswith('goto_'))
async def close(callback_query: CallbackQuery, state: FSMContext):
    ticket_id = int(callback_query.data.split('_')[1])
    sender_id = int(callback_query.data.split('_')[2])
    bt1 = InlineKeyboardButton(text='◀️ Назад', callback_data='list-tickets')
    bt2 = InlineKeyboardButton(text="Закрыть тикет", callback_data=f'close-ticket_{ticket_id}')
    n = '0' * (5 - len(str(ticket_id))) + str(ticket_id)
    ticket = await db.get_ticket(int(sender_id))

    if ticket['status']:
        await state.clear()
        global listen_ticket
        listen_ticket = None

        ticket = ticket['ticket']
        if ticket is not None:
            bt3 = InlineKeyboardButton(text="Начать диалог",
                                       callback_data=f'create-dialog_{ticket_id}_{ticket['sender_id']}')
            await callback_query.message.edit_text(
                f'*Тикет №{n}*\n'
                f'```\n{ticket['message']}\n```'
                f'От пользователя: {ticket['sender_id']} [ссылка](tg://user?id={ticket['sender_id']})\n\n'
                f'🟢 Статус: {ticket['status']}\n\n'
                f'📅 Дата создания: {datetime.fromisoformat(ticket['created_at'])}',
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt3], [bt2], [bt1]])
            )
        else:
            await callback_query.message.edit_text(
                f'Не удалось получить тикет',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]])
            )
    else:
        await callback_query.message.edit_text(
            f'Не удалось получить тикет: {ticket['error']}',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]])
        )

    await callback_query.answer()