# manual_creation.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from data.constants import CLASSES, GENDERS
from db.database import get_character, save_state_db as save_state, load_state_db as load_state
from utils.helpers import log_error, send_race_card
from utils.keyboards import add_back_button

RACE_IMAGES = [
    "Человек", "Эльф", "Полурослик", "Полуорк", "Тифлинг",
    "Полуэльф", "Гном", "Дварф", "Драконорожденный"
]

ELF_SUBRACES = ["Лесной эльф", "Высший эльф", "Темный эльф"]

async def show_gender_selection(chat_id, bot, db_pool):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for gender in GENDERS:
        markup.add(KeyboardButton(gender))
    markup = add_back_button(markup)
    await bot.send_message(chat_id, "Выбери пол персонажа:", reply_markup=markup)

    state = await load_state(chat_id, db_pool) or {}
    state["state"] = "awaiting_gender"
    await save_state(chat_id, state, db_pool)

async def show_race_selection(chat_id, bot, db_pool):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for race in RACE_IMAGES:
        markup.add(KeyboardButton(race))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, "Выбери расу для своего персонажа:", reply_markup=markup)

    state = await load_state(chat_id, db_pool) or {}
    state["state"] = "awaiting_race_selection"
    await save_state(chat_id, state, db_pool)

async def handle_race_choice(message, user_state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()

    if text not in RACE_IMAGES:
        await bot.send_message(chat_id, "Пожалуйста, выбери расу из предложенного списка.")
        return

    state = await load_state(chat_id, db_pool) or {}
    state["race"] = text

    if text == "Эльф":
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for subrace in ELF_SUBRACES:
            markup.add(KeyboardButton(subrace))
        markup = add_back_button(markup)

        await bot.send_message(chat_id, "Выбери подрасу эльфа:", reply_markup=markup)
        state["state"] = "awaiting_elf_subrace_selection"
    else:
        await show_class_selection(chat_id, bot, db_pool)
        state["state"] = "awaiting_class_selection"

    await save_state(chat_id, state, db_pool)

async def handle_elf_subrace_choice(message, user_state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()

    if text not in ELF_SUBRACES:
        await bot.send_message(chat_id, "Пожалуйста, выбери подрасу из списка.")
        return

    state = await load_state(chat_id, db_pool) or {}
    state["race"] = text  # подставляем подрасу вместо общей расы
    state["state"] = "awaiting_class_selection"
    await save_state(chat_id, state, db_pool)

    await show_class_selection(chat_id, bot, db_pool)

async def show_class_selection(chat_id, bot, db_pool):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for cls in CLASSES:
        markup.add(KeyboardButton(cls))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, "Теперь выбери класс:", reply_markup=markup)

    state = await load_state(chat_id, db_pool) or {}
    state["state"] = "awaiting_class_selection"
    await save_state(chat_id, state, db_pool)

async def handle_class_choice(message, user_state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()

    if text not in CLASSES:
        await bot.send_message(chat_id, "Пожалуйста, выбери класс из предложенного списка.")
        return

    state = await load_state(chat_id, db_pool) or {}
    state["class"] = text
    state["state"] = "awaiting_stat_distribution_method"
    await save_state(chat_id, state, db_pool)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Стандартно"), KeyboardButton("Самостоятельно"))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, "Теперь распределим характеристики. Выбери способ:", reply_markup=markup)
