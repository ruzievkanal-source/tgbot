from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_buttons():
    rkb = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text="new note"),
        KeyboardButton(text="view notes"),
        KeyboardButton(text="delete last note"),
        KeyboardButton(text="Language"),
               ]
    rkb.add(*buttons)
    rkb.adjust(2,2)
    return rkb.as_markup(resize_keyboard=True)