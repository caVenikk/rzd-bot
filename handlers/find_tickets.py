from aiogram.types import Message, ChatActions

from keyboards import StationSelector
from loader import dp
from services.api import get_stations
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
