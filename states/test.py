# states/test.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from data.constants import QUESTIONS, RECOMMENDATIONS
from utils.display import show_character_card
from utils.helpers import log_error
from db.database import save_state_db as save_state, load_state_db as load_state
from utils.keyboards import add_back_button

def build_keyboard(options):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(option))
    markup = add_back_button(markup)
    return markup


async def start_character_test(chat_id, user_states, bot, db_pool):
    state = await load_state(chat_id, db_pool) or {}
    state.update({
        "state": "taking_test",
        "test_answers": [],
        "test_stats": {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 0},
        "current_question": 0,
        "hero_name": state.get("hero_name"),
        "gender": state.get("gender")
    })
    await save_state(chat_id, state, db_pool)
    await ask_test_question(chat_id, state, bot, db_pool)


async def ask_test_question(chat_id, state, bot, db_pool):
    question_num = state["current_question"]
    if question_num >= len(QUESTIONS):
        await finish_character_test(chat_id, bot, db_pool)
        return

    question = QUESTIONS[question_num]
    options = [opt["text"] for opt in question["options"]]
    markup = build_keyboard(options)
    await bot.send_message(chat_id, question["text"], reply_markup=markup)


def normalize(text):
    return text.replace("–", "-").replace("—", "-").strip().lower()


async def handle_test_answer(message, bot, db_pool):
    chat_id = message.chat.id
    text = message.text.strip()
    state = await load_state(chat_id, db_pool) or {}
    question_num = state["current_question"]
    question = QUESTIONS[question_num]
    print(f"[DEBUG] handle_test_answer called with: '{text}'")
    user_text = normalize(text)
    print(f"[DEBUG] normalized user_text = '{user_text}'")
    for opt in question["options"]:
        print(f"[DEBUG] comparing with: '{normalize(opt['text'])}'")
    selected = next((opt for opt in question["options"] if normalize(opt["text"]) == user_text), None)

    if not selected:
        await bot.send_message(chat_id, "Пожалуйста, выбери вариант из предложенных.")
        return

    for stat, val in selected["stats"].items():
        state["test_stats"][stat] += val

    state["current_question"] += 1
    await save_state(chat_id, state, db_pool)
    await ask_test_question(chat_id, state, bot, db_pool)


async def finish_character_test(chat_id, bot, db_pool):
    state = await load_state(chat_id, db_pool) or {}
    stats = state["test_stats"]
    stat_order = sorted(stats.items(), key=lambda item: item[1], reverse=True)
    standard_array = [15, 14, 13, 12, 10, 8]
    final_stats = {stat: val for (stat, _), val in zip(stat_order, standard_array)}

    main_stat = max(stats, key=stats.get)
    recommendation = RECOMMENDATIONS.get(main_stat, {"class": "Воин", "race": "Человек"})
    race = recommendation["race"]
    char_class = recommendation["class"]

    from data.constants import RACE_BONUSES, CLASS_BONUSES
    race_bonus = RACE_BONUSES.get(race, {})
    class_bonus = CLASS_BONUSES.get(char_class, {})

    for stat, bonus in race_bonus.items():
        final_stats[stat] = final_stats.get(stat, 0) + bonus

    for stat, bonus in class_bonus.items():
        final_stats[stat] = final_stats.get(stat, 0) + bonus

    bonus_stats = {}
    for stat in ["str", "dex", "con", "int", "wis", "cha"]:
        bonus = 0
        if stat in race_bonus:
            bonus += race_bonus[stat]
        if stat in class_bonus:
            bonus += class_bonus[stat]
        if bonus != 0:
            bonus_stats[stat] = bonus

    state["recommendation"] = {
        "race": race,
        "class": char_class,
        "stats": final_stats
    }

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Пройти тест заново"))
    markup.add(KeyboardButton("Создать своего персонажа"))
    markup.add(KeyboardButton("Начать игру"))
    markup.add(KeyboardButton("Назад"))

    from db.database import get_character
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE users SET race=$1, class=$2, strength=$3, dexterity=$4, constitution=$5,
            intelligence=$6, wisdom=$7, charisma=$8 WHERE chat_id=$9
        """,
        race, char_class,
        final_stats["str"], final_stats["dex"], final_stats["con"],
        final_stats["int"], final_stats["wis"], final_stats["cha"],
        chat_id)

    character = await get_character(chat_id, db_pool)
    await save_state(chat_id, state, db_pool)
    await show_character_card(chat_id, bot, db_pool, state)

    state["state"] = "test_completed"
    await save_state(chat_id, state, db_pool)

    await bot.send_message(chat_id, "Выбери дальнейшее действие:", reply_markup=markup)
