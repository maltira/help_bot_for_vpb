import os
from datetime import datetime, timezone

import asyncpg
from dotenv import load_dotenv
from logs.logger import logger

load_dotenv()
DB = os.getenv('DB')
DB_NAME = os.getenv('DB_NAME')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


class Database:
    def __init__(self):
        self.pool = None



    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                database=DB,
                user=DB_NAME,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT
            )
        except asyncpg.PostgresError as err:
            logger.critical(f"Не удалось подключиться к БД: {err}")
            return {'status': False, 'error': err}



    # Получить статус бота
    async def get_bot_mode(self):


        async with self.pool.acquire() as conn:
            try:
                res = await conn.fetchrow("SELECT * FROM settings WHERE id=1")
                if res:
                    return {'status': True, 'mode': res['mode']}
                else:
                    logger.warning("Статус бота не найден в БД")
                    return {'status': False}

            except asyncpg.PostgresError as err:
                logger.error(f"Не удалось получить статус бота: {err}")
                return {'status': False, 'error': err}



    # Установить статус бота
    async def set_bot_mode(self, mode):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("UPDATE settings SET mode=$1 WHERE id=1", mode)


                logger.info(f"Установлен новый статус бота в БД: {mode}")
                return {'status': True}

            except Exception as err:
                logger.error(f"Не удалось установить статус бота ({mode}): {err}")
                return {'status': False, 'error': err}



    # Получить тикет по id
    async def get_ticket(self, ticket_id):
        async with self.pool.acquire() as conn:
            try:
                t = await conn.fetchrow("SELECT * FROM tickets WHERE id=$1", ticket_id)
                return {'status': True, 'ticket': t}
            except Exception as err:
                logger.error(f"Не удалось получить последний тикет: {err}")
                return {'status': False, 'error': err}



    # Получить тикет по id пользователя
    async def get_ticket_by_uid(self, uid):
        async with self.pool.acquire() as conn:
            try:
                t = await conn.fetchrow("SELECT * FROM tickets WHERE sender_id=$1 AND status=$2", uid, 'open')
                return {'status': True, 'ticket': t}
            except Exception as err:
                logger.error(f"Не удалось получить последний тикет: {err}")
                return {'status': False, 'error': err}


    # Создать тикет
    async def create_ticket(self, sender, message):
        async with self.pool.acquire() as conn:
            try:
                now_date = datetime.now(timezone.utc)
                res = await conn.fetchrow('SELECT * FROM tickets WHERE sender_id=$1 AND status=$2', sender, 'open')
                if not res:
                    r = await conn.execute("INSERT INTO tickets (sender_id, status, created_at, closed_at, message) VALUES ($1,$2,$3,$4,$5)",
                                        sender, 'open', now_date, None, message)
                    res = await conn.fetchrow('SELECT * FROM tickets WHERE sender_id=$1 AND status=$2', sender, 'open')
                    logger.info(f"Тикет создан пользователем {sender}")
                    return {'status': True, 'id': res['id']}
                else:
                    return {'status': False, 'error': 'duplicate'}
            except Exception as err:
                logger.error(f"Не удалось cоздать тикет: {err}")
                return {'status': False, 'error': err}



    # Закрыть тикет
    async def close_ticket(self, ticket_id):
        async with self.pool.acquire() as conn:
            try:
                now_date = datetime.now(timezone.utc)
                await conn.execute("UPDATE tickets SET status=$1, closed_at=$2 WHERE id=$3", 'closed', now_date, ticket_id)
                logger.info(f"Тикет №{ticket_id} закрыт")
                return {'status': True}
            except Exception as err:
                logger.error(f"Не удалось закрыть тикет ({ticket_id}): {err}")
                return {'status': False, 'error': err}



    # Получить все открытые тикеты
    async def get_open_ticket(self):
        async with self.pool.acquire() as conn:
            try:
                res = await conn.fetch('SELECT * FROM tickets WHERE status=$1', 'open')

                return {'status': True, 'list': res}
            except Exception as err:
                logger.error(f"Не удалось получить список тикетов: {err}")
                return {'status': False, 'error': err}



    async def close(self):
        await self.pool.close()