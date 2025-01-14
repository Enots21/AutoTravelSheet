import datetime
import logging
import re

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.DB.database import db
from tgbot.Keyboar import start_vod, cars_number, info_vod, rep_start, reinfoveh, access_vod
from tgbot.states import Gen

router = Router()  # Создание роутера
storage = MemoryStorage()  # Создание хранилища

logging.basicConfig(level=logging.INFO, filename="logi.log", filemode="w", encoding="utf-8",
                    format="%(asctime)s - %(name)s - %(module)s - %(message)s ✔️ ")


@router.message(Command("start"))  # Создание команды
async def send_welcome(message: types.Message):
    logging.info('Проверка есть ли база данных')
    try:
        if not await db.create_tables():
            logging.info('Таблицы созданы')  # Логируем создание таблиц только при условии успеха
        else:
            logging.info('Таблицы уже существуют')

        if not await db.user_exists(message.from_user.id):  # Создание пользователя
            await sta_reg(message)
        elif not await db.info_number_car(message.from_user.id):  # Проверка есть ли у пользователя авто
            await env_reg(message)
        else:
            await gen_info(message)
    except Exception as err:  # Общая обработка исключений
        logging.error(f'Ошибка: {err}❌')  # Более общий вывод ошибки


# ==========================НАЧАЛО
async def sta_reg(message: types.Message):
    logging.info('Началось выполнение запроса')
    stext = ('Добро пожаловать в бота для работы!🎉 \n\nЯ — ваш помощник в оформлении путевых листов.😊\n'
             'С моей помощью вы сможете быстро и без ошибок заполнять документы для служебных поездок '
             'и других рабочих нужд. Просто опишите вашу поездку, и я подготовлю готовый путевой лист,'
             ' который вы сможете распечатать или сохранить. 📄\n\nПреимущества\n\nЭкономия времени: ⏰\nАвтоматизация'
             ' заполнения путевых листов избавит вас от рутинной работы.\n\n'
             'Точность: 🎯\nБот гарантирует правильность всех данных, исключая ошибки.\n\nУдобство: 💻\nДокументы можно '
             ' распечатать или сохранить в электронном виде.\n\nНачните пользоваться ботом '
             'уже сегодня и упростите процесс'
             ' оформления путевых листов!🚀')
    try:
        logging.info('Выполнено запрос успешно')
        await message.answer(stext, reply_markup=start_vod)
    except ZeroDivisionError as err:
        logging.error(err)
        await message.answer('Ошибка❌')


async def env_reg(message: types.Message):  #
    await message.answer('Добро пожаловать водитель! \nДавай добавим тебе авто для начала!',
                         reply_markup=cars_number)


