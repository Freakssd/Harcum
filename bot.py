import logging
import datetime
from aiogram import types
from create_bot import dp, bot
from handlers import start_lang_handlers, order_handlers, reg_handlers, quick_handlers, disassembly_handlers, \
    car_disassembly_handlers
from db import BotDB, bot_db

bot_db = bot_db()
BotDB = BotDB()
now = datetime.datetime.now()

disassembly_handlers.register_handlers_disassembly(dp)
reg_handlers.register_handlers_reg(dp)
order_handlers.register_handlers_order(dp)
start_lang_handlers.register_handlers_start(dp)
car_disassembly_handlers.register_handlers_car_disassembly(dp)

logging.basicConfig(level=logging.INFO)

# бд


if __name__ == '__main__':
    from aiogram import executor
    try:
        executor.start_polling(dp)
    except Exception as e:
        logging.exception("Ошибка в работе бота")

