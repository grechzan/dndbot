# stat_distribution.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from db.database import get_character, save_state_db as save_state, load_state_db as load_state
from utils.helpers import send_race_card
from utils.keyboards import add_back_button
import random
from data.constants import RACE_BONUSES, CLASS_BONUSES
from data.names import RANDOM_NAMES

STAT_LABELS = {
    "Сила": "str",
    "Ловкость": "dex",
    "Выносливость": "con",
    "Интеллект": "int",
    "Мудрость": "wis",
    "Харизма": "cha"
}

STAT_NAMES_REVERSE = {
    "str": "Сила",
    "dex": "Ловкость",
    "con": "Выносливость",
    "int": "Интеллект",
    "wis": "Мудрость",
    "cha": "Харизма"
}

# 🎲 Показываем случайное имя
async def show_random_name(chat_id, bot, user_states, db_pool):
    name = random.choice(RANDOM_NAMES)
    state = await load_state(chat_id, db_pool) or {}
    state["hero_name"] = name
    state["state"] = "confirm_random_name"
    await save_state(chat_id, state, db_pool)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Принять"))
    markup.add(KeyboardButton("Другое имя"))
    markup.add(KeyboardButton("Назад"))
    await bot.send_message(chat_id, f"Твое случайное имя: {name} Хочешь оставить его?", reply_markup=markup)

# 📦 Обработка выбора случайного имени
async def handle_random_name_choice(message, user_states, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    state = await load_state(chat_id, db_pool) or {}

    if text == "принять":
        state["state"] = "awaiting_gender"
        await save_state(chat_id, state, db_pool)

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Мужчина"), KeyboardButton("Женщина"))
        markup = add_back_button(markup)
        await bot.send_message(chat_id, "Выбери пол своего персонажа:", reply_markup=markup)

    elif text == "другое имя":
        await show_random_name(chat_id, bot, user_states, db_pool)

    elif text == "назад":
        await prompt_hero_name(chat_id, bot, db_pool)

    else:
        await bot.send_message(chat_id, "Пожалуйста, выбери один из предложенных вариантов.")

# 🔤 Запрос имени героя
async def prompt_hero_name(chat_id, bot, db_pool):
    state = await load_state(chat_id, db_pool) or {}
    state["state"] = "awaiting_hero_name"
    await save_state(chat_id, state, db_pool)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🎲 Случайное имя"))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, "Введи имя своего персонажа или выбери \"Случайное имя\":", reply_markup=markup)

# 🧱 Выбор способа распределения
async def handle_stat_distribution_method(message, state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip().lower()

    if text == "стандартно":
        await start_standard_distribution(chat_id, state, bot, db_pool)
    elif text == "самостоятельно":
        await start_custom_distribution(chat_id, state, bot, db_pool)
    else:
        await bot.send_message(chat_id, "Пожалуйста, выбери 'Стандартно' или 'Самостоятельно' с кнопки.")

# 🧱 Стандартное распределение (фиксированные значения)
async def start_standard_distribution(chat_id, state, bot, db_pool):
    state.update({
        "state": "assign_stat_value",
        "available_values": [15, 14, 13, 12, 10, 8],
        "assigned_stats": {},
        "available_stats": list(STAT_LABELS.keys())
    })
    await save_state(chat_id, state, db_pool)

    value = state["available_values"][0]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for stat in state["available_stats"]:
        markup.add(KeyboardButton(stat))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, f"Какую характеристику назначить значению {value}?", reply_markup=markup)

# 📦 Обработка одного шага стандартного распределения
async def handle_stat_assignment(message, state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()

    if text not in state["available_stats"]:
        await bot.send_message(chat_id, "Пожалуйста, выбери характеристику из предложенных.")
        return

    value = state["available_values"][0]
    key = STAT_LABELS[text]
    state["assigned_stats"][key] = value
    state["available_values"].pop(0)
    state["available_stats"].remove(text)

    if state["available_values"]:
        next_value = state["available_values"][0]
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for stat in state["available_stats"]:
            markup.add(KeyboardButton(stat))
        markup = add_back_button(markup)
        await save_state(chat_id, state, db_pool)
        await bot.send_message(chat_id, f"Какую характеристику назначить значению {next_value}?", reply_markup=markup)
    else:
        await finalize_character(chat_id, state, bot, db_pool, state["assigned_stats"])

# 🧮 Финализация персонажа
async def finalize_character(chat_id, state, bot, db_pool, stats):
    race = state["race"]
    char_class = state["class"]
    hero_name = state["hero_name"]
    gender = state["gender"]

    race_bonus = RACE_BONUSES.get(race, {})
    class_bonus = CLASS_BONUSES.get(char_class, {})

    for stat in stats:
        stats[stat] += race_bonus.get(stat, 0) + class_bonus.get(stat, 0)

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users SET gender=$1, race=$2, class=$3, hero_name=$4,
            strength=$5, dexterity=$6, constitution=$7,
            intelligence=$8, wisdom=$9, charisma=$10
            WHERE chat_id=$11
            """,
            gender, race, char_class, hero_name,
            stats["str"], stats["dex"], stats["con"],
            stats["int"], stats["wis"], stats["cha"], chat_id
        )

    await send_race_card(bot, chat_id, race, char_class, stats, hero_name, gender=gender)
    await bot.send_message(chat_id, "🎉 Персонаж успешно создан! Скоро ты сможешь выбрать сюжет для игры!")

    await save_state(chat_id, {"state": "main_menu"}, db_pool)

# 🚧 TODO: Реализация ручного распределения (в следующем шаге)
async def start_custom_distribution(chat_id, state, bot, db_pool):
    state.update({
        "state": "custom_stat_str",
        "custom_stats": {},
        "remaining_points": 27,
        "order": ["str", "dex", "con", "int", "wis", "cha"],
        "current_index": 0
    })
    await save_state(chat_id, state, db_pool)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(8, 16):
        markup.add(KeyboardButton(str(i)))
    markup = add_back_button(markup)

    await bot.send_message(chat_id, "Начнем! Сколько очков ты хочешь вложить в СИЛУ?", reply_markup=markup)

# 🧮 Обработка каждого шага ручного распределения (27 очков)
async def handle_custom_distribution(message, state, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()

    try:
        val = int(text)
    except ValueError:
        await bot.send_message(chat_id, "Пожалуйста, введите число от 8 до 15.")
        return

    if val < 8 or val > 15:
        await bot.send_message(chat_id, "Допустимы значения от 8 до 15.")
        return

    def calc_cost(score):
        return {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}.get(score, 100)

    cost = calc_cost(val)
    if cost > state["remaining_points"]:
        await bot.send_message(chat_id, f"Недостаточно очков. У тебя осталось {state['remaining_points']}.")
        return

    order = state["order"]
    index = state["current_index"]
    stat_key = order[index]

    state["custom_stats"][stat_key] = val
    state["remaining_points"] -= cost
    state["current_index"] += 1

    if state["current_index"] < len(order):
        next_stat = order[state["current_index"]]
        state["state"] = f"custom_stat_{next_stat}"
        await save_state(chat_id, state, db_pool)

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(8, 16):
            markup.add(KeyboardButton(str(i)))
        markup = add_back_button(markup)

        await bot.send_message(
            chat_id,
            f"Выбери значение для {STAT_NAMES_REVERSE[next_stat]}. Очков осталось: {state['remaining_points']}",
            reply_markup=markup
        )
    else:
        await finalize_character(chat_id, state, bot, db_pool, state["custom_stats"])