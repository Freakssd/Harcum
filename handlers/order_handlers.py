import asyncio
import datetime
import tracemalloc
import random
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ContentType
from aiogram.utils import json

from handlers import start_lang_handlers as stas
import config as cfg
from db_cars import CarsDB
from db import BotDB, bot_car, bot_db
from create_bot import bot
from create_bot import dp as DP

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

        return await order(message)
        # ... (остальной код функции)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


# Старт запроса
async def order(message: types.Message):
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
                button = InlineKeyboardButton(text=brand, callback_data=f"firms|-|{brand}",
                                              resize_keyboard=True)
            else:
                button = InlineKeyboardButton(text=brand, callback_data=f"firms|-|{brand}")
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
        firm = callback_query.data.split('|-|')[1]
        models = cars_db.models_by_firm(firm)
        print(models)
        print(len(models))

        # Разделение списка на части по 100 элементов
        button_chunks = [models[i:i + 100] for i in range(0, len(models), 100)]

        # Создание встроенной клавиатуры
        keyboard05 = types.InlineKeyboardMarkup(row_width=3)

        # Добавление кнопок из каждой части списка и отправка сообщений
        for chunk in button_chunks:
            buttons = [types.InlineKeyboardButton(text=model, callback_data=f"omodel\-/{model}\-/{firm}") for
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
    model = callback_query.data.split('\-/')[1]
    firm = callback_query.data.split('\-/')[2]

    gens = cars_db.years_by_model_and_firm(firm, model)

    keyboard06 = InlineKeyboardMarkup(row_width=1)
    buttons = list()

    for gen in gens:
        button = InlineKeyboardButton(text=gen, callback_data=f"gens_-_{gen}_-_{model}_-_{firm}")
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
        firm = callback_query.data.split('_-_')[3]
        model = callback_query.data.split('_-_')[2]
        gen = callback_query.data.split('_-_')[1]

        c = '_' + firm + ', ' + model + ', ' + gen + '_'
        await bot.send_message(user_id, c, parse_mode="Markdown")

        language = BotDB.get_user_lang(user_id)
        if language == 'ru':
            met = cfg.ru_met
            met_1 = cfg.ru_met_1
            met_2 = cfg.ru_met_2
        elif language == 'am':
            met = cfg.am_met
            met_1 = cfg.am_met_1
            met_2 = cfg.am_met_2
        print("тут")
        keyboard07 = InlineKeyboardMarkup(row_width=1)
        buttons = list()
        button1 = InlineKeyboardButton(text=met_1, callback_data=f"method_=_{'1'}_=_{gen}_=_{model}_=_{firm}")
        button2 = InlineKeyboardButton(text=met_2, callback_data=f"method_=_{'2'}_=_{gen}_=_{model}_=_{firm}")
        buttons.append(button1)
        buttons.append(button2)
        keyboard07.add(*buttons)
        if language == 'ru':
            await bot.send_message(callback_query.from_user.id, met, reply_markup=keyboard07)
        else:
            await bot.send_message(callback_query.from_user.id, met, reply_markup=keyboard07)
        print("finish")

    except Exception as e:
        print(f'error - {e}')


async def method_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    global ed, photo_mess
    await callback_query.message.delete()

    user_id = callback_query.from_user.id

    firm = callback_query.data.split('_=_')[4]
    model = callback_query.data.split('_=_')[3]
    gen = callback_query.data.split('_=_')[2]
    method = callback_query.data.split('_=_')[1]

    await Configuration.brand.set()
    await state.update_data(brand=firm)
    await Configuration.model.set()
    await state.update_data(model=model)
    await Configuration.gen.set()
    await state.update_data(gen=gen)

    c = firm + ', ' + model + ', ' + gen
    await Configuration.c.set()
    await state.update_data(c=c)

    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        ed = cfg.ru_ed
        photo_mess = cfg.ru_photo

    elif language == 'am':
        ed = cfg.am_ed
        photo_mess = cfg.am_photo

    if method == '2':
        await Configuration.engine_displacement.set()
        await bot.send_message(user_id, ed)
    else:
        await Configuration.pts_photo.set()
        await bot.send_message(user_id, photo_mess)


async def pts_photo(message: types.Message, state: FSMContext):
    global pt, met_1, met_2

    user_id = message.from_user.id
    language = BotDB.get_user_lang(user_id)

    # Получаем информацию о фото
    file_id_1 = message.photo[-1].file_id
    await state.update_data(pts_photo=file_id_1)
    await message.delete()
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        met_1 = "Отправить фото запчасти"
        met_2 = "Продолжить без фото"
    elif language == 'am':
        met_1 = ""
        met_2 = "Продолжить без фото"

    keyboard077 = InlineKeyboardMarkup(row_width=1)
    buttons = list()
    button1 = InlineKeyboardButton(text=met_1, callback_data=f"partmethod_o_{1}")
    button2 = InlineKeyboardButton(text=met_2, callback_data=f"partmethod_o_{2}")
    buttons.append(button1)
    buttons.append(button2)
    keyboard077.add(*buttons)
    await Configuration.part_photo_start.set()
    await bot.send_message(user_id, '~', reply_markup=keyboard077)


async def part_method_callback_button(callback_query: types.CallbackQuery):
    global pt, ph_pt
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    language = BotDB.get_user_lang(user_id)

    part_method = callback_query.data.split('_o_')[1]
    print(part_method)
    if language == 'ru':
        pt = cfg.ru_pt
        ph_pt = cfg.ru_pt_photo

    elif language == 'am':
        pt = cfg.am_pt
        ph_pt = cfg.am_pt_photo
    if part_method == "2":

        await Configuration.part.set()
        await bot.send_message(user_id, pt)
    else:
        await Configuration.part_photo_process.set()
        await bot.send_message(user_id, ph_pt)


async def part_photo_process(message: types.Message, state: FSMContext):
    global pt

    user_id = message.from_user.id
    language = BotDB.get_user_lang(user_id)
    # Получаем информацию о фото
    file_id_1 = message.photo[-1].file_id
    await state.update_data(part_photo_process=file_id_1)
    await message.delete()

    if language == 'ru':
        pt = cfg.ru_pt

    elif language == 'am':
        pt = cfg.am_pt

    await Configuration.part.set()
    await bot.send_message(user_id, pt)


async def process_engine_displacement(message: types.Message, state: FSMContext):
    global ep
    try:
        await message.delete()
        user_id = message.from_user.id
        await bot.delete_message(user_id, message.message_id - 1)
        language = BotDB.get_user_lang(user_id)
        engine_displacement = message.text

        if engine_displacement in stop_list:
            await state.finish()
            if language == 'ru':
                await bot.send_message(user_id, 'Запрос прерван')
            elif language == 'am':
                await bot.send_message(user_id, 'Հարցումն ընդհատվել է')
            return await stas.start(message, state)

        await state.update_data(engine_displacement=engine_displacement)
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            ep = cfg.ru_ep
        elif language == 'am':
            ep = cfg.am_ep

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + engine_displacement
        await state.update_data(c=c)
        await Configuration.motor_power.set()
        await bot.send_message(user_id, ep)
    except Exception as e:
        print(f'process_engine_displacement error - {e}')
        await state.finish()


async def process_motor_power(message: types.Message, state: FSMContext):
    global keyboard11, cb, st
    try:

        await message.delete()
        user_id = message.from_user.id
        await bot.delete_message(user_id, message.message_id - 1)
        motor_power = message.text
        language = BotDB.get_user_lang(user_id)

        if motor_power in stop_list:
            await state.finish()
            if language == 'ru':
                await bot.send_message(user_id, 'Запрос прерван')
            elif language == 'am':
                await bot.send_message(user_id, 'Հարցումն ընդհատվել է')
            return await stas.start(message, state)
        await state.update_data(motor_power=motor_power)
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            cb = cfg.ru_cb
            st = cfg.ru_st
            keyboard11 = ru_car_body_keyboard()
        elif language == 'am':
            cb = cfg.am_cb
            st = cfg.am_st
            keyboard11 = am_car_body_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + motor_power + st
        await state.update_data(c=c)
        await Configuration.car_body.set()
        await bot.send_message(user_id, cb, reply_markup=keyboard11)
    except Exception as e:
        print(f'process_motor_power error - {e}')
        await state.finish()


def ru_car_body_keyboard():
    keyboard13 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Седан", callback_data="Sedan")
    button2 = InlineKeyboardButton(text="Хэтчбек 3 дв.", callback_data="Хэтчбек 3 дв.")
    button3 = InlineKeyboardButton(text="Хэтчбек 5 дв.", callback_data="Хэтчбек 5 дв.")
    button4 = InlineKeyboardButton(text="Лифтбек", callback_data="Лифтбек")
    button5 = InlineKeyboardButton(text="Внедорожник 3 дв.", callback_data="Внедорожник 3 дв.")
    button6 = InlineKeyboardButton(text="Внедорожник 5 дв.", callback_data="Внедорожник 5 дв.")
    button7 = InlineKeyboardButton(text="Универсал", callback_data="Универсал")
    button9 = InlineKeyboardButton(text="Купе", callback_data="Купе")
    button10 = InlineKeyboardButton(text="Минивэн", callback_data="Минивэн")
    button11 = InlineKeyboardButton(text="Пикап", callback_data="Пикап")
    button12 = InlineKeyboardButton(text="Лимузин", callback_data="Лимузин")
    button13 = InlineKeyboardButton(text="Фургон", callback_data="Фургон")
    button14 = InlineKeyboardButton(text="Кабриолет", callback_data="Кабриолет")
    keyboard13.add(button1, button2, button3, button4, button5, button6, button7, button9, button10, button11,
                   button12, button13, button14)
    return keyboard13


def am_car_body_keyboard():
    keyboard14 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Սեդան", callback_data="Սեդան")
    button2 = InlineKeyboardButton(text="Հեչբեկ 3 դռներ", callback_data="Հեչբեկ 3 դռներ")
    button3 = InlineKeyboardButton(text="Հեչբեկ 5 դուռ", callback_data="Հեչբեկ 5 դուռ")
    button4 = InlineKeyboardButton(text="Liftbek", callback_data="Liftbek")
    button5 = InlineKeyboardButton(text="Ամենագնաց 3 դռներ", callback_data="Ամենագնաց 3 դռներ")
    button6 = InlineKeyboardButton(text="Ամենագնաց 5 դուռ", callback_data="Ամենագնաց 5 դուռ")
    button7 = InlineKeyboardButton(text="Ունիվերսալ", callback_data="Ունիվերսալ")
    button9 = InlineKeyboardButton(text="Կուպե", callback_data="Կուպե")
    button10 = InlineKeyboardButton(text="Մինիվեն", callback_data="Մինիվեն")
    button11 = InlineKeyboardButton(text="Պիկապ", callback_data="Պիկապ")
    button12 = InlineKeyboardButton(text="Լիմուզին", callback_data="Լիմուզին")
    button13 = InlineKeyboardButton(text="Վան", callback_data="Վան")
    button14 = InlineKeyboardButton(text="Փոխարկելի", callback_data="Փոխարկելի")
    keyboard14.add(button1, button2, button3, button4, button5, button6, button7, button9, button10, button11,
                   button12, button13, button14)
    return keyboard14


async def car_body_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global at, keyboard34
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        car_body = callback_query.data
        await state.update_data(car_body=car_body)
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            at = cfg.ru_at
            keyboard34 = ru_auto_transmission_keyboard()
        elif language == 'am':
            at = cfg.am_at
            keyboard34 = am_auto_transmission_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + car_body
        await state.update_data(c=c)
        await Configuration.auto_transmission.set()
        await bot.send_message(user_id, at, reply_markup=keyboard34)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_auto_transmission_keyboard():
    keyboard35 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Автоматическая", callback_data="Автоматическая")
    button2 = InlineKeyboardButton(text="Робот", callback_data="Робот")
    button3 = InlineKeyboardButton(text="Вариатор", callback_data="Вариатор")
    button5 = InlineKeyboardButton(text="Механическая", callback_data="Механическая")
    keyboard35.add(button1, button2, button3, button5)
    return keyboard35


def am_auto_transmission_keyboard():
    keyboard36 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Ավտոմատ", callback_data="Ավտոմատ")
    button2 = InlineKeyboardButton(text="Ռոբոտ", callback_data="Ռոբոտ")
    button3 = InlineKeyboardButton(text="Վարիատոր", callback_data="Վարիատոր")
    button5 = InlineKeyboardButton(text="Մեխանիկական", callback_data="Մեխանիկական")
    keyboard36.add(button1, button2, button3, button5)
    return keyboard36


async def auto_transmission_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global et, keyboard37
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        auto_transmission = callback_query.data
        await state.update_data(auto_transmission=auto_transmission)

        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            et = cfg.ru_et
            keyboard37 = ru_engine_keyboard()
        elif language == 'am':
            et = cfg.am_et
            keyboard37 = am_engine_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + auto_transmission
        await state.update_data(c=c)
        await Configuration.engine.set()
        await bot.send_message(user_id, et, reply_markup=keyboard37)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_engine_keyboard():
    keyboard15 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Бензин", callback_data="Бензин")
    button2 = InlineKeyboardButton(text="Дизель", callback_data="Дизель")
    button3 = InlineKeyboardButton(text="Гибрид", callback_data="Гибрид")
    button4 = InlineKeyboardButton(text="Электро", callback_data="Электро")
    button5 = InlineKeyboardButton(text="Газ", callback_data="Газ")
    keyboard15.add(button1, button2, button3, button4, button5)
    return keyboard15


def am_engine_keyboard():
    keyboard16 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Բենզին", callback_data="Բենզին")
    button2 = InlineKeyboardButton(text="Դիզել", callback_data="Դիզել")
    button3 = InlineKeyboardButton(text="Հիբրիդ", callback_data="Հիբրիդ")
    button4 = InlineKeyboardButton(text="Էլեկտրո", callback_data="Էլեկտրո")
    button5 = InlineKeyboardButton(text="Գազ", callback_data="Գազ")
    keyboard16.add(button1, button2, button3, button4, button5)
    return keyboard16


async def engine_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global keyboard17, d
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        engine = callback_query.data
        await state.update_data(engine=engine)

        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            d = cfg.ru_d
            keyboard17 = ru_drive_keyboard()
        elif language == 'am':
            d = cfg.am_d
            keyboard17 = am_drive_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + engine
        await state.update_data(c=c)
        await Configuration.drive.set()
        await bot.send_message(user_id, d, reply_markup=keyboard17)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_drive_keyboard():
    keyboard18 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Передний", callback_data="Передний")
    button2 = InlineKeyboardButton(text="Задний", callback_data="Задний")
    button3 = InlineKeyboardButton(text="Полный", callback_data="Полный")

    keyboard18.add(button1, button2, button3)
    return keyboard18


def am_drive_keyboard():
    keyboard19 = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Ճակատ", callback_data="Ճակատ")
    button2 = InlineKeyboardButton(text="Հետեւի", callback_data="Հետեւի")
    button3 = InlineKeyboardButton(text="Ֆուլլ", callback_data="Ֆուլլ")

    keyboard19.add(button1, button2, button3)
    return keyboard19


async def drive_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global pt1, met_1, met_2
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        drive = callback_query.data
        await state.update_data(drive=drive)
        language = BotDB.get_user_lang(user_id)
        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + drive

        await state.update_data(c=c)

        if language == 'ru':
            met_1 = "Отправить фото запчасти"
            met_2 = "Продолжить без фото"
        elif language == 'am':
            met_1 = ""
            met_2 = "Продолжить без фото"

        keyboard077 = InlineKeyboardMarkup(row_width=1)
        buttons = list()
        button1 = InlineKeyboardButton(text=met_1, callback_data=f"partmethod_o_{1}")
        button2 = InlineKeyboardButton(text=met_2, callback_data=f"partmethod_o_{2}")
        buttons.append(button1)
        buttons.append(button2)
        keyboard077.add(*buttons)
        await Configuration.part_photo_start.set()
        await bot.send_message(user_id, '~', reply_markup=keyboard077)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


async def close_car(message: types.Message, state: FSMContext):
    global txt, keyboard, idd
    await message.delete()

    user_id = message.from_user.id
    await bot.delete_message(user_id, message.message_id - 1)
    part = message.text
    language = BotDB.get_user_lang(user_id)

    if part in stop_list:
        await state.finish()
        if language == 'ru':
            await bot.send_message(user_id, 'Запрос прерван')
        elif language == 'am':
            await bot.send_message(user_id, 'Հարցումն ընդհատվել է')
        return await stas.start(message, state)

    await state.update_data(part=part)
    data = await state.get_data()
    c = data.get('c')
    sts_photo = data.get('pts_photo')
    firm = data.get('brand')
    model = data.get('model')
    gen = data.get('gen')
    part_photo = data.get('part_photo_process')
    engine_displacement = data.get('engine_displacement')
    motor_power = data.get('motor_power')
    car_body = data.get('car_body')
    auto_transmission = data.get('auto_transmission')
    engine = data.get('engine')
    drive = data.get('drive')
    part = data.get('part')
    status = 'processed'

    await state.finish()
    # добавление запроса в enquiries
    try:
        idd = bot_car.add_enquiry(firm, model, gen, engine_displacement, motor_power, car_body, auto_transmission,
                                  engine,
                                  drive, sts_photo, part_photo, part, c, user_id, status)
    except Exception as e:
        print(f'добавление запроса в enquiries error - {e}')

    return await next_close_car(firm, model, gen, user_id, part, c, idd, motor_power, car_body,
                                auto_transmission, engine, drive, engine_displacement, sts_photo, part_photo, state)


class Notifi(StatesGroup):
    login_list = State()


class Change(StatesGroup):
    idd = State()
    types = State()
    summ = State()
    photo = State()
    photo_1 = State()
    login = State()
    mess_id = State()
    mess_chat_id = State()
    k = State()
    u_id = State()


async def next_close_car(firm, model, gen, user_id, part, c, iddd, motor_power, car_body,
                         auto_transmission, engine, drive, engine_displacement, sts_photo, part_photo,
                         state: FSMContext):
    global txt11, keyboard20
    try:
        print(firm, model, gen)
        car_id = cars_db.get_car_id(firm, model, gen)
        print(car_id)
        if car_id is None:
            return await bot.send_message(user_id, f"Car is not found, Contact support: {cfg.support}")
        logins_list = bot_car.get_logins_by_car_id(str(car_id))
        print(logins_list)
        if logins_list is not None and len(logins_list) != 0:
            language = BotDB.get_user_lang(user_id)

            if language == 'ru':
                await bot.send_message(user_id, f'Запрос №{iddd} принят в обработку')
                if sts_photo is not None:
                    media = [types.InputMediaPhoto(media=sts_photo, caption=c)]
                    if part_photo is not None:
                        media.append(types.InputMediaPhoto(media=part_photo))

                    await bot.send_media_group(chat_id=user_id, media=media)
                else:
                    await bot.send_message(user_id, f'{c}')
                await bot.send_message(user_id, part)
                await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')

            elif language == 'am':
                await bot.send_message(user_id, f'Հարցում №{iddd} ընդունվել է մշակման')

                if sts_photo is not None:
                    media = [types.InputMediaPhoto(media=sts_photo, caption=c)]
                    if part_photo is not None:
                        media.append(types.InputMediaPhoto(media=part_photo))

                    await bot.send_media_group(chat_id=user_id, media=media)
                else:
                    await bot.send_message(user_id, f'{c}')
                await bot.send_message(user_id, part)
                await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')

            if sts_photo is not None:
                media = [types.InputMediaPhoto(media=sts_photo,
                                               caption=f'#Запрос номер {iddd} отправлен {c}, {part}\n date - '
                                                       f'{datetime.datetime.now()}'
                                                       f'\n'
                                                       f'user_id - {user_id}')]
                if part_photo is not None:
                    media.append(types.InputMediaPhoto(media=part_photo))

                await bot.send_media_group(chat_id=cfg.chat_id_logs, media=media)
            else:
                await bot.send_message(cfg.chat_id_logs,
                                       f'#Запрос номер {iddd} отправлен {c}, {part}\n date - '
                                       f'{datetime.datetime.now()}'
                                       f'\n'
                                       f'user_id - {user_id}')

            print(f'Запрос номер {iddd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')

            tasks = []
            num = 0
            for i in logins_list:
                i = str(i).replace(' ', '')
                c_user_id = BotDB.get_user_id_login(i)
                print(c_user_id)

                user_login_result = BotDB.get_user_login(c_user_id)

                if user_login_result is not None and len(user_login_result) > 0:
                    async with state.proxy() as data:
                        login_list = data.get('login_list', [])  # Получаем список из состояния+
                        login_list.append(user_login_result[0])
                        data['login_list'] = login_list

                    user_login = user_login_result[0]

                    if user_login == i:
                        languag = BotDB.get_user_lang(c_user_id)
                        if languag == 'ru':
                            txt11 = f'''
Запрос № #{iddd}\n
{c}\n
Объем двигателя - {engine_displacement}
Мощность двигателя - {motor_power}
Кузов - {car_body}
КПП - {auto_transmission}
Тип двигателя - {engine}
Привод авто - {drive}
    
Запчасть/деталь -  {part}
                            '''
                            keyboard20 = ru_change_keyboard(iddd)
                        elif languag == 'am':
                            txt11 = f'''
Հարցում  № #{iddd}\n
{c}\n
Շարժիչի ծավալը - {engine_displacement}
Շարժիչի հզորությունը - {motor_power}
Մարմին - {car_body}
PPC - {auto_transmission}
Շարժիչի տեսակը - {engine}
Ավտո drive - {drive}


Մաս -  {part}
                            '''
                            keyboard20 = am_change_keyboard(iddd)
                        num = num + 1
                        try:

                            tasks.append(notification(iddd, languag, txt11, c_user_id, keyboard20, num,
                                                      len(logins_list), sts_photo, part_photo, state))
                        except Exception as e:
                            print(e)
                    else:
                        print(f"User login {user_login} does not match.")
                else:
                    print(f"User login result {c_user_id} is None or empty.")
                    # await notification(mess, idd, languag)
            await asyncio.gather(*tasks)

        else:
            try:
                language = BotDB.get_user_lang(user_id)
                if language == 'ru':
                    await bot.send_message(user_id, f'Запрос №{iddd} принят в обработку')
                    await bot.send_message(user_id, f'{c}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')
                    await bot.send_message(cfg.chat_id_logs,
                                           f'#Запрос НЕОТВЕЧЕННЫЕ номер {iddd} отправлен {c}, {part} date - {datetime.datetime.now()}')
                    await bot.send_message(cfg.chat_id_logs, f"user_id - {user_id}")

                    print(
                        f'Запрос НЕОТВЕЧЕННЫЕ номер {iddd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')
                elif language == 'am':
                    await bot.send_message(user_id, f'Հարցում №{iddd} ընդունվել է մշակման')
                    await bot.send_message(user_id, f'{c}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')
                    await bot.send_message(cfg.chat_id_logs,
                                           f'#Запрос НЕОТВЕЧЕННЫЕ номер {iddd} отправлен {c}, {part} date - {datetime.datetime.now()}')
                    await bot.send_message(cfg.chat_id_logs, f"user_id - {user_id}")
                    print(
                        f'Запрос НЕОТВЕЧЕННЫЕ номер {iddd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')
                if bot_car.get_stat(iddd) == 'processed':
                    bot_car.update_stat(iddd, 'unanswered')
            except Exception as e:
                print(f'error - {e}')

    except Exception as e:
        print(f'error - {e}')


async def notification(idd, languag, txt, c_user_id, keyboard0222, num, lk, sts_photo, part_photo, state: FSMContext):
    global k_mess, mess, chat_id, message_id, lmessage_id, lchat_id
    try:
        if sts_photo is not None:
            media = [types.InputMediaPhoto(media=sts_photo,
                                           caption=txt)]
            if part_photo is not None:
                media.append(types.InputMediaPhoto(media=part_photo))

            mess = await bot.send_media_group(chat_id=c_user_id, media=media)
            rf = await bot.send_message(c_user_id, f"#{idd}", reply_markup=keyboard0222)
            for message in rf:
                try:# Получение значений message_id и chat_id из каждого сообщения
                    message_id = message['message_id']
                    chat_id = message['chat']['id']
                except Exception:
                    message_id = rf['message_id']
                    chat_id = rf['chat']['id']
                # Вывод полученных значений
                print("Message ID:", message_id)
                print("Chat ID:", chat_id)
            await bot.send_message(cfg.chat_id_logs,
                                   f"Удалить запрос номер {idd}\n /delete_order _{message_id}_{chat_id}")

        else:
            mess = await bot.send_message(c_user_id, txt, reply_markup=keyboard0222)
        for kmessage in mess:
            try:  # Получение значений message_id и chat_id из каждого сообщения
                message_id = kmessage['message_id']
                chat_id = kmessage['chat']['id']
            except Exception:
                message_id = mess['message_id']
                chat_id = mess['chat']['id']

            # Вывод полученных значений
            print("Message ID:", lmessage_id)
            print("Chat ID:", lchat_id)
        await bot.send_message(cfg.chat_id_logs, f"Удалить запрос номер {idd}\n /delete_order _{lmessage_id}_{lchat_id}")

        print(f'Доставлен запрос {num} из {lk}, {BotDB.get_user_login(c_user_id)[0]}')
        await asyncio.sleep(1)

    except Exception:
        pass
        # ... больше не разбирает авто

    async with state.proxy() as data:
        login_list = data.get('login_list', [])
    ld = 0
    await state.finish()
    await Change.mess_chat_id.set()
    await state.update_data(mess_chat_id=chat_id)
    await Change.mess_id.set()
    await state.update_data(mess_id=message_id)
    while BotDB.get_user_login(c_user_id)[0] in login_list:
        if ld != 24:
            ld += 1
        else:
            await bot.send_message(cfg.chat_id_logs,
                                   f'{BotDB.get_user_login(c_user_id)[0]} - не отвечает на запрос уже 2 дня {idd}'
                                   f'{bot_db.get_num_login(BotDB.get_user_login(c_user_id)[0])}')
            print(f'{BotDB.get_user_login(c_user_id)[0]} - не отвечает на запрос уже 2 дня {idd}'
                  f'{bot_db.get_num_login(BotDB.get_user_login(c_user_id)[0])}')
            if bot_car.get_stat(idd) == 'processed':
                bot_car.update_stat(idd, 'unanswered')
            return
        while 9 > int(str(datetime.datetime.now())[10:-13]) > 1:
            print(f'sleep - {idd}')
            await asyncio.sleep(random.randint(5020, 5600))
        await asyncio.sleep(random.randint(1620, 1800))
        async with state.proxy() as dataa:
            login_lst = dataa.get('login_list', [])
        try:
            chat_id = k_mess.chat.id
            message_id = k_mess.message_id
            # Попытка удаления сообщения
            await bot.delete_message(chat_id, message_id)
        except Exception:
            pass  # Если сообщение уже удалено или не найдено, продолжаем выполнение
        try:
            if BotDB.get_user_login(c_user_id)[0] not in login_lst:
                await mess.delete()
                return
        except Exception:
            pass
        await asyncio.sleep(10)
        try:
            if languag == 'ru':
                k_mess = await mess.reply(f'У вас есть неотвеченный запрос #{idd}')
            elif languag == 'am':
                k_mess = await mess.reply(f'Դուք ունեք անպատասխան հարցում #{idd}')
        except Exception as e:
            pass
    try:
        await mess.delete()
    except Exception:
        pass
    return


def ru_change_keyboard(idd):
    keyboard0111 = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="✅ЕСТЬ НОВАЯ ОРИГИНАЛ", callback_data=f"neworig_{idd}")
    button2 = InlineKeyboardButton(text="✅ЕСТЬ Б/У ОРИГИНАЛ", callback_data=f"baorig_{idd}")
    button3 = InlineKeyboardButton(text="✅ЕСТЬ НОВАЯ КОПИЯ", callback_data=f"newcopy_{idd}")
    button4 = InlineKeyboardButton(text="✅ЕСТЬ Б/У КОПИЯ", callback_data=f"bacopy_{idd}")
    button5 = InlineKeyboardButton(text="❌Я не разбираю этот автомобиль", callback_data=f"NON_{idd}")
    button6 = InlineKeyboardButton(text="❌Нет в наличии такой запчасти", callback_data=f"NOT_{idd}")
    keyboard0111.add(button1, button2, button3, button4, button5, button6)
    return keyboard0111


