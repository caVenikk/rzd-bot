from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

no_button = KeyboardButton("Нет")
yes_button = KeyboardButton("Да")

yes_no_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(yes_button, no_button)
