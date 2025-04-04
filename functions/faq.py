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
            '2️⃣ <b>Есть ли какие-то ограничения по скорости или трафику?</b>\n'
            'Мы предоставляем стабильное и быстрое соединение без ограничений'
            '3️⃣ <b>Зачем мне платить, если в интернете есть бесплатные VPN?</b>\n'
            'Бесплатные VPN могут ограничивать скорость интернета и не всегда работают, что уж говорить о том, что они могут собирать и перепродавать ваши личные '
            'данные, не заботясь об анонимности и безопасности'
            '4️⃣ <b>А безопасно ли использовать ваш VPN?</b>\n'
            'Да, использование нашего VPN абсолютно безопасно. Мы придерживаемся строгой политики безопасности и конфиденциальности.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[bt1]]),
            parse_mode='HTML'
        )
    else:
        await callback_query.message.answer('🔄️ Сервис находится на технических работах, скоро всё придёт в норму')
    await callback_query.answer()