# ===============================================================
# env_reg
@router.callback_query(F.data == "numbercars")  # Передаем данные из кнопки
async def start_number(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()  # Удаление сообщения
    await callback.message.answer('Введите Номер автомобиля:\n\nПРИМЕР: A341AA777')
    await state.set_state(Gen.car_number)


# ===============================================================
@router.callback_query(F.data == "start")
async def start(callback: types.CallbackQuery, state: FSMContext):
    logging.info('Началось выполнение 1/3 запроса')
    try:
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer('1/3\nЧтобы ваш путевой лист был оформлен правильно, пожалуйста, '
                                      'напишите ваше полное имя.\n\n ПРИМЕР: Иван')
        await state.set_state(Gen.name)
    except ZeroDivisionError as err:
        logging.error(err)
        await callback.message.answer('Ошибка❌')


# ===============================================================


@router.message(Gen.name)  # Передаем данные из текста
async def name(message: types.Message, state: FSMContext):
    names = message.text
    pattern = r'^[а-яА-ЯёЁ]+$'  # Пример шаблона, может потребовать уточнения
    if not re.match(pattern, names):  # Проверка на корректность
        await message.answer('Некорректное имя. Пожалуйста, введите имя на русском языке. ПРИМЕР: Иван')
        return
    await state.update_data(names=message.text)  # Обновление данных
    await message.answer('2/3\nДля заполнения формы, пожалуйста, введите вашу фамилию. \n\nПРИМЕР: Иванов')
    await state.set_state(Gen.last_name)  # Передаем данные из текста


@router.message(Gen.last_name)  # Передаем данные из текста
async def last_name(message: types.Message, state: FSMContext):
    last_sname = message.text
    pattern = r'^[а-яА-ЯёЁ]+$'  # Пример шаблона, может потребовать уточнения
    if not re.match(pattern, last_sname):
        await message.answer('Некорректная фамилия. Пожалуйста, введите фамилию на русском языке')
        return
    await state.update_data(last_names=message.text)
    await message.answer('3/3\nДля заполнения формы, пожалуйста, введите ваш телефон\n\nПРИМЕР: +7XXXXXXXXXX')
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
    if not await db.user_exists(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.username, names, last_names, iphone_number,
                          reg_date)  # добавление пользователя в базу
    else:
        pass
    msg = (f'Ваши данные:\n'
           f'Имя: {names}\n'
           f'Фамилия: {last_names}\n'
           f'Телефон: {iphone_number}\nВверные ли данные которые вы указали?\n')
    await message.answer(msg, reply_markup=info_vod)


# ===============================================================


# ===============================================================

@router.callback_query(F.data == "sinfo")
async def process_start(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()  # Correctly use call.message
    await env_reg(call.message)


@router.message(Gen.car_number)  # Передаем данные из текстаv
async def number_cars(message: types.Message, state: FSMContext):
    names = message.text
    pattern = r'^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
    await state.update_data(numbers_cars=message.text)
    number_car = str(names)
    if not re.match(pattern, names):
        await message.answer('Номер, похоже, корректный.')
    else:
        if await db.car_exists(number_car, message.from_user.id):
            await message.answer(f'Такой {number_car} есть в базе')
            await gen_info(message)
            await state.clear()
        else:
            await message.answer('Есть ли у машины спец оборудование\nЕсли есть '
                                 'введите Л/час\n\nЕсли нету введите 0.')
            await state.set_state(Gen.spec_litcar)
        # if not await db.car_exists(number_car):
        #     await db.add_vehicle(message.from_user.id, number_car)  # добавление автомобиля в базу
        #     await db.create_car_table(number_car)  # создание таблицы в базе
        #     await message.answer('Все готово, ожидайте.')
        #     await state.clear()
        #     await asyncio.sleep(0.5)
        #     await gen_info(message)  # Переход к следующему сообщению
        # else:
        #     await db.get_car_number(number_car)
        #     carinfo = await db.num_info_car(number_car)
        #     if carinfo:  # Check if carinfo is not None
        #         await message.answer(f'Такой уже есть в базе\n\n'
        #                              f'Последние данные о машине:\n'
        #                              f'Номер: {carinfo.get("nuber_car", "N/A")}\n'
        #                              f'Начальный километраж: {carinfo.get("start_km", "N/A")}\n'
        #                              f'Последний километраж: {carinfo.get("end_km", "N/A")}\n'
        #                              f'Топливо Нач: {carinfo.get("fuel_start", "N/A")}\n'
        #                              f'Топливо Пос: {carinfo.get("fuel_end", "N/A")}\n'
        #                              f'Общий километраж: {carinfo.get("total_km", "N/A")}\n'
        #                              f'Фактический расход: {carinfo.get("fuel_refuel", "N/A")}\n'
        #                              f'Последний водитель: {carinfo.get("user_name", "N/A")}\n')
        #     else:
        #         print(f'Номер машины: {number_car}')
        #         await message.answer('Данные об этой машине не найдены.')


@router.message(Gen.spec_litcar)
async def spec_litcar(message: types.Message, state: FSMContext):
    await state.update_data(spec_litcar=message.text)
    await message.answer('Введите модель авто')
    await state.set_state(Gen.name_car)


@router.message(Gen.name_car)
async def name_car(message: types.Message, state: FSMContext):
    if len(message.text) <= 10:
        await state.update_data(name_car=message.text)
        await message.answer('Все готово')
        vinfo = await state.get_data()
        number_cars = vinfo.get("numbers_cars", "Не указано")
        spec_litcar = vinfo.get("spec_litcar", "Не указано")
        name_car = vinfo.get("name_car", "Не указано")
        if int(spec_litcar) == 0:
            spec = 0
            await db.add_vehicle(number_cars, name_car, spec, message.from_user.id)
            await db.create_car_table(number_cars)
            await state.clear()
        else:
            await db.create_car_table(number_cars)
            await db.add_vehicle(number_cars, name_car, spec_litcar, message.from_user.id)
            await state.clear()
    else:
        logging.error(f'{message.from_user.id} Ввёл слишком много символов для названия авто')
        await message.answer('Название авто не может быть больше 10 символов!')


async def gen_info(message: types.Message):
    info = await db.get_user(message.from_user.id)
    logging.debug(f"Полученные данные: {info}")
    await message.answer(f'Добро пожаловать {info["name"]}, {info["last_name"]}\n\n'
                         f'Пожалуйста, выберите действие, которое вы хотите совершить:\n\n'
                         f'1. Добавить новый путевой лист📄\n2. Выбрать путевой лист📇\n3. Информация о машине🚘',
                         reply_markup=rep_start)


@router.message(F.text == 'Добавить новый путевой лист📄')
async def list_car(message: types.Message, state: FSMContext):
    global auto
    global keyboard
    auto = await db.fetch_vehicle_info_by_user_id(message.from_user.id)  # Запрашиваем у пользователя список машин
    if auto:
        for num in auto:  # цикл по списку машин
            keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [types.InlineKeyboardButton(text=f'{num[0]} | {num[1]}', callback_data=f"car_{num[0]}")],
            ])  # Кнопки будут в один ряд
        await message.answer(f'Выберите машину:', reply_markup=keyboard)
        await state.set_state(Gen.car_type)
    else:
        soz_avto = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [types.InlineKeyboardButton(text='Cоздать авто', callback_data='numbercars')]])
        await message.answer('У вас нет машин', reply_markup=soz_avto)


