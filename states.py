from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    name = State()
    last_name = State()
    iphone = State()
    car_number = State()
    spec_litcar = State()
    name_car = State()
    car_type = State()
    start_km = State()
    end_km = State()
    start_fuel = State()
    total_comkm = State()
    fuel_refuel = State()

