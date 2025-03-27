from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_ID, db

router = Router()

# Обработчик колбека /faq
@router.callback_query(lambda c: c.data == 'faq')
async def faq_call(callback_query: CallbackQuery):
    uid = callback_query.from_user.id
    access = await db.get_bot_mode()
    if access['mode'] == 'activate' or str(uid) == ADMIN_ID:
        bt1 = InlineKeyboardButton(text="◀️ Назад", callback_data='start')

        await callback_query.message.edit_text(
            'Здесь ты можешь найти ответы на следующие частые вопросы:\n\n'
            '1️⃣ <b>Как подключиться к ВПН?</b>\n'
            'Чтобы получить доступ к VPN-сервисам, необходимо приобрести доступ у @cubeevpnbot, после чего перейти'
            'в раздел «Настроить VPN» -> «Моя подписка» -> «Инструкция»\n\n'
            '2️⃣ <b>Как подключиться к ВПН?</b>\n'
            'Чтобы получить доступ к VPN-сервисам, необходимо приобрести доступ у @cubeevpnbot, после чего перейти'
            'в раздел «Настроить VPN» -> «Моя подписка» -> «Инструкция»\n\n'
            '3️⃣ <b>Как подключиться к ВПН?</b>\n'
            'Чтобы получить доступ к VPN-сервисам, необходимо приобрести доступ у @cubeevpnbot, после чего перейти'
            'в раздел «Настроить VPN» -> «Моя подписка» -> «Инструкция»\n\n',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]]),
            parse_mode='HTML'
        )
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()