def am_change_keyboard(idd):
    keyboard0112 = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="✅ԿԱ ՆՈՐ ԲՆՕՐԻՆԱԿ", callback_data=f"neworig_{idd}")
    button2 = InlineKeyboardButton(text="✅ՕԳՏԱԳՈՐԾՎԱԾ ԲՆՕՐԻՆԱԿ ԿԱ", callback_data=f"baorig_{idd}")
    button3 = InlineKeyboardButton(text="✅ԿԱ ՆՈՐ ՊԱՏՃԵՆ", callback_data=f"newcopy_{idd}")
    button4 = InlineKeyboardButton(text="✅ԿԱ ՕԳՏԱԳՈՐԾՎԱԾ ՊԱՏՃԵՆ", callback_data=f"bacopy_{idd}")
    button5 = InlineKeyboardButton(text="❌Ես չեմ ապամոնտաժում այս մեքենան", callback_data=f"NON_{idd}")
    button6 = InlineKeyboardButton(text="❌Նման պահեստամասեր մատչելի չեն", callback_data=f"NOT_{idd}")
    keyboard0112.add(button1, button2, button3, button4, button5, button6)
    return keyboard0112


async def change_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global k, message02, message011

    srs = callback_query.data.split('_')[0]
    idd = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    await Change.u_id.set()
    await state.update_data(u_id=user_id)

    login = None
    try:
        login = BotDB.get_user_login(user_id)
        await callback_query.message.delete()
    except Exception as e:
        pass

    try:

        try:
            c_user_id = bot_car.get_user_id_by_id(idd)
            dp = DP
            data = await dp.storage.get_data(user=c_user_id)
            user_state = dp.current_state(chat=c_user_id, user=c_user_id)
            # Извлечь login_list из данных состояния (при наличии)
            login_list = data.get('login_list', [])
            try:
                login_list.remove(login[0])
            except Exception as e:
                await user_state.finish()
            await user_state.update_data(login_list=login_list)
            if len(login_list) == 0:
                print(f'state finish {idd}')
                await user_state.finish()
        except Exception as e:
            pass

        if srs == 'NON':

            # Получаем chat_id и message_id из callback_query
            chat_id = callback_query.message.chat.id
            message_id = callback_query.message.message_id

            # Удаляем сообщение
            await bot.delete_message(chat_id, message_id)
            if bot_car.get_stat(idd) == 'processed':
                bot_car.update_stat(idd, 'close')
            await bot.send_message(cfg.chat_id_logs,
                                   f'Не разбирает авто:  логин - {login[0]}, id запроса - {idd} {datetime.datetime.now()}')
            return print(f'Not car {idd} {login[0]} {datetime.datetime.now()}')

        elif srs == 'NOT':

            # Получаем chat_id и message_id из callback_query
            chat_id = callback_query.message.chat.id
            message_id = callback_query.message.message_id

            # Удаляем сообщение
            await bot.delete_message(chat_id, message_id)
            if bot_car.get_stat(idd) == 'processed':
                bot_car.update_stat(idd, 'close')
            await bot.send_message(cfg.chat_id_logs,
                                   f'Нет запчасти:  логин - {login[0]}, id запроса - {idd} {datetime.datetime.now()}')
            return print(f'Not part {idd} {login[0]} {datetime.datetime.now()}')

        await Change.login.set()
        await state.update_data(login=login[0])
        await Change.idd.set()
        await state.update_data(idd=idd)
        await Change.types.set()
        await state.update_data(types=srs)

        if bot_car.get_stat(idd) == 'unanswered':
            bot_car.update_stat(idd, 'first')

        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            message011 = "Отправить фото запчасти"
            message02 = "Продолжить без фото"
        elif language == 'am':
            message011 = "Ուղարկեք պահեստամասի լուսանկար"
            message02 = ""

        keyboard07 = InlineKeyboardMarkup(row_width=1)
        buttons = list()
        button1 = InlineKeyboardButton(text=message011, callback_data=f"methodik_m_1")
        button2 = InlineKeyboardButton(text=message02, callback_data=f"methodik_m_2")
        buttons.append(button1)
        buttons.append(button2)
        keyboard07.add(*buttons)
        await Change.photo_1.set()
        if language == 'ru':
            await bot.send_message(callback_query.from_user.id, "~", reply_markup=keyboard07)
        else:
            await bot.send_message(callback_query.from_user.id, "~", reply_markup=keyboard07)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