@router.message(F.text == 'Информация о машине🚘')
async def info_car(message: types.Message, state: FSMContext):
    global keyboards
    list_car = await db.list_car_numbers(message.from_user.id)
    print(list_car)
    auto = await db.fetch_vehicle_info_by_user_id(message.from_user.id)  # Запрашиваем у пользователя список машин
    if auto:
        for num in auto:  # цикл по списку машин
            keyboards = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [types.InlineKeyboardButton(text=f'{num[0]} | {num[1]}', callback_data=f"info_{num[0]}")],
            ])  # Кнопки будут в один ряд
        keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [types.InlineKeyboardButton(text='Добавить авто', callback_data='numbercars')],
            ])
        
        ss = zip(keyboards, keyboard)
        await message.answer(f'Выберите машину:', reply_markup=ss)
    else:
        await message.answer('У вас нет машин.')


@router.callback_query(lambda c: c.data and c.data.startswith("car_"))  # Измените условие на соответствующее
async def car_selected(call: types.CallbackQuery, state: FSMContext):
    # Получаем данные о выбранной машине
    car_type = call.data[4:]
    try:
        await state.update_data(car_type=car_type)  # Сохраняем выбранные данные в state
        await call.answer(f"Выбран автомобиль: {car_type}")
        await call.message.delete()

        # Проверяем, существует ли выбранный автомобиль
        auto = await db.fetch_vehicle_info_by_user_id(call.from_user.id)
        if auto[0]:
            for num in auto[0]:
                if num == car_type:
                    await call.message.answer('Введите стартовый километры:')
                    await state.set_state(Gen.start_km)
                    return  # Завершаем функцию после успешного вызова
            await call.message.answer('Выбранный автомобиль не найден в вашем списке.')
            print(auto)
        else:
            await call.message.answer('У вас нету машины.')
    except Exception as e:
        await call.message.answer(f'Произошла ошибка: {e}')


@router.callback_query(lambda c: c.data and c.data.startswith("info_"))
async def info_car_selected(call: types.CallbackQuery, state: FSMContext):
    car_type = call.data[5:]
    try:
        # Здесь выполняется получение и отображение информации о машине
        car_info = await db.fetch_vehicle_info(car_type)

        try:
            if car_info and car_info[0]:  # Проверяем, что car_info не пуст и содержит хотя бы один элемент
                vehicle_name, special_equipment, vehicle_numbers = car_info[0]  # Распаковка кортежа
                await call.message.answer(f"Информация о машине {vehicle_numbers}:\n"
                                          f"Название: {vehicle_name}\n"
                                          f"Спец.оборудование: {special_equipment} Л.час\n"
                                          f"Номер: {vehicle_numbers}")
            else:
                await call.message.answer(f"Информация о машине {car_type} не найдена.")
        except Exception as e:
            logging.error(e)
            await call.answer()
        await call.answer()
    except Exception as e:
        await call.message.answer(f'Произошла ошибка: {e}')


@router.message(Gen.start_km)
async def start_km(message: types.Message, state: FSMContext):
    await state.update_data(start_km=message.text)
    await message.answer('Введите конечные километры:')  # Запрашиваем у пользователя конечные километры
    await state.set_state(Gen.end_km)


@router.message(Gen.end_km)
async def end_km(message: types.Message, state: FSMContext):
    await state.update_data(end_km=message.text)
    await message.answer('Введите количество топлива на начало:')
    await state.set_state(Gen.start_fuel)


@router.message(Gen.start_fuel)  # Запрашиваем у пользователя количество топлива на начало
async def fuel_start(message: types.Message, state: FSMContext):
    await state.update_data(start_fuel=message.text)
    await message.answer('Введите какой рассход: ')
    await state.set_state(Gen.total_comkm)


