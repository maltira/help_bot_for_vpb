from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import ADMIN_ID, db
from functions.ticket.log_ticket import log_ticket_message

router = Router()

class MessageState(StatesGroup):
    waiting_for_message = State()

# Обработчик колбека /create-ticket
@router.callback_query(lambda c: c.data == 'create-ticket')
async def create_ticket(callback_query: CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        bt1 = InlineKeyboardButton(text="◀️ Назад", callback_data='start')

        await callback_query.message.edit_text(
            f'<b>📄 Создание тикета</b>\n\nПеред созданием тикета обратись к разделу <b>FAQ (часто задаваемые вопросы)</b>, быть может, там уже есть ответ на твой вопрос!\n\n<i>Опиши проблему, с которой ты обращаешься:</i>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]]),
            parse_mode='HTML'
        )

        await state.set_state(MessageState.waiting_for_message)
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()

# Обработчки сообщения от пользователя (описание проблемы)
@router.message(MessageState.waiting_for_message)
async def process_promo_code(message: Message, state: FSMContext):
    uid = message.from_user.id
    bt1 = InlineKeyboardButton(text="◀️ Главное меню", callback_data='start')

    last_ticket = await db.get_last_ticket()
    if last_ticket['status'] and last_ticket['ticket'] is not None:
        free_id = last_ticket['ticket']['id'] + 1
    else: free_id = 1;
    n = '0' * (5 - len(str(free_id))) + str(free_id)

    res = await db.create_ticket(free_id, uid, message.text.strip())
    if res['status']:
        log_ticket_message(n, message)
        bt2 = InlineKeyboardButton(text="❌ Закрыть тикет", callback_data=f'close-ticket_{free_id}')
        # Создать файл
        await message.answer(
            f'📄 *Тикет №{n}*\n'
            f'```\n{message.text}\n```'
            'Ваше обращение успешно создано, в ближайшее время в этом чате с вами свяжется технический специалист!\n\n'
            'Если вы нашли решение проблемы — *закройте тикет*, чтобы не беспокоить поддержку\n\n'
            '_P.S. Рабочее время тех. поддержки 10:00 - 20:00 (МСК) 🕛_',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt2], [bt1]]),
            parse_mode='Markdown'
        )

    else:
        await message.answer(
            f'❌ *Тикет №{n}*\n'
            f'```\n{message.text}\n```'
            'Непредвиденная ошибка: не получилось создать обращение, такое случается редко, напиши администратору @sselanium\n\n',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]]),
            parse_mode='Markdown'
        )
    # Сбрасываем состояние
    await state.clear()