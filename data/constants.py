# data/constants.py
import os
from dotenv import dotenv_values

# Загружаем конфиг из .env файла
CONFIG_PATH = "config/tokens.env"
config = dotenv_values(CONFIG_PATH)

TOKEN = config['TELEGRAM_BOT_TOKEN']

DB_CONFIG = {
    'host': config['DB_HOST'],
    'port': config.get('DB_PORT', '5432'),
    'database': config['DB_NAME'],
    'user': config['DB_USER'],
    'password': config['DB_PASSWORD']
}

db_pool = None  # будет заполнен в main.py

# Глобальные игровые данные
GENDERS = ["Мужчина", "Женщина"]

CLASSES = {
    "Воин": {"main": ["str", "con"], "secondary": ["dex"]},
    "Варвар": {"main": ["str", "con"], "secondary": ["dex"]},
    "Плут": {"main": ["dex", "int"], "secondary": ["cha"]},
    "Жрец": {"main": ["wis", "cha"], "secondary": ["con"]},
    "Паладин": {"main": ["str", "cha"], "secondary": ["con"]},
    "Волшебник": {"main": ["int", "wis"], "secondary": ["dex"]},
    "Чародей": {"main": ["cha", "con"], "secondary": ["dex"]},
    "Колдун": {"main": ["cha", "int"], "secondary": ["con"]},
    "Бард": {"main": ["cha", "dex"], "secondary": ["wis"]},
    "Друид": {"main": ["wis", "con"], "secondary": ["dex"]},
}

RACE_BONUSES = {  
    "Человек": {"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1},
    "Эльф": {"dex": 2},
    "Темный эльф": {"dex": 2, "cha": 1},
    "Лесной эльф": {"dex": 2, "wis": 1},
    "Высший эльф": {"dex": 2, "int": 1},
    "Гном": {"con": 2},
    "Дварф": {"con": 2, "wis": 1},
    "Драконорожденный": {"str": 2, "cha": 1},
    "Полурослик": {"dex": 2, "cha": 1},
    "Полуорк": {"str": 2, "con": 1},
    "Полуэльф": {"cha": 2, "dex": 1},
    "Тифлинг": {"cha": 2, "int": 1},
}

CLASS_BONUSES = {
    "Воин": {"str": 1},
    "Варвар": {"con": 1},
    "Плут": {"dex": 1},
    "Жрец": {"wis": 1},
    "Паладин": {"cha": 1},
    "Волшебник": {"int": 1},
    "Чародей": {"cha": 1},
    "Колдун": {"cha": 1},
    "Бард": {"cha": 1},
    "Друид": {"wis": 1},
}

QUESTIONS = [
    {
        "text": "Перед тобой развязалась драка между стражей и разбойниками. Как ты поступишь?",
        "options": [
            {"text": "Ввяжусь в драку и помогу страже", "stats": {"str": 2, "con": 1}},
            {"text": "Ввяжусь в драку и помогу разбойникам", "stats": {"dex": 2, "int": 1}},
            {"text": "Убегу и спрячусь от них", "stats": {"dex": 2, "wis": 1}},
            {"text": "Попробую уговорить их перестать сражаться", "stats": {"cha": 2, "wis": 1}}
        ]
    },
    {
        "text": "Ты нашел древний артефакт. Что будешь делать?",
        "options": [
            {"text": "Возьму себе - сила в моих руках!", "stats": {"str": 2, "con": 1}},
            {"text": "Изучу его магические свойства", "stats": {"int": 2, "wis": 1}},
            {"text": "Продам за хорошие деньги", "stats": {"cha": 2, "dex": 1}},
            {"text": "Спрячу, чтобы никто не нашел", "stats": {"dex": 2, "wis": 1}}
        ]
    },
    {
        "text": "Как ты обычно решаешь проблемы?",
        "options": [
            {"text": "Физической силой", "stats": {"str": 3}},
            {"text": "Хитростью и ловкостью", "stats": {"dex": 3}},
            {"text": "Магией и знаниями", "stats": {"int": 3}},
            {"text": "Убеждением и обаянием", "stats": {"cha": 3}}
        ]
    }
]

RECOMMENDATIONS = {
    "str": {"class": "Воин", "race": "Дварф"},
    "dex": {"class": "Плут", "race": "Эльф"},
    "int": {"class": "Волшебник", "race": "Гном"},
    "wis": {"class": "Жрец", "race": "Полуэльф"},
    "cha": {"class": "Бард", "race": "Тифлинг"},
    "con": {"class": "Варвар", "race": "Полуорк"}
}
