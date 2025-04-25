# states/entry.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from db.database import save_state, get_character
from utils.display import show_character_card

async def handle_continue_choice(message, user_states, bot, db_pool):
    text = message.text.strip().lower()
    chat_id = message.chat.id

    if "продолжить" in text:
        await bot.send_message(chat_id, "Продолжаем с того места, где ты остановился.")
        from router import handle_state
        current_state = user_states.get(chat_id, {}).get("state")
        await handle_state(message, current_state, user_states, bot, db_pool)

    elif "заново" in text or "нового" in text:
        user_states[chat_id] = {"state": "awaiting_hero_name"}
        await bot.send_message(chat_id, "Давай создадим нового персонажа. Введи имя героя:")
        await save_state(chat_id, user_states[chat_id], db_pool)

    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Продолжить создание персонажа"))
        markup.add(KeyboardButton("Начать заново"))
        await bot.send_message(chat_id, "Пожалуйста, выбери вариант из предложенного списка:", reply_markup=markup)


# Команды меню Telegram
async def setup_bot_commands(bot):
    await bot.set_my_commands([
        BotCommand("/start", "Начать заново"),
        BotCommand("/menu", "Вернуться в главное меню"),
        BotCommand("/hero", "Показать карточку персонажа")
    ])


# Обработчик команды /menu
async def handle_menu_command(message, user_states, bot, db_pool):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Показать персонажа"), KeyboardButton("Играть"))
    await bot.send_message(chat_id, "Ты в главном меню, что желаешь?", reply_markup=markup)


# Обработчик команды /hero
async def handle_hero_command(message, db_pool, bot):
    chat_id = message.chat.id
    character = await get_character(chat_id, db_pool)
    if character:
        await show_character_card(chat_id, bot, db_pool)
    else:
        await bot.send_message(chat_id, "Персонаж не найден. Попробуй /start или создай нового.")
