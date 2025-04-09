import asyncio
from datetime import datetime, timezone
from logs.logger import clean_logs
from logs.ticket_logger import clean_tickets


async def daily_check():
    while True:
        today = datetime.now(timezone.utc)

        # Очищаем логи, если их больше max_lines
        clean_logs(25000)
        await clean_tickets(today)

        # Ждём 3 часа перед следующей проверкой
        await asyncio.sleep(3600*6)