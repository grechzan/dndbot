# registration.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from asyncpg.exceptions import UniqueViolationError
from data.constants import GENDERS
from db.database import save_state_db as save_state, load_state_db as load_state
from utils.helpers import is_valid_name, log_error
from utils.keyboards import add_back_button
from utils.stat_distribution import show_random_name, handle_random_name_choice

async def save_username(message, db_pool, state, bot):
    chat_id = message.chat.id
    username = message.text.strip()
    is_valid, error_msg = is_valid_name(username)
    if not is_valid:
        await bot.send_message(chat_id, f"⚠️ {error_msg} Попробуй другое имя.")
        return
    try:
        async with db_pool.acquire() as conn:
            existing = await conn.fetchval("SELECT 1 FROM users WHERE username = $1 AND chat_id != $2", username, chat_id)
            if existing:
                await bot.send_message(chat_id, f"⚠️ Имя '{username}' уже занято. Попробуй другое.")
                return
            await conn.execute(
                """
                INSERT INTO users (chat_id, username)
                VALUES ($1, $2)
                ON CONFLICT (chat_id) DO UPDATE SET username = EXCLUDED.username
                """,
                chat_id, username
            )
        await bot.send_message(chat_id, f"Прекрасно, {username}! Теперь введи имя своего героя.", reply_markup=ReplyKeyboardRemove())
        state["state"] = "awaiting_hero_name"
        state["username"] = username
        await save_state(chat_id, state, db_pool)
    except Exception as e:
        await log_error(chat_id, e, f"При сохранении username: {username}")
        await bot.send_message(chat_id, "⚠️ Ошибка! Попробуй снова.")


async def save_hero_name(message, db_pool, state, bot):
    chat_id = message.chat.id
    hero_name = message.text.strip()

    if hero_name.lower() in ["случайное имя", "🎲 случайное имя", "random", "random name"]:
        await show_random_name(chat_id, bot, {}, db_pool)
        return

    if hero_name.lower() in ["принять", "другое имя", "назад"]:
        await handle_random_name_choice(message, {}, bot, db_pool)
        return

    is_valid, error_msg = is_valid_name(hero_name)
    if not is_valid:
        await bot.send_message(chat_id, f"⚠️ {error_msg}\nПопробуй другое имя.")
        return

    state["hero_name"] = hero_name
    state["state"] = "awaiting_gender"
    await save_state(chat_id, state, db_pool)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for gender in GENDERS:
        markup.add(KeyboardButton(gender))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, f"Имя героя '{hero_name}' записано! Теперь выбери пол персонажа.", reply_markup=markup)


async def save_gender(message, state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()

    if text not in GENDERS:
        await bot.send_message(chat_id, "Пожалуйста, выбери пол из предложенных вариантов.")
        return

    state["gender"] = text
    state["state"] = "awaiting_race_selection"
    await save_state(chat_id, state, db_pool)

    from states.manual_creation import show_race_selection
    await show_race_selection(chat_id, bot, db_pool)
