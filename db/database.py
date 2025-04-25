# db/database.py
import asyncpg
import logging
import json

logger = logging.getLogger(__name__)

# --- Новые функции работы с таблицей states ---

async def save_state_db(chat_id, state, db_pool, new_state_name=None):
    if new_state_name:
        prev = state.get("state")
        if prev and prev != new_state_name:
            state.setdefault("navigation_stack", []).append(prev)
        state["state"] = new_state_name

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO states (chat_id, state_data)
            VALUES ($1, $2)
            ON CONFLICT (chat_id) DO UPDATE SET state_data = $2
            """,
            chat_id, state
        )


async def load_state_db(chat_id, pool):
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT state_data FROM states WHERE chat_id = $1", chat_id)
            return json.loads(result) if result else {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке state из таблицы states: {e}", exc_info=True)
        return {}

async def create_db_pool():
    from data.constants import DB_CONFIG
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        logger.info("Пул подключений к БД успешно создан")
        return pool
    except Exception as e:
        logger.error("Ошибка при создании пула подключений", exc_info=True)
        raise

async def init_db(pool):
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    hero_name TEXT,
                    gender TEXT,
                    race TEXT,
                    class TEXT,
                    strength INTEGER,
                    dexterity INTEGER,
                    constitution INTEGER,
                    intelligence INTEGER,
                    wisdom INTEGER,
                    charisma INTEGER,
                    state JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS states (
                    chat_id BIGINT PRIMARY KEY
                )
            ''')
            # Проверка наличия колонки state_data — если нет, то добавим
            col_check = await conn.fetchval("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'states' AND column_name = 'state_data'
            """)
            if not col_check:
                await conn.execute("ALTER TABLE states ADD COLUMN state_data JSONB;")

            logger.info("Таблицы users и states инициализированы")
    except Exception as e:
        logger.error("Ошибка при инициализации таблиц: users/states", exc_info=True)
        raise

async def get_character(chat_id, pool):
    try:
        async with pool.acquire() as conn:
            character = await conn.fetchrow("SELECT * FROM users WHERE chat_id = $1", chat_id)
            return character
    except Exception as e:
        logger.error(f"Ошибка при получении персонажа: {e}", exc_info=True)
        return None

async def save_state(chat_id, state_dict, pool):
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET state = $1 WHERE chat_id = $2",
                json.dumps(state_dict), chat_id
            )
    except Exception as e:
        logger.error(f"Ошибка при сохранении состояния: {e}", exc_info=True)

async def load_state(chat_id, pool):
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT state FROM users WHERE chat_id = $1", chat_id)
            return json.loads(result) if result else {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке состояния: {e}", exc_info=True)
        return {}