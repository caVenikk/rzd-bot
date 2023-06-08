import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ["TOKEN"], parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
