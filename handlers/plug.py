from aiogram.types import CallbackQuery

from loader import dp


@dp.callback_query_handler(text=["_"], state="*")
async def plug(callback_query: CallbackQuery):
    print(f"{callback_query.message.from_user.first_name}: plug")
    await callback_query.answer()
