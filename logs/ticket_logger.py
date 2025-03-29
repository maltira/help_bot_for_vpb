import os

from asyncpg.pgproto.pgproto import timedelta

from config import db
from logs.logger import logger


async def clean_tickets(today):
    res = await db.get_tickets('closed')
    count = 0
    if res['status']:
        res = res['list']
        if res:
            for ticket in res:
                if ticket['closed_at'] < today - timedelta(days=30):
                    filename = f"help_bot/tickets_log/ticket_{ticket['id']}/ticket_{ticket['id']}.json"
                    path = f"help_bot/tickets_log/ticket_{ticket['id']}"
                    logger.info(ticket['closed_at'])

                    try:
                        os.remove(filename)  # Удаляет файл
                        os.rmdir(path)  # Удаляет только пустую папку
                        count += 1
                    except Exception as err:
                        logger.info(f"Ошибка удаления тикета №{ticket['id']}: {err}")

            if count > 0:
                logger.info(f"Удалены {count} тикетов")
