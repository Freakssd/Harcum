import asyncio
import logging
import datetime
from aiogram import types
from create_bot import dp, bot
from handlers import start_lang_handlers, order_handlers, reg_handlers, quick_handlers, disassembly_handlers, \
    car_disassembly_handlers, admin_panel, unanswered_requests
from db import BotDB, bot_db
from db_cars import CarsDB

cars_db = CarsDB()
bot_db = bot_db()
BotDB = BotDB()


disassembly_handlers.register_handlers_disassembly(dp)
reg_handlers.register_handlers_reg(dp)
order_handlers.register_handlers_order(dp)
start_lang_handlers.register_handlers_start(dp)
car_disassembly_handlers.register_handlers_car_disassembly(dp)
admin_panel.register_handlers_admin_panel(dp)
unanswered_requests.register_handlers_unanswered_requests(dp)
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    from aiogram import executor
    try:
        executor.start_polling(dp)
    except Exception as e:
        datetime.datetime.now()
        logging.exception("Ошибка в работе бота")

