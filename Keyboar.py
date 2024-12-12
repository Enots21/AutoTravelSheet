from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_vod = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегестрироваться', callback_data='start')]])

cars_number = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить авто', callback_data='numbercars')]])

info_vod = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Верно', callback_data='start_vod')]])
