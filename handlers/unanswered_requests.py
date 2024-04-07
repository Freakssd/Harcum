import datetime
import time

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, MediaGroup
from handlers import order_handlers as ord
from handlers import start_lang_handlers as stas
import config as cfg
from create_bot import bot
from db import BotDB, bot_db, bot_car

bot_car = bot_car()
BotDB = BotDB()


async def un(lst, user_id):
    global txt, uns
    language = BotDB.get_user_lang(user_id)
    for idd in lst:
        data = bot_car.get_data_by_idd(idd)
        print(data)
        if language == 'ru':
            txt = f'''
Запрос №{idd}\n
{', '.join(data[1:4])}\n
Объем двигателя - {data[4]}
Мощность двигателя - {data[5]}
Кузов - {data[6]}
КПП - {data[7]}
Тип двигателя - {data[8]}
Привод авто - {data[9]}

Запчасть/деталь -  {data[12]}'''
            uns = "ОТВЕТИТЬ"
        elif language == 'am':
            uns = "Պատասխանել"
            txt = f'''
Հարցում  № #{idd}\n
{', '.join(data[1:4])}\n
Շարժիչի ծավալը - {data[4]}
Շարժիչի հզորությունը - {data[5]}
Մարմին - {data[6]}
PPC - {data[7]}
Շարժիչի տեսակը - {data[8]}
Ավտո drive - {data[9]}

Մաս -  {data[12]}'''

        keyboard = InlineKeyboardMarkup(row_width=1)
        button1 = InlineKeyboardButton(text=uns, callback_data=f"uns={idd}")
        keyboard.add(button1)
        try:
            if data[10] is not None:
                media = [types.InputMediaPhoto(media=data[10],
                                               caption=txt)]
                if data[11] is not None:
                    media.append(types.InputMediaPhoto(media=data[11]))
                try:
                    messl = await bot.send_media_group(chat_id=user_id, media=media)
                    rf = await bot.send_message(chat_id=user_id, text=f"#{idd}", reply_markup=keyboard)
                except:
                    pass
            else:
                await bot.send_message(user_id, txt, reply_markup=keyboard)
            time.sleep(0.1)
        except Exception as e:
            pass


async def unanswered(message: types.Message):
    global uns
    user_id = message.from_user.id
    if user_id in cfg.ban_list:
        return await bot.send_message(user_id, 'BAN')
    k = BotDB.get_user_phone(user_id)
    language = BotDB.get_user_lang(user_id)
    if k is None:
        return await get_phone(message)

    lst = bot_car.get_idd_by_status("unanswered")[::-1][:10]
    print(lst)
    await un(lst, user_id)
    if language == 'ru':
        uns = 'еще запросы'
    elif language == 'am':
        uns = "Այլ հարցումներ"
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text=uns, callback_data=f"uns213")
    keyboard.add(button1)
    await bot.send_message(user_id, '-------', reply_markup=keyboard)


async def unanswered_and_call(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lst = bot_car.get_idd_by_status("unanswered")[::-1][10:25]
    await un(lst, user_id)


async def unanswered_call(callback_query: types.CallbackQuery):
    idd = callback_query.data.split('=')[1]
    user_id = callback_query.from_user.id

    # Получаем предпочтение языка из базы данных на основе user_id
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        keyboard = ru_change_keyboard(idd)

    elif language == 'am':
        keyboard = am_change_keyboard(idd)
    else:
        return print('ERROR')
    await bot.send_message(user_id, f"#{idd}", reply_markup=keyboard)


def ru_change_keyboard(idd):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="✅ЕСТЬ НОВАЯ ОРИГИНАЛ", callback_data=f"neworig_{idd}")
    button2 = InlineKeyboardButton(text="✅ЕСТЬ Б/У ОРИГИНАЛ", callback_data=f"baorig_{idd}")
    button3 = InlineKeyboardButton(text="✅ЕСТЬ НОВАЯ КОПИЯ", callback_data=f"newcopy_{idd}")
    button4 = InlineKeyboardButton(text="✅ЕСТЬ Б/У КОПИЯ", callback_data=f"bacopy_{idd}")
    button6 = InlineKeyboardButton(text="❌Нет в наличии такой запчасти", callback_data=f"NOT_{idd}")
    keyboard.add(button1, button2, button3, button4, button6)
    return keyboard


def am_change_keyboard(idd):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="✅ԿԱ ՆՈՐ ԲՆՕՐԻՆԱԿ", callback_data=f"neworig_{idd}")
    button2 = InlineKeyboardButton(text="✅ՕԳՏԱԳՈՐԾՎԱԾ ԲՆՕՐԻՆԱԿ ԿԱ", callback_data=f"baorig_{idd}")
    button3 = InlineKeyboardButton(text="✅ԿԱ ՆՈՐ ՊԱՏՃԵՆ", callback_data=f"newcopy_{idd}")
    button4 = InlineKeyboardButton(text="✅ԿԱ ՕԳՏԱԳՈՐԾՎԱԾ ՊԱՏՃԵՆ", callback_data=f"bacopy_{idd}")
    button6 = InlineKeyboardButton(text="❌Նման պահեստամասեր մատչելի չեն", callback_data=f"NOT_{idd}")
    keyboard.add(button1, button2, button3, button4, button6)
    return keyboard


class ADD_PHONE(StatesGroup):
    num = State()


async def get_phone(message: types.Message):
    global txt
    user_id = message.from_user.id
    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        txt = cfg.ru_j
    elif language == 'am':
        txt = cfg.am_j
    await ADD_PHONE.num.set()
    await bot.send_message(user_id, txt)


async def process_get_phone(message: types.Message, state: FSMContext):
    num = message.text
    await state.finish()
    user_id = message.from_user.id
    BotDB.load_phone(user_id, num)
    await bot.send_message(user_id, 'phone access')
    await unanswered(message)


def register_handlers_unanswered_requests(dp: Dispatcher):
    dp.register_message_handler(unanswered, commands=['unanswered'])
    dp.register_message_handler(get_phone, commands=['GET-phone'])
    dp.register_message_handler(process_get_phone, state=ADD_PHONE.num)
    dp.register_callback_query_handler(unanswered_call, lambda c: c.data.startswith('uns='))
    dp.register_callback_query_handler(unanswered_and_call, lambda c: c.data.startswith('uns213'))
