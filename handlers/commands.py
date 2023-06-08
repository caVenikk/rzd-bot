from aiogram.types import Message

from loader import dp
from utils import MessageBox
from utils.states import States


@dp.message_handler(commands=["start", "help"])
async def start_and_help(message: Message):
    print(f"{message.from_user.first_name}: {message.text}")
    await message.answer(
        "<b>Приветствую!</b>\nДанный бот создан для поиска самых дешевых железнодорожных билетов. 🔍\n"
        "Чтобы воспользоваться поиском, введите команду <b>/find</b>"
    )


@dp.message_handler(commands=["find"], state="*")
async def find_ticket(message: Message):
    print(f"{message.from_user.first_name}: {message.text}")
    message_ = await message.answer(text="Приступим к поиску! 🔍\nВведите название пункта отправления:")
    MessageBox.put(message=message_, user_id=message.from_user.id)
    await States.waiting_for_departure_station.set()
