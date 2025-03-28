import asyncio
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
        bt1 = InlineKeyboardButton(text='◀️ Назад', callback_data=f'goto-ticket_{ticket_id}')
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

# Обработчки сообщения от админа
@router.message(MessageState.waiting_for_admin)
async def wait_message(message: Message, state: FSMContext):
    data = await state.get_data()
    sender_id = data.get('sender_id')
    ticket_id = data.get('ticket_id')

    n = '0' * (5 - len(str(ticket_id))) + str(ticket_id)
    log_ticket_message(n, message)
    print(sender_id)
    await bot.send_message(
        chat_id=sender_id,
        text=message.text
    )

@router.message()
async def wait_message_user(message: Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()
    ticket = await db.get_ticket_by_uid(uid)
    print(listen_ticket)
    if ticket['status']:
        ticket = ticket['ticket']
        n = '0' * (5 - len(str(ticket['id']))) + str(ticket['id'])
        log_ticket_message(n, message) # логируем все сообщения пользователей с открытыми тикетами

        if ticket['id'] == listen_ticket: # админу отправляем только те сообщения, в чате тикета которого он сидит
            # TODO: ОТПРАВКА ФОТО И ВИДЕО
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=message.text
            )


# Обработчки сообщения закрытия тикета от админа
@router.message(lambda c: c.data.startswith('close_'))
async def close(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    bt1 = InlineKeyboardButton(text="Меню", callback_data='menu')
    res = await db.close_ticket(int(ticket_id))

    n = '0' * (5 - len(ticket_id)) + ticket_id
    if res['status']:
        await state.clear()
        global listen_ticket
        listen_ticket = None
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