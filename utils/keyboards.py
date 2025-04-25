# utils/keyboards.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def add_back_button(markup: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    markup.add(KeyboardButton("Назад"))
    return markup
