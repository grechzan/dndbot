# main.py (упрощённый)
import asyncio
from telebot.async_telebot import AsyncTeleBot
from data.constants import TOKEN
from db.database import create_db_pool, init_db, get_character, save_state_db as save_state, load_state_db as load_state
from utils.display import show_character_card
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from router import handle_state
from utils.stat_distribution import prompt_hero_name

bot = AsyncTeleBot(TOKEN)
db_pool = None
# user_states больше не используется — заменено на хранение в БД


async def show_main_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Показать персонажа"), KeyboardButton("Играть"))
    await bot.send_message(chat_id, "Ты в главном меню, что желаешь?", reply_markup=markup)


@bot.message_handler(commands=['start'])
async def start(message):
    chat_id = message.chat.id
    character = await get_character(chat_id, db_pool)
    state_from_db = await load_state(chat_id, db_pool)

    if character:
        if character.get("class") and character.get("race"):
            await bot.send_message(chat_id, "С возвращением, странник!")
            await save_state(chat_id, {"state": "main_menu"}, db_pool)
            await show_main_menu(chat_id)
        elif state_from_db and state_from_db.get("state"):
            # состояние загружается напрямую из БД — ничего не нужно сохранять
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("Продолжить создание персонажа"))
            markup.add(KeyboardButton("Начать заново"))
            await bot.send_message(chat_id, "Ты не завершил создание персонажа. Хочешь продолжить?", reply_markup=markup)
            state_from_db["state"] = "awaiting_continue_choice"
            await save_state(chat_id, state_from_db, db_pool)
        else:
            await bot.send_message(chat_id, "У тебя уже есть аккаунт. Хочешь создать нового персонажа?")
            await prompt_hero_name(chat_id, bot, db_pool)
    else:
        await bot.send_message(chat_id, "Приветствую, путник! Готов погрузиться в захватывающий мир Подземелий и Драконов? Введи имя аккаунта, чтобы начать.")
        await save_state(chat_id, {"state": "awaiting_username"}, db_pool)


@bot.message_handler(commands=['help'])
async def handle_help_command(message):
    from help import show_help_menu
    await show_help_menu(bot, message.chat.id)


@bot.message_handler(commands=['donate'])
async def handle_donate_command(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("PayPal"), KeyboardButton("Сбербанк"), KeyboardButton("Крипта"))
    await bot.send_message(message.chat.id, "Хотите поддержать разработчика? Благодарим! Пожалуйста выберите метод оплаты:", reply_markup=markup)


@bot.message_handler(commands=['username'])
async def handle_change_username(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введи новое имя аккаунта:")
    await save_state(chat_id, {"state": "changing_username"}, db_pool)


@bot.message_handler(commands=['hero'])
async def hero_command(message):
    from states.entry import handle_hero_command
    await handle_hero_command(message, db_pool, bot)


@bot.message_handler(func=lambda m: True)
async def route(message):
    chat_id = message.chat.id
    state_dict = await load_state(chat_id, db_pool)
    state = state_dict.get("state") if state_dict else None
    await handle_state(message, state, bot, db_pool)


async def main():
    global db_pool
    db_pool = await create_db_pool()
    await init_db(db_pool)
    from states.entry import setup_bot_commands
    from telebot.types import BotCommand
    await bot.set_my_commands([
        BotCommand("/help", "Помощь новичкам/техническая"),
        BotCommand("/start", "Начать/Главное меню"),
        BotCommand("/hero", "Показать карточку персонажа"),
        BotCommand("/username", "Сменить имя аккаунта"),
        BotCommand("/donate", "Поддержать разработчика")
    ])
    await bot.infinity_polling()


if __name__ == '__main__':
    asyncio.run(main())