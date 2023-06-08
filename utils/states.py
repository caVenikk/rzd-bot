from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    waiting_for_departure_station = State()
    select_departure_station = State()
    waiting_for_arrival_station = State()
    select_arrival_station = State()
    select_date = State()
