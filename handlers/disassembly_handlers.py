import tracemalloc
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup

import config as cfg
from db_cars import CarsDB
from db import BotDB, bot_car, bot_db
from create_bot import bot

tracemalloc.start()

cars_db = CarsDB()
BotDB = BotDB()
bot_car = bot_car()
bot_db = bot_db()

stop_list = ['\start', '/start', '/stop', '/order', 'Запрос', 'Автосервисы (скоро)', 'Авто в разборе',
             'Аккаунт авторазборки',
             '/quick', '/disassembly', '/feedback', '/language', '/login', '/account', 'Авторизация автразборки',
             'Հարցում', 'Ավտոսպասարկում (շուտով)', 'Ավտո վերլուծության մեջ', 'Թույլտվություն ինքնահավաք',
             'ինքնահավաք հաշիվ']


async def order_switch(message: types.Message, s=0):
    global kl, keyboard03
    try:
        user_id = message.from_user.id
        if user_id in cfg.ban_list:
            return await bot.send_message(user_id, 'BAN')

        return await disassembly(message)
        # ... (остальной код функции)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


# Старт запроса
async def disassembly(message: types.Message):
    try:
        user_id = message.from_user.id

        # Получаем предпочтение языка из базы данных на основе user_id
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            keyboard04 = generate_brands_inline_keyboard()
            await bot.send_message(user_id, "Выберите марку авто из списка:", reply_markup=keyboard04)
        elif language == 'am':
            keyboard04 = generate_brands_inline_keyboard()
            await bot.send_message(user_id, "ընտրեք մակնիշը ավտոմեքենայի:", reply_markup=keyboard04)
        else:
            # Логика для языка по умолчанию (английский или другой)
            await bot.send_message(user_id, 'Выберите язык / Ընտրեք լեզուն: - /language')
            # Остальная логика для языка по умолчанию

    except Exception as e:
        # Обработка исключения
        print(f"11Произошла ошибка: {e}")
        await message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


# Генерация инлайн кнопок
def generate_brands_inline_keyboard():
    try:
        keyboard_brands = InlineKeyboardMarkup(row_width=4)
        car_brands = cars_db.firms()
        buttons = []
        for i, brand in enumerate(car_brands):
            if i == len(car_brands) - 1:
                button = InlineKeyboardButton(text=brand, callback_data=f"firms|d-|{brand}",
                                              resize_keyboard=True)
            else:
                button = InlineKeyboardButton(text=brand, callback_data=f"firms|d-|{brand}")
            buttons.append(button)

        keyboard_brands.add(*buttons)
        return keyboard_brands

    except Exception as e:
        # Обработка исключения
        print(f"22Произошла ошибка: {e}")


async def models_callback_button(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        firm = callback_query.data.split('|d-|')[1]
        models = cars_db.models_by_firm(firm)
        print(models)
        print(len(models))

        # Разделение списка на части по 100 элементов
        button_chunks = [models[i:i + 100] for i in range(0, len(models), 100)]

        # Создание встроенной клавиатуры
        keyboard05 = types.InlineKeyboardMarkup(row_width=3)

        # Добавление кнопок из каждой части списка и отправка сообщений
        for chunk in button_chunks:
            buttons = [types.InlineKeyboardButton(text=model, callback_data=f"omodel\d-/{model}\d-/{firm}") for
                       model in chunk]
            keyboard05.add(*buttons)

            language = BotDB.get_user_lang(user_id)

            if language == 'ru':
                await bot.send_message(callback_query.from_user.id, cfg.ru_change, reply_markup=keyboard05)
            else:
                await bot.send_message(callback_query.from_user.id, cfg.am_change, reply_markup=keyboard05)

            # Очищаем клавиатуру для следующего сообщения
            keyboard05 = types.InlineKeyboardMarkup(row_width=3)
    except Exception as e:
        # Обработка исключения
        print(f"33Произошла ошибка: {e}")
        await callback_query.message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


# @dp.callback_query_handler(lambda c: c.data.startswith('model:'))
async def years_callback_button(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    language = BotDB.get_user_lang(user_id)
    model = callback_query.data.split('\d-/')[1]
    firm = callback_query.data.split('\d-/')[2]

    gens = cars_db.years_by_model_and_firm(firm, model)

    keyboard06 = InlineKeyboardMarkup(row_width=1)
    buttons = list()

    for gen in gens:
        button = InlineKeyboardButton(text=gen, callback_data=f"gens_d-_{gen}_d-_{model}_d-_{firm}")
        buttons.append(button)

    keyboard06.add(*buttons)
    if language == 'ru':
        await bot.send_message(callback_query.from_user.id, cfg.ru_change, reply_markup=keyboard06)
    else:
        await bot.send_message(callback_query.from_user.id, cfg.am_change, reply_markup=keyboard06)


class Configuration(StatesGroup):
    sta = State()
    brand = State()
    model = State()
    gen = State()
    c = State()
    part_photo_start = State()
    part_photo_process = State()
    pts_photo = State()
    engine_displacement = State()
    motor_power = State()
    car_body = State()
    auto_transmission = State()
    engine = State()
    drive = State()
    code = State()
    codes = State()
    engine_code = State()
    body_code = State()
    part = State()
    met = State()
    k = ()


async def year_callback_button(callback_query: types.CallbackQuery):
    global ed, met_2, met_1, met
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        firm = callback_query.data.split('_d-_')[3]
        model = callback_query.data.split('_d-_')[2]
        gen = callback_query.data.split('_d-_')[1]

        c = '_' + firm + ', ' + model + ', ' + gen + '_'
        await bot.send_message(user_id, c, parse_mode="Markdown")
        print(firm, model, gen)
        car_id = cars_db.get_car_id(firm, model, gen)
        print(car_id)
        if car_id is None:
            return await bot.send_message(user_id, f"Car is not found, Contact support: {cfg.support}")
        logins_list = bot_car.get_logins_by_car_id(str(car_id))
        print(logins_list)
        if logins_list is not None and len(logins_list) != 0:
            print(logins_list)

    except:
        pass


def register_handlers_disassembly(dp: Dispatcher):
    dp.register_message_handler(disassembly, commands=['disassembly'])
    dp.register_callback_query_handler(models_callback_button, lambda c: c.data.startswith('firms|d-|'))
    dp.register_callback_query_handler(years_callback_button, lambda c: c.data.startswith('omodel\d-/'))
    dp.register_callback_query_handler(year_callback_button, lambda c: c.data.startswith('gens_d-_'))
