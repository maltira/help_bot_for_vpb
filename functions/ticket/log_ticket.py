import os
import json
from datetime import datetime

def add_to_json(new_entry, ticket_id):
    filename = f"/home/enemybye/help_bot/tickets_log/ticket_{ticket_id}/ticket_{ticket_id}.json"
    try:
        # Открываем файл и загружаем данные
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []  # Если файла нет или он пустой, создаем пустой список

    # Добавляем новый элемент
    data.append(new_entry)

    # Записываем обратно в файл
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def log_ticket_message(ticket_id, message):
    # Создаём папку, если её нет
    os.makedirs("/home/enemybye/help_bot/tickets_log", exist_ok=True)
    os.makedirs(f"/home/enemybye/help_bot/tickets_log/ticket_{ticket_id}", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        'sender_id': message.from_user.id,
        'sent_to': timestamp,
        'text': message.text or '',
        'caption': message.caption or '',
        'photo': message.photo[-1].file_id if message.photo else '',
        'video': message.video.file_id if message.video else '',
        'document': message.document.file_id if message.document else '',
        'sticker': message.sticker.file_id if message.sticker else '',
    }

    add_to_json(data, ticket_id)
