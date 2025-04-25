# utils/display.py

from db.database import get_character
from utils.helpers import send_race_card


async def show_character_card(chat_id, bot, db_pool, user_states=None):
    character = await get_character(chat_id, db_pool)
    stats = {
        "str": character.get("strength", 10),
        "dex": character.get("dexterity", 10),
        "con": character.get("constitution", 10),
        "int": character.get("intelligence", 10),
        "wis": character.get("wisdom", 10),
        "cha": character.get("charisma", 10)
    }

    gender = character.get("gender")
    if not gender and user_states:
        gender = user_states.get(chat_id, {}).get("gender", "Мужчина")
    if not gender:
        gender = "Мужчина"

    hero_name = character.get("hero_name", "Безымянный")

    await send_race_card(
        bot,
        chat_id,
        character["race"],
        character["class"],
        stats,
        hero_name,
        gender=gender
    )
