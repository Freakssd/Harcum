from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from handlers import reg_handlers
from create_bot import bot
from db import BotDB, bot_db
from create_bot import dp

bot_db = bot_db()
BotDB = BotDB()
# НАХ НЕ НАДО
