from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config as cfg
bot = Bot(token=cfg.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