async def photo_call(callback_query: types.CallbackQuery, state: FSMContext):
    global price, message01
    user_id = callback_query.from_user.id
    method = callback_query.data.split('_m_')[1]
    language = BotDB.get_user_lang(user_id)
    print(method)

    if language == 'ru':
        message01 = "Отправьте фото запчасти"
        price = "Введите цену за деталь"
    elif language == 'am':
        message01 = "Ուղարկեք պահեստամասի լուսանկար"
        price = "Մուտքագրեք գինը յուրաքանչյուր մասի համար"
    await Change.photo.set()

    if method == "1":
        await bot.send_message(user_id, message01)
    elif method == "2":
        await state.update_data(photo=None)
        kpk = await bot.send_message(user_id, price)
        await Change.k.set()
        await state.update_data(k=kpk)
        await Change.summ.set()


async def photo_process(message: types.Message, state: FSMContext):
    global price
    user_id = message.from_user.id
    language = BotDB.get_user_lang(user_id)
    print("process")
    # Получаем информацию о фото
    file_id_1 = message.photo[-1].file_id
    await state.update_data(photo=file_id_1)
    if language == 'ru':
        price = "Введите цену за деталь"
    elif language == 'am':
        price = "Մուտքագրեք գինը յուրաքանչյուր մասի համար"

    await Change.k.set()
    kpk = await bot.send_message(user_id, price)
    await state.update_data(k=kpk)
    await Change.summ.set()


