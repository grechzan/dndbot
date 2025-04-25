# utils/helpers.py
import os
import re
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "images", "heroes"))

GENDER_CODES = {
    "Мужчина": "man",
    "Женщина": "woman"
}

from telebot.types import ReplyKeyboardMarkup

RACE_KEYS = {
    "Человек": "human",
    "Эльф": "elf",
    "Лесной эльф": "forest_elf",
    "Высший эльф": "high_elf",
    "Темный эльф": "dark_elf",
    "Полурослик": "halfling",
    "Полуорк": "halforc",
    "Тифлинг": "tifling",
    "Полуэльф": "halfelf",
    "Гном": "gnome",
    "Дварф": "dwarf",
    "Драконорожденный": "dragonborn"
}

CLASS_KEYS = {
    "Воин": "fighter",
    "Варвар": "barbarian",
    "Плут": "rogue",
    "Жрец": "cleric",
    "Паладин": "paladin",
    "Волшебник": "wizard",
    "Чародей": "sorcerer",
    "Колдун": "warlock",
    "Бард": "bard",
    "Друид": "druid"
}

def is_valid_name(name):
    if len(name) > 50:
        return False, "Имя слишком длинное (максимум 50 символов)"
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', name):
        return False, "Имя содержит недопустимые символы"
    return True, ""

async def log_error(chat_id, error, context=""):
    error_msg = f"Ошибка у пользователя {chat_id}: {error}\nКонтекст: {context}"
    logger.error(error_msg, exc_info=True)

async def go_back(chat_id, db_pool):
    from db.database import load_state_db, save_state_db
    state = await load_state_db(chat_id, db_pool) or {}
    if state.get("navigation_stack"):
        state["state"] = state["navigation_stack"].pop()
        await save_state_db(chat_id, state, db_pool)
        return state
    return None

async def send_race_card(bot, chat_id, race, char_class, stats, hero_name, bonus_stats=None, gender=None):
    try:
        if "(" in race and ")" in race:
            race = race.split("(")[-1].replace(")", "").strip()

        if bonus_stats:
            card = f"""🧙‍♂️ {hero_name} - {race} ({char_class})\n\n📊 Дополнительные характеристики расы и класса:"""
            card += f"""
💪 Сила: +{bonus_stats.get("str", 0)}
🏃 Ловкость: +{bonus_stats.get("dex", 0)}
🛡️ Выносливость: +{bonus_stats.get("con", 0)}
🧠 Интеллект: +{bonus_stats.get("int", 0)}
🔮 Мудрость: +{bonus_stats.get("wis", 0)}
🎭 Харизма: +{bonus_stats.get("cha", 0)}
"""
        else:
            card = f"""🧙‍♂️ {hero_name} - {race} ({char_class})\n\n📊 Характеристики:
💪 Сила: {stats.get("str", "—")}
🏃 Ловкость: {stats.get("dex", "—")}
🛡️ Выносливость: {stats.get("con", "—")}
🧠 Интеллект: {stats.get("int", "—")}
🔮 Мудрость: {stats.get("wis", "—")}
🎭 Харизма: {stats.get("cha", "—")}"""

        gender_key = GENDER_CODES.get(gender or "Мужчина", "man")
        race_key = RACE_KEYS.get(race, race.lower().replace(" ", "_"))
        class_key = CLASS_KEYS.get(char_class, char_class.lower())
        filename = f"{gender_key}_{race_key}_{class_key}.png"
        path = os.path.join(IMAGES_DIR, filename)

        if not os.path.exists(path):
            path = os.path.join(IMAGES_DIR, "wip.png")

        with open(path, "rb") as photo:
            await bot.send_photo(chat_id, photo, caption=card)

    except Exception as e:
        await log_error(chat_id, e, "При отправке карточки персонажа")
        await bot.send_message(chat_id, "⚠️ Ошибка при отображении персонажа")