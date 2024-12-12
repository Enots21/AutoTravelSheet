import asyncio
import datetime
import re

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from DB.database import db
from Keyboar import start_vod, cars_number, info_vod
from states import Gen

router = Router()  # Создание роутера
storage = MemoryStorage()  # Создание хранилища


@router.message(Command("start"))  # Создание команды
async def send_welcome(message: types.Message):
    await db.create_tables()  # Создание таблиц
    if not await db.user_exists(message.from_user.id, message.from_user.username):  # Создание пользователя
        await message.answer(
            "Добро пожаловать в бота! \nЯ помогаю заполнять путевые листы. \nДля начала нужно зарегестрироваться!",
            reply_markup=start_vod)
    elif not await db.info_number_car(message.from_user.id):  # Проверка есть ли у пользователя авто
        await message.answer('Добро пожаловать водитель! \nДавай добавим тебе авто для начала!',
                             reply_markup=cars_number)
    else:
        await main(message)


@router.callback_query(F.data == "numbercars")  # Передаем данные из кнопки
async def start_number(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Введите Номер автомобиля:')
    await state.set_state(Gen.car_number)


@router.callback_query(F.data == "start")  # Передаем данные из кнопки
async def start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Введите Имя:')
    await state.set_state(Gen.name)


@router.message(Gen.name)  # Передаем данные из текста
async def name(message: types.Message, state: FSMContext):
    names = message.text
    pattern = r'^[а-яА-ЯёЁ]+$'  # Пример шаблона, может потребовать уточнения
    if not re.match(pattern, names):  # Проверка на корректность
        await message.answer('Некорректное имя. Пожалуйста, введите имя на русском языке')
        return
    await state.update_data(names=message.text)  # Обновление данных
    await message.answer('Введите Фамилию:')
    await state.set_state(Gen.last_name)  # Передаем данные из текста


@router.message(Gen.last_name)  # Передаем данные из текста
async def last_name(message: types.Message, state: FSMContext):
    last_sname = message.text
    pattern = r'^[а-яА-ЯёЁ]+$'  # Пример шаблона, может потребовать уточнения
    if not re.match(pattern, last_sname):
        await message.answer('Некорректная фамилия. Пожалуйста, введите фамилию на русском языке')
        return
    await state.update_data(last_names=message.text)
    await message.answer('Введите телефон')
    await state.set_state(Gen.iphone)


@router.message(Gen.iphone)
async def iphone(message: types.Message, state: FSMContext):
    phone_number = message.text
    # Проверка номера телефона с помощью регулярного выражения
    pattern = r"^\+\d{1,3}\d{9,15}$"  # Пример шаблона, может потребовать уточнения
    if not re.match(pattern, phone_number):
        await message.answer('Некорректный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX')
        return
    await state.update_data(iphone=message.text)
    data = await state.get_data()  # Получение данных из состояния
    names = data.get("names", "Не указано")
    last_names = data.get("last_names", "Не указано")
    iphone_number = data.get("iphone", "Не указано")
    reg_date = datetime.date.today()
    msg = (f'Ваши данные:\n'
           f'Имя: {names}\n'
           f'Фамилия: {last_names}\n'
           f'Телефон: {iphone_number}\nВверные ли данные которые вы указали?\n')
    if not await db.user_exists(message.from_user.id, message.from_user.username):
        await db.add_user(message.from_user.id, message.from_user.username, names, last_names, iphone_number,
                          reg_date)  # добавление пользователя в базу
    else:
        pass
    await message.answer(msg, reply_markup=info_vod)


@router.message(Gen.car_number)  # Передаем данные из текста
async def number_cars(message: types.Message, state: FSMContext):
    names = message.text
    pattern = r'^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
    await state.update_data(numbers_cars=message.text)
    number_car = str(names)
    if not re.match(pattern, names):
        await message.answer('Номер, похоже, корректный.')
    else:
        if not await db.car_exists(number_car):
            await db.add_vehicle(message.from_user.id, number_car)  # добавление автомобиля в базу
            await db.create_car_table(number_car)  # создание таблицы в базе
            await message.answer('Все готово, ожидайте.')
            await state.clear()  # Очищаем состояние
            await asyncio.sleep(0.5)
            await main(message)  # Переход к следующему сообщению
        else:
            await message.answer('Такой автомобиль уже есть в базе')


async def main(message: types.Message):
    info = await db.get_user(message.from_user.id)
    await message.answer(f'Добро пожаловать {info['name']}, {info['last_name']}')
