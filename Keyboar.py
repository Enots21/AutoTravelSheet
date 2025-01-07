from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_vod = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегестрироваться', callback_data='start')]])

cars_number = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить авто', callback_data='numbercars')]])

access_vod = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Записать данные', callback_data='yesaccess')]
])

info_vod = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Верно', callback_data='sinfo')]])

reinfoveh = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Перезаписать', callback_data='reinfove')],
    [InlineKeyboardButton(text='Верно', callback_data='yesinfo')]
])

rep_start = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='Добавить новый путевой лист📄')],
    [KeyboardButton(text='Выбрать путевой лист📇')],
    [KeyboardButton(text='Информация о машине🚘')]
])