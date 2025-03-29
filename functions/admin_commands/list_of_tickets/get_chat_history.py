import json

from config import bot, ADMIN_ID, BOT_ID


async def get_chat_history(ticket_id):
    filename = f"help_bot/tickets_log/ticket_{ticket_id}/ticket_{ticket_id}.json"
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data: # конкретное сообщение
        tag = f'ADMIN\n🟢 {entry['sent_to']}\n\n' if str(entry['sender_id']) == ADMIN_ID or str(entry['sender_id']) == BOT_ID else f'[Пользователь](tg://user?id={entry['sender_id']})\n🟠 {entry['sent_to']}\n\n'
        if entry['photo'] != "":
            await bot.send_photo(ADMIN_ID, photo=entry['photo'], caption=tag + entry['caption'], parse_mode='Markdown')
        elif entry['video'] != "":
            await bot.send_video(ADMIN_ID, video=entry['video'], caption=tag + entry['caption'], parse_mode='Markdown')
        elif entry['document'] != "":
            await bot.send_document(ADMIN_ID, document=entry['document'], caption=tag + entry['caption'], parse_mode='Markdown')
        elif entry['sticker'] != "":
            await bot.send_sticker(ADMIN_ID, sticker=entry['sticker'])
        else:
            await bot.send_message(ADMIN_ID, text=tag + entry['text'], parse_mode='Markdown')


