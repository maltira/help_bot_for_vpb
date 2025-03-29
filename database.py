import json
import os
import redis.asyncio as redis
import asyncpg
from dotenv import load_dotenv
from logs.logger import logger
from datetime import datetime, timezone

load_dotenv()
DB = os.getenv('DB')
DB_NAME = os.getenv('DB_NAME')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
RDS_PASS = os.getenv('RDS_PASS')
RDS_ADDRESS=os.getenv('RDS_ADDRESS')
RDS_PORT = os.getenv('RDS_PORT')

rds = redis.Redis(
    host=RDS_ADDRESS,
    port=int(RDS_PORT),
    db=1,
    password=RDS_PASS,
    decode_responses=True
)

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
        try:
            mode = await rds.get('mode')
            if mode:
                logger.info(f"Получен статус бота из redis: {mode}")
                return {'status': True, 'mode': mode}
        except Exception as err:
            logger.error(f"Не удалось получить статус бота из redis: {err}")

        async with self.pool.acquire() as conn:
            try:
                res = await conn.fetchrow("SELECT * FROM settings WHERE id=1")
                if res:
                    logger.warning(f"Статус бота найден в БД: {res['mode']}")
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

                try:
                    await rds.set('mode', mode)
                    logger.info(f"Установлен новый статус redis: {mode}")
                except Exception as e:
                    logger.error(f"Ошибка при установке статуса в Redis: {e}")

                logger.info(f"Установлен новый статус бота в БД: {mode}")
                return {'status': True}

            except Exception as err:
                logger.error(f"Не удалось установить статус бота ({mode}): {err}")
                return {'status': False, 'error': err}



    # Получить тикет по id пользователя
    async def get_ticket(self, uid):
        try:
            rd_data = await rds.get(str(uid))
            if rd_data is not None:
                data = json.loads(rd_data) # какая-то невменяемая пробелма с тем, что оно выводит это даже после того как я удалил его
                return {'status': True, 'ticket': data}
        except Exception as err:
            logger.error(f"Не удалось получить тикет из redis: {err}")

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
                    try:
                        data = {
                            'id': res['id'],
                            'sender_id': res['sender_id'],
                            'status': 'open',
                            'created_at': now_date.isoformat(), # получать datetime.fromisoformat(data["created_at"])
                            'message': message
                        }
                        await rds.set(str(sender), json.dumps(data))
                    except Exception as e:
                        logger.error(f"Ошибка при вставке тикета {res['id']} в Redis: {e}")
                    return {'status': True, 'id': res['id']}
                else:
                    return {'status': False, 'error': 'duplicate'}
            except Exception as err:
                logger.error(f"Не удалось cоздать тикет: {err}")
                return {'status': False, 'error': err}



    # Закрыть тикет
    async def close_ticket(self, uid, ticket_id):
        try:
            res = await rds.get(str(uid))
            await rds.delete(str(uid))
            res = await rds.get(str(uid))
        except Exception as err:
            logger.error(f'Не удалось удалить {uid} из redis: {err}')

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
    async def get_tickets(self, status, sender_id=0):
        async with self.pool.acquire() as conn:
            try:
                if sender_id == 0:
                    res = await conn.fetch('SELECT * FROM tickets WHERE status=$1', status)
                else:
                    res = await conn.fetchrow('SELECT * FROM tickets WHERE sender_id=$1 AND status=$2', sender_id, status)
                return {'status': True, 'list': res}
            except Exception as err:
                logger.error(f"Не удалось получить список открытых тикетов: {err}")
                return {'status': False, 'error': err}



    # Получить все закрытые тикеты
    async def get_closed_tickets(self):
        async with self.pool.acquire() as conn:
            try:
                res = await conn.fetch('SELECT * FROM tickets WHERE status=$1', 'сlosed')
                return {'status': True, 'list': res}
            except Exception as err:
                logger.error(f"Не удалось получить список закрытых тикетов: {err}")
                return {'status': False, 'error': err}


    async def close(self):
        await self.pool.close()