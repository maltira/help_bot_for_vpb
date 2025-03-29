import os
import json
from datetime import datetime

def add_to_json(new_entry, ticket_id):
    try:
        # Открываем файл и загружаем данные
        with open(f"/root/help_bot/tickets_log/ticket_{ticket_id}/ticket_{ticket_id}.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []  # Если файла нет или он пустой, создаем пустой список

    # Добавляем новый элемент
    data.append(new_entry)

    # Записываем обратно в файл
    with open(f"/root/help_bot/tickets_log/ticket_{ticket_id}/ticket_{ticket_id}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def log_ticket_message(ticket_id, message):
    # Записывает сообщение в файл тикета
    filename = f"/root/help_bot/tickets_log/ticket_{ticket_id}/ticket_{ticket_id}.txt"

    # Создаём папку, если её нет
    os.makedirs("/root/help_bot/tickets_log", exist_ok=True)
    os.makedirs(f"/root/help_bot/tickets_log/ticket_{ticket_id}", exist_ok=True)

    # Записываем сообщение в файл
    with open(filename, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {message.from_user.id} ({message.from_user.username}) : {message.text}\n")

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