async def change_finish(message: types.Message, state: FSMContext):
    global photo_1, photo_2, photo_3, y, caption, auto_name, address, summ
    try:
        summ = message.text
    except Exception as e:
        print(f'error - {e}')
        await state.finish()

    data = await state.get_data()
    idd = data.get('idd')
    u_id = data.get('u_id')
    k = data.get('k')
    srs = data.get('types')
    login = data.get('login')
    photo = data.get('photo')
    user_id = bot_car.get_user_id_by_id(idd)
    c = bot_car.get_c_by_id(idd)
    part = bot_car.get_part_by_id(idd)
    result = bot_db.user(login)  # Pass the login value as login[0]
    language = BotDB.get_user_lang(user_id)
    chat_id = message.chat.id
    message_id = message.message_id
    mess_id = data.get("mess_id")
    mess_chat_id = data.get("mess_chat_id")

    await k.delete()

    # Удаляем сообщение
    await bot.delete_message(chat_id, message_id)

    if language == 'am':
        if srs == 'neworig':
            y = 'նոր օրիգինալ առկա է'

        elif srs == 'baorig':
            y = 'օգտագործված բնօրինակ պահեստում'

        elif srs == 'newcopy':
            y = 'նոր պատճենը պահեստում'

        elif srs == 'bacopy':
            y = 'օգտագործված պատճենը առկա է'

    elif language == 'ru':
        if srs == 'neworig':
            y = 'новая оригинал в наличии'

        elif srs == 'baorig':
            y = 'б.у. оригинал в наличии'

        elif srs == 'newcopy':
            y = 'новая копия в наличии'

        elif srs == 'bacopy':
            y = 'б.у. копия в наличии'

    f = f'{part} {summ} դրամ {y}'

    user_type_acc = None
    num_1 = None
    num_2 = None
    site = None

    for row in result:
        user_type_acc = row[3]
        auto_name = row[6]
        address = row[7]
        num_1 = row[8]
        num_2 = row[9]
        site = row[12]

    if login is None:
        auto_name = u_id
        num_1 = BotDB.get_phones(u_id)
        address = ' '
        user_type_acc = 2

    num_1 = f'☎️ +{num_1}'

    if num_2 is not None:
        num_2 = f'☎️ +{num_2}\n'
    else:
        num_2 = ''

    if site is not None:
        website = '🌎 ' + site
    else:
        website = ''

    if user_type_acc == 2:
        try:

            if language == 'ru':
                caption = f'Запрос №{idd}\n{c}\n\n{f}\n\n{auto_name}\n{address}\n{num_1}\n{num_2}{website}'
            elif language == 'am':
                caption = f'Հարցում №{idd}\n{c}\n\n{f}\n\n{auto_name}\n{address}\n{num_1}\n{num_2}{website}'
            if photo is None:
                await bot.send_message(user_id, caption)
            else:
                media = [InputMediaPhoto(media=str(photo), caption=caption)]

                await bot.send_media_group(chat_id=user_id, media=media)
        except Exception as e:
            print(f'Error - {e}')
            await state.finish()
    ui = message.from_user.id
    lang = BotDB.get_user_lang(ui)
    if lang == 'ru':
        await bot.send_message(ui, f'Предложение отправлено, номер - {idd}, \n\n{c},\n\n{f}')

    if lang == 'am':
        await bot.send_message(ui, f'Առաջարկը ուղարկված է, թիվ - {idd}, \n\n{c},\n\n{f}')

    if photo is None:
        await bot.send_message(cfg.chat_id_logs, caption)
    else:
        media = [InputMediaPhoto(media=str(photo), caption=f"#ответ на запрос номер {idd} отправлен {c} "
                                                           f"{datetime.datetime.now()}, {login}\n\n{caption}\n\n "
                                                           f"User_id - {user_id}\n"
                                                           f"Удалить запрос - <a>/delete_order , {mess_chat_id} ,"
                                                           f" {mess_id}</a>", parse_mode="HTML")]

        await bot.send_media_group(cfg.chat_id_logs, media=media)

    print(f'#ответ на запрос номер {idd} отправлен {c} {datetime.datetime.now(), user_id}')

    if bot_car.get_stat(idd) == 'processed' or bot_car.get_stat(idd) == 'closed' or bot_car.get_stat(
            idd) == 'unanswered':
        bot_car.update_stat(idd, 'first')

    elif bot_car.get_stat(idd) == 'first':
        bot_car.update_stat(idd, 'second')

    elif bot_car.get_stat(idd) == 'second':
        bot_car.update_stat(idd, 'third')

    elif bot_car.get_stat(idd) == 'third':
        bot_car.update_stat(idd, 'fourth')
        print(f'id - {idd}, fourth')

    await state.finish()


