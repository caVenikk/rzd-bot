from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards import DateSelector, StationSelector, TrainsNavigator, yes_no_keyboard
from loader import dp
from utils import MessageBox
from utils.states import States


@dp.callback_query_handler(
    StationSelector.data.filter(action=[StationSelector.actions.next, StationSelector.actions.prev]),
    state=[States.select_departure_station, States.select_arrival_station],
)
async def station_selection(callback_query, callback_data):
    print(f"{callback_query.message.from_user.first_name}: {callback_data}")
    user_id = callback_query.from_user.id
    message_ = await callback_query.message.edit_reply_markup(
        reply_markup=StationSelector.markup(user_id=user_id, callback_data=callback_data)
    )
    MessageBox.put(message=message_, user_id=user_id)


@dp.callback_query_handler(
    StationSelector.data.filter(action=StationSelector.actions.back),
    state=[States.select_departure_station, States.select_arrival_station],
)
async def back_departure(callback_query, state: FSMContext):
    print(f"{callback_query.message.from_user.first_name}: {callback_query.data}")
    user_id = callback_query.from_user.id
    StationSelector.clear(user_id)
    await MessageBox.delete_last(user_id)

    await callback_query.message.answer(
        f"Введите название пункта "
        f"{'отправления' if await state.get_state() == 'States:select_departure_station' else 'прибытия'}: ✏️"
    )
    await States.previous()


@dp.callback_query_handler(
    StationSelector.data.filter(action=StationSelector.actions.select), state=States.select_departure_station
)
async def waiting_for_arrival_station(callback_query, callback_data):
    print(f"{callback_query.message.from_user.first_name}: {callback_data}")
    user_id = callback_query.from_user.id
    await dp.storage.set_data(user=user_id, data=dict(departure=callback_data["station_code"]))
    StationSelector.clear(user_id)
    await MessageBox.delete_last(user_id)
    message_ = await callback_query.message.answer(text="Отлично!\nТеперь введите название пункта прибытия: ✏️")
    MessageBox.put(message=message_, user_id=user_id)
    await States.waiting_for_arrival_station.set()


@dp.callback_query_handler(
    StationSelector.data.filter(action=StationSelector.actions.select), state=States.select_arrival_station
)
async def stations_done(callback_query, callback_data):
    print(f"{callback_query.message.from_user.first_name}: {callback_data}")
    user_id = callback_query.from_user.id
    data = await dp.storage.get_data(user=user_id)
    data["arrival"] = callback_data["station_code"]
    await dp.storage.set_data(user=user_id, data=data)
    StationSelector.clear(user_id)
    await MessageBox.delete_last(user_id)

    DateSelector.setup(user_id=user_id)
    message_ = await callback_query.message.answer(
        "Выберите дату отправления:", reply_markup=DateSelector.markup(user_id)
    )
    MessageBox.put(message=message_, user_id=user_id)
    await States.select_date.set()


@dp.callback_query_handler(
    DateSelector.data.filter(
        action=[DateSelector.actions.next_month, DateSelector.actions.prev_month, DateSelector.actions.select_day]
    ),
    state=States.select_date,
)
async def calendar_selection(callback_query: CallbackQuery, callback_data: dict):
    print(f"{callback_query.message.from_user.first_name}: {callback_data}")
    user_id = callback_query.from_user.id
    if user_id in DateSelector.users():
        message_ = await callback_query.message.edit_reply_markup(
            DateSelector.markup(user_id=user_id, callback_data=callback_data)
        )
        MessageBox.put(message=message_, user_id=user_id)
    else:
        await callback_query.answer()


@dp.callback_query_handler(DateSelector.data.filter(action=DateSelector.actions.confirm), state=States.select_date)
async def calendar_selection(callback_query: CallbackQuery, callback_data: dict):
    print(f"{callback_query.message.from_user.first_name}: {callback_data}")
    user_id = callback_query.from_user.id

    date_ = datetime(day=int(callback_data["day"]), month=int(callback_data["month"]), year=int(callback_data["year"]))
    data = await dp.storage.get_data(user=user_id)
    data["date"] = date_
    await dp.storage.set_data(user=user_id, data=data)

    await callback_query.message.answer(text="Интересуют ли Вас места для инвалидов?", reply_markup=yes_no_keyboard)
    await States.waiting_for_disabled.set()

    # await MessageBox.delete_last(user_id=user_id)
    # wait_message = await callback_query.message.answer(text="Выполнен запрос на выбранную дату, ожидайте...")
    # await ChatActions.typing()
    #
    # data = await dp.storage.get_data(user=user_id)
    # trains = await get_trains(
    #     code0=data["departure"],
    #     code1=data["arrival"],
    #     date_=date_,
    # )
    #
    # await wait_message.delete()
    # if not trains:
    #     message_ = await callback_query.message.answer(
    #         text="По данному маршруту на выбранную дату не найдено ни одного прямого билета.\n"
    #         "Попробуйте выбрать другую дату:",
    #         reply_markup=DateSelector.markup(user_id),
    #     )
    #     MessageBox.put(message=message_, user_id=user_id)
    #     await States.select_date.set()
    #     return
    # DateSelector.clear(user_id=user_id)

    # sorted_trains = sorted_trains_by_price(trains)
    # TrainsNavigator.setup(trains=sorted_trains, user_id=user_id)
    # text, markup = TrainsNavigator.text_and_markup(user_id=user_id)
    # await callback_query.message.answer(text=text, reply_markup=markup)
    # await state.finish()


@dp.callback_query_handler(
    TrainsNavigator.data.filter(action=[TrainsNavigator.actions.next, TrainsNavigator.actions.prev]),
    state="*",
)
async def trains_navigation(callback_query: CallbackQuery, callback_data):
    print(f"{callback_query.message.from_user.first_name}: {callback_data}")
    user_id = callback_query.from_user.id
    text, markup = TrainsNavigator.text_and_markup(user_id=user_id, callback_data=callback_data)
    if not text or not markup:
        await callback_query.answer()
        return
    await callback_query.message.edit_text(text=text)
    message_ = await callback_query.message.edit_reply_markup(reply_markup=markup)
    MessageBox.put(message=message_, user_id=user_id)
