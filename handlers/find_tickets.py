from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ChatActions, ReplyKeyboardRemove

from keyboards import StationSelector, DateSelector, TrainsNavigator
from loader import dp
from services.api import get_stations, get_trains
from services.filters import sorted_trains_by_price, filtered_without_disabled
from utils import MessageBox
from utils.states import States


@dp.message_handler(state=[States.waiting_for_departure_station, States.waiting_for_arrival_station])
async def station_input(message: Message):
    print(f"{message.from_user.first_name}: {message.text}")
    user_id = message.from_user.id
    await ChatActions.typing()
    await MessageBox.delete_last(user_id=user_id)
    stations = await get_stations(query=message.text)
    if not stations:
        await message.answer(
            text=f"<i>По запросу</i> <b>«{message.text}»</b> <i>ничего не найдено.</i>\n Попробуйте снова:"
        )
        return
    StationSelector.setup(stations=stations, user_id=user_id)

    message_ = await message.answer(
        text=f"<i>Результаты по запросу</i> <b>«{message.text}»</b>:",
        reply_markup=StationSelector.markup(user_id=user_id),
    )

    MessageBox.put(message=message_, user_id=user_id)

    await States.next()


@dp.message_handler(text=["Да", "Нет"], state=States.waiting_for_disabled)
async def disabled_answer(message: Message, state: FSMContext):
    print(f"{message.from_user.first_name}: {message.text}")
    user_id = message.from_user.id

    remove_keyboard_message = await message.answer("-", reply_markup=ReplyKeyboardRemove())
    await remove_keyboard_message.delete()

    disabled_person = True if message.text == "Да" else False

    await MessageBox.delete_last(user_id=user_id)
    wait_message = await message.answer(text="Выполнен запрос на выбранную дату, ожидайте...")
    await ChatActions.typing()

    data = await dp.storage.get_data(user=user_id)
    trains = await get_trains(
        code0=data["departure"],
        code1=data["arrival"],
        date_=data["date"],
    )

    await wait_message.delete()
    if not trains:
        message_ = await message.answer(
            text="По данному маршруту на выбранную дату не найдено ни одного прямого билета.\n"
            "Попробуйте выбрать другую дату:",
            reply_markup=DateSelector.markup(user_id),
        )
        MessageBox.put(message=message_, user_id=user_id)
        await States.select_date.set()
        return
    DateSelector.clear(user_id=user_id)

    if not disabled_person:
        trains = filtered_without_disabled(trains)

    sorted_trains = sorted_trains_by_price(trains)
    TrainsNavigator.setup(trains=sorted_trains, user_id=user_id)
    text, markup = TrainsNavigator.text_and_markup(user_id=user_id)
    await message.answer(text=text, reply_markup=markup)
    await state.finish()
