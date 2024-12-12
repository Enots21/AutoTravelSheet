from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    name = State()
    last_name = State()
    iphone = State()
    info_state = State()
    car_number = State()