@router.message(Gen.total_comkm)
async def total_comkm(message: types.Message, state: FSMContext):
    await state.update_data(total_comkm=message.text)
    await message.answer('Вы сегодня заправлялись ?!\n'
                         'Введите количество топлива\n'
                         'Если не заправлялись напиште 0')
    await state.set_state(Gen.fuel_refuel)


@router.message(Gen.fuel_refuel)
async def fuel_refuel(message: types.Message, state: FSMContext):
    await state.update_data(fuel_refuel=message.text)
    vinfo = await state.get_data()
    kmst = vinfo.get("start_km", "Не указано")
    kmen = vinfo.get("end_km", "Не указано")
    fust = vinfo.get("start_fuel", "Не указано")
    aut = vinfo.get("car_type", "Не указано")
    fuel_refuel_st = vinfo.get("fuel_refuel", "Не указано")
    total_comkm_st = vinfo.get("total_comkm", "Не указано")
    await message.answer(f'Информация о машине:\n'
                         f'Начальные километры: {kmst}\n'
                         f'Конечные километры: {kmen}\n'
                         f'Количество топлива на начало: {fust}\n'
                         f'Расход топлива: {total_comkm_st}\n'
                         f'Заправка: {fuel_refuel_st}\n'
                         f'Тип машины: {aut}', reply_markup=reinfoveh)


@router.callback_query(F.data == 'reinfove')
async def reinfove(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(f'Выберите машину:', reply_markup=keyboard)


@router.callback_query(F.data == 'yesinfo')
async def yesinfo(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await uinfo(call.message, state)


async def uinfo(message: types.Message, state: FSMContext):
    global kmst, kmen, fust, fuel_refuel_st, total_comkm_st, summ_ob, fuct, end_ful, aut
    # Начальный км,, конечный км, начальное топливо, заправка, расход топлива, тип машины
    vinfo = await state.get_data()
    kmst = vinfo.get("start_km", "Не указано")  # Начальные километры
    kmen = vinfo.get("end_km", "Не указано")  # Конечные километры
    fust = vinfo.get("start_fuel", "Не указано")  # Количество топлива на начало
    fuel_refuel_st = vinfo.get("fuel_refuel", "Не указано")  # Заправка
    total_comkm_st = vinfo.get("total_comkm", "Не указано")  # Какой расход
    aut = vinfo.get("car_type", "Не указано")  # Тип машины

    try:
        # Преобразование входных данных в числа
        kmst = float(kmst.replace(',', '.')) if kmst != "Не указано" else 0  # Начальные километры
        kmen = float(kmen.replace(',', '.')) if kmen != "Не указано" else 0  # Конечные километры
        fust = float(fust.replace(',', '.')) if fust != "Не указано" else 0  # Количество топлива на начало
        fuel_refuel_st = float(fuel_refuel_st.replace(',', '.')) if fuel_refuel_st != "Не указано" else 0  # Заправка
        total_comkm_st = float(total_comkm_st.replace(',', '.')) if total_comkm_st != "Не указано" else 0  # расход

        # Расчеты
        summ_ob = kmen - kmst  # Общий пробег
        fuct = (summ_ob * total_comkm_st) / 100  # Фактический расход
        end_ful = fust - fuct + fuel_refuel_st  # Топливо на конец

        # Формирование сообщения
        await message.answer(f'Информация о машине:\n'
                             f'Начальные километры: {kmst:.0f}\n'
                             f'Конечные километры: {kmen:.0f}\n'
                             f'Количество топлива на начало: {fust:.2f}\n'
                             f'Количество топлива на конец: {end_ful:.2f}\n'
                             f'Общий пробег: {summ_ob:.0f}\n'
                             f'Фактический расход: {fuct:.1f}\n'
                             f'Заправка: {fuel_refuel_st:.0f}\n'
                             f'Машина: {aut}', reply_markup=access_vod)
        await state.clear()

    except ValueError as e:
        print(e)


@router.callback_query(F.data == 'yesaccess')
async def access_vods(call: types.CallbackQuery):
    await call.answer()
    date = datetime.date.today()
    info = await db.get_user(call.from_user.id)
    name = info.get('name')
    last_name = info.get('last_name')
    use_info = name + ' ' + last_name
    spec = await db.get_veh_id(aut)
    await db.add_car_info(aut, use_info, date, 0, 0, kmst, kmen, summ_ob, spec[0], fuct, fust, end_ful)
    await call.message.delete()
    await call.answer(f'Успешно добавлена информация о машине\n/START')
