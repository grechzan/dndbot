# help.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

async def show_help_menu(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("1. Правила игры"))
    markup.add(KeyboardButton("2. Характеристики и бонусы"))
    markup.add(KeyboardButton("3. Выбор навыков"))
    markup.add(KeyboardButton("4. Технический вопрос"))
    await bot.send_message(chat_id, "С чем вам нужна помощь?", reply_markup=markup)

async def handle_help_response(bot, chat_id, text):
    await bot.send_message(chat_id, "Эта функция ещё в разработке. Скоро всё появится!")

