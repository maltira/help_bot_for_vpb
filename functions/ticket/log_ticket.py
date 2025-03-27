import os
from datetime import datetime

def log_ticket_message(ticket_id, message):
    # Записывает сообщение в файл тикета
    filename = f"tickets_log/ticket_{ticket_id}.txt"

    # Создаём папку, если её нет
    os.makedirs("tickets_log", exist_ok=True)

    # Записываем сообщение в файл
    with open(filename, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {message.from_user.id} ({message.from_user.username}) : {message.text}\n")