def register_handlers_order(dp: Dispatcher):
    dp.register_message_handler(order_switch, commands=['order'])

    dp.register_message_handler(order, commands=['orderswitch', 'quick'])
    dp.register_callback_query_handler(models_callback_button, lambda c: c.data.startswith('firms|-|'))
    dp.register_callback_query_handler(years_callback_button, lambda c: c.data.startswith('omodel\-/'))
    dp.register_callback_query_handler(year_callback_button, lambda c: c.data.startswith('gens_-_'))

    dp.register_callback_query_handler(method_callback_button, lambda c: c.data.startswith('method_=_'))
    dp.register_message_handler(pts_photo, content_types=ContentType.PHOTO, state=Configuration.pts_photo)

    dp.register_callback_query_handler(part_method_callback_button, state=Configuration.part_photo_start)
    dp.register_message_handler(part_photo_process, content_types=ContentType.PHOTO,
                                state=Configuration.part_photo_process)

    dp.register_message_handler(process_engine_displacement, state=Configuration.engine_displacement)
    dp.register_message_handler(process_motor_power, state=Configuration.motor_power)
    dp.register_callback_query_handler(car_body_callback, lambda c: c.data.startswith(('Sedan', 'Хэтчбек 3 дв.',
                                                                                       'Хэтчбек 5 дв.', 'Лифтбек',
                                                                                       'Внедорожник 3 дв.',
                                                                                       'Внедорожник 5 дв.', 'Универсал',
                                                                                       'Купе', 'Минивэн', 'Пикап',
                                                                                       'Лимузин', 'Фургон',
                                                                                       'Кабриолет', "Սեդան",
                                                                                       "Հեչբեկ 3 դռներ",
                                                                                       "Հեչբեկ 5 դուռ",
                                                                                       "Liftbek", "Ամենագնաց 3 դռներ",
                                                                                       "Ամենագնաց 5 դուռ", "Ունիվերսալ",
                                                                                       "Կուպե", "Մինիվեն", "Պիկապ",
                                                                                       "Լիմուզին", "Վան", "Փոխարկելի")),
                                       state=Configuration.car_body)
    dp.register_callback_query_handler(auto_transmission_callback, lambda c: c.data.startswith(('Автоматическая',
                                                                                                'Робот',
                                                                                                'Вариатор',
                                                                                                'Механическая',
                                                                                                "Ավտոմատ",
                                                                                                "Ռոբոտ", "Վարիատոր",
                                                                                                "Մեխանիկական")),
                                       state=Configuration.auto_transmission)
    dp.register_callback_query_handler(engine_callback, lambda c: c.data.startswith(('Бензин', 'Дизель', 'Гибрид',
                                                                                     'Электро', 'Газ', "Բենզին",
                                                                                     "Դիզել", "Հիբրիդ",
                                                                                     "Էլեկտրո", "Գազ")),
                                       state=Configuration.engine)
    dp.register_callback_query_handler(drive_callback, lambda c: c.data.startswith(('Передний', 'Задний', 'Полный',
                                                                                    "Ճակատ",
                                                                                    "Հետեւի",
                                                                                    "Ֆուլլ"
                                                                                    )),
                                       state=Configuration.drive)
    dp.register_message_handler(close_car, state=Configuration.part)
    dp.register_callback_query_handler(change_callback, lambda c: c.data.startswith(('neworig_', 'baorig_', 'newcopy_',
                                                                                     'bacopy_', 'NON_', 'NOT_')))
    dp.register_callback_query_handler(photo_call, lambda c: c.data.startswith('methodik_m_'), state=Change.photo_1)
    dp.register_message_handler(photo_process, content_types=ContentType.PHOTO, state=Change.photo)
    dp.register_message_handler(change_finish, state=Change.summ)
