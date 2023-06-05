import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a bot instance
bot = Bot(token="5233363509:AAEFSLOH94rsoQUXopSKc1p-e_aQB5mlpxI")

# Create a dispatcher instance
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Define the echo command handler
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hello! I'm an echo bot. Send me a message and I'll echo it back to you.")

# Define the echo message handler
@dp.message_handler()
async def echo_message(message: types.Message):
    await message.answer(message.text)

# Start the bot
async def main():
    try:
        # Start the bot
        await dp.start_polling()
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    # Run the main function
    asyncio.run(main())
