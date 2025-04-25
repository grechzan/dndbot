# router.py
from states.registration import save_username, save_hero_name, save_gender
from states.test import start_character_test, handle_test_answer
from states.manual_creation import (
    handle_race_choice, handle_elf_subrace_choice, handle_class_choice, show_race_selection
)
from utils.stat_distribution import handle_stat_distribution_method
from utils.stat_distribution import (
    handle_custom_distribution,
    start_custom_distribution,
    start_standard_distribution,
    handle_stat_assignment
)
from db.database import get_character, save_state
from utils.display import show_character_card
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from help import handle_help_response
from db.database import load_state_db as load_state, save_state_db as save_state
from utils.helpers import go_back

async def handle_state(message, current_state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()
    state = await load_state(chat_id, db_pool) or {}

    handlers = {
        "awaiting_username": lambda: save_username(message, db_pool, state, bot),
        "awaiting_hero_name": lambda: save_hero_name(message, db_pool, state, bot),
        "awaiting_gender": lambda: save_gender(message, state, bot, db_pool),
        "taking_test": lambda: handle_test_answer(message, bot, db_pool),
        "awaiting_race_selection": lambda: handle_race_choice(message, state, bot, db_pool),
        "awaiting_elf_subrace_selection": lambda: handle_elf_subrace_choice(message, state, bot, db_pool),
        "awaiting_class_selection": lambda: handle_class_choice(message, state, bot, db_pool),
        "awaiting_stat_distribution_method": lambda: handle_stat_distribution_method(message, state, bot, db_pool),
        "assign_stat_value": lambda: handle_stat_assignment(message, state, bot, db_pool),
        "changing_username": lambda: save_username(message, db_pool, state, bot)
    }

    if text.lower() == "пройти тест заново":
        await start_character_test(chat_id, state, bot, db_pool)
        await save_state(chat_id, state, db_pool)
        return

    if text.lower() == "назад":
        new_state = await go_back(chat_id, db_pool)
        if new_state:
            await handle_state(message, new_state.get("state"), bot, db_pool)
            return

    if current_state == "awaiting_continue_choice":
        from states.entry import handle_continue_choice
        await handle_continue_choice(message, state, bot, db_pool)
        return

    if current_state in handlers:
        await handlers[current_state]()
    else:
        await bot.send_message(chat_id, "Я тебя не понял. Используй /start, чтобы начать сначала.")
