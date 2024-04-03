import asyncio
import datetime
import tracemalloc
import random
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup
from handlers import start_lang_handlers as stas
import config as cfg
from db_cars import CarsDB
from db import BotDB, bot_car, bot_db
from create_bot import bot
from create_bot import dp as DP

cars_db = CarsDB()

tracemalloc.start()

BotDB = BotDB()
bot_car = bot_car()
bot_db = bot_db()

stop_list = ['\start', '/start', '/stop', '/order', 'Запрос', 'Автосервисы (скоро)', 'Авто в разборе',
             'Аккаунт авторазборки',
             '/quick', '/disassembly', '/feedback', '/language', '/login', '/account', 'Авторизация автразборки',
             'Հարցում', 'Ավտոսպասարկում (շուտով)', 'Ավտո վերլուծության մեջ', 'Թույլտվություն ինքնահավաք',
             'ինքնահավաք հաշիվ']


def switches_ru(eq):
    keyboard01 = InlineKeyboardMarkup(row_width=2)
    es = eq.split(', ')
    buttons = [InlineKeyboardButton(text=model, callback_data=f"om-{model}") for model in es]
    keyboard01.add(*buttons)
    button = InlineKeyboardButton(text='Нет нужного автомобиля в списке', callback_data='omsk')
    keyboard01.row(button)
    return keyboard01


def switches_am(eq):
    keyboard02 = InlineKeyboardMarkup(row_width=2)
    es = eq.split(', ')
    buttons = [InlineKeyboardButton(text=model, callback_data=f"om-{model}") for model in es]
    keyboard02.add(*buttons)
    button = InlineKeyboardButton(text='Theանկում ճիշտ մեքենա չկա', callback_data='omsk')
    keyboard02.row(button)
    return keyboard02


async def order_switch(message: types.Message, s=0):
    global kl, keyboard03
    try:
        user_id = message.from_user.id
        if user_id in cfg.ban_list:
            return await bot.send_message(user_id, 'BAN')
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            kl = cfg.ru_cc

        elif language == 'am':
            kl = cfg.am_cc

        if s == 0:
            eq = list()

            if BotDB.get_user_status(user_id) == 1:
                login = BotDB.get_user_login(user_id)
                enq = bot_db.get_enquiries_login(login[0])
                if enq[0] is None:
                    await order(message)
                    return
                elif enq[0] is not None:
                    if ', ' in enq[0]:
                        if language == 'ru':
                            keyboard03 = switches_ru(enq[0])

                        elif language == 'am':
                            keyboard03 = switches_am(enq[0])
                        # В этом месте обработаем enq[0]
                        await bot.send_message(user_id, kl, reply_markup=keyboard03)
                    else:
                        eq.extend(enq)
                        if language == 'ru':
                            keyboard03 = switches_ru(", ".join(eq))

                        elif language == 'am':
                            keyboard03 = switches_am(", ".join(eq))

                        await bot.send_message(user_id, kl, reply_markup=keyboard03)
                        eq.clear()
                else:
                    await order(message)
                    return
            else:
                await order(message)
                return
        # ... (остальной код функции)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


async def order_switch_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    data = callback_query.data
    if data == 'omsk':
        await order(callback_query)
        return
    data = data[3::]
    dt = data.split(' ')
    brand = dt[0]
    model = dt[1]
    year = dt[2]
    callback_query.data = f"year-{year}-{model}-{brand}"
    await year_callback_button(callback_query, state)


# @dp.message_handler(commands=['order'])
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


# @dp.callback_query_handler(lambda c: c.data.startswith('condition:'))
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
    model = callback_query.data.split('\-/')[1]
    firm = callback_query.data.split('\-/')[2]
    c = '_*' + firm + ' ' + model + '*_'
    language = BotDB.get_user_lang(user_id)
    gens = cars_db.years_by_model_and_firm(firm, model)
    keyboard06 = InlineKeyboardMarkup(row_width=1)
    buttons = []
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
    year = State()
    c = State()
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
    k = ()


async def year_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        firm = callback_query.data.split('_-_')[3]
        model = callback_query.data.split('_-_')[2]
        year = callback_query.data.split('_-_')[1]

        await Configuration.c.set()

        c ='_' + firm + ', ' + model + ', ' + year + '_'
        await bot.send_message(user_id, c, parse_mode="Markdown")

        x = str(firm) + ' ' + str(model) + ' ' + str(year)
        await state.update_data(c=c)
        language = BotDB.get_user_lang(user_id)
        if language == 'ru':
            frst = cfg.ru_cool
            second = cfg.ru_year_start
            ed = cfg.ru_ed
        elif language == 'am':
            frst = cfg.am_cool
            second = cfg.am_year_start
            ed = cfg.am_ed

        await Configuration.engine_displacement.set()
        await bot.send_message(user_id, ed)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


async def year_message_button(message: types.Message, state: FSMContext):
    try:

        user_id = message.from_user.id
        data = await state.get_data()
        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')

        if 'other' in brand:
            brand = brand[6::]

            await Configuration.brand.set()
            await state.update_data(brand=brand)

        if model == 'Non':
            await Configuration.model.set()
            await state.update_data(model=model)

        if year == 'Non':
            return await year_model(message)

        await Configuration.year.set()
        await state.update_data(year=year)

        await Configuration.c.set()

        c = brand + ', ' + model + ', ' + year
        x = str(brand) + ' ' + str(model) + ' ' + str(year)
        await state.update_data(c=c)
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            ed = cfg.ru_ed
        elif language == 'am':
            ed = cfg.am_ed

        await Configuration.engine_displacement.set()
        await bot.send_message(user_id, ed)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


async def process_engine_displacement(message: types.Message, state: FSMContext):
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
        print(f'error - {e}')
        await state.finish()


async def process_motor_power(message: types.Message, state: FSMContext):
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
            frst = cfg.ru_accept
            cb = cfg.ru_cb
            st = cfg.ru_st
            keyboard = ru_car_body_keyboard()
        elif language == 'am':
            frst = cfg.am_accept
            cb = cfg.am_cb
            st = cfg.am_st
            keyboard = am_car_body_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + motor_power + st
        # await bot.send_message(user_id, f'{frst} - {c}')
        await state.update_data(c=c)
        await Configuration.car_body.set()
        await bot.send_message(user_id, cb, reply_markup=keyboard)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_car_body_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
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
    keyboard.add(button1, button2, button3, button4, button5, button6, button7, button9, button10, button11,
                 button12, button13, button14)
    return keyboard


def am_car_body_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
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
    keyboard.add(button1, button2, button3, button4, button5, button6, button7, button9, button10, button11,
                 button12, button13, button14)
    return keyboard


async def car_body_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        car_body = callback_query.data
        await state.update_data(car_body=car_body)
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            frst = cfg.ru_accept
            at = cfg.ru_at
            keyboard = ru_auto_transmission_keyboard()
        elif language == 'am':
            frst = cfg.am_accept
            at = cfg.am_at
            keyboard = am_auto_transmission_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + car_body
        # await bot.send_message(user_id, f'{frst} - {c}')
        await state.update_data(c=c)
        await Configuration.auto_transmission.set()
        await bot.send_message(user_id, at, reply_markup=keyboard)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_auto_transmission_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Автоматическая", callback_data="Автоматическая")
    button2 = InlineKeyboardButton(text="Робот", callback_data="Робот")
    button3 = InlineKeyboardButton(text="Вариатор", callback_data="Вариатор")
    button5 = InlineKeyboardButton(text="Механическая", callback_data="Механическая")
    keyboard.add(button1, button2, button3, button5)
    return keyboard


def am_auto_transmission_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Ավտոմատ", callback_data="Ավտոմատ")
    button2 = InlineKeyboardButton(text="Ռոբոտ", callback_data="Ռոբոտ")
    button3 = InlineKeyboardButton(text="Վարիատոր", callback_data="Վարիատոր")
    button5 = InlineKeyboardButton(text="Մեխանիկական", callback_data="Մեխանիկական")
    keyboard.add(button1, button2, button3, button5)
    return keyboard


async def auto_transmission_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        auto_transmission = callback_query.data
        await state.update_data(auto_transmission=auto_transmission)

        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            frst = cfg.ru_accept
            et = cfg.ru_et
            keyboard = ru_engine_keyboard()
        elif language == 'am':
            frst = cfg.am_accept
            et = cfg.am_et
            keyboard = am_engine_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + auto_transmission
        # await bot.send_message(user_id, f'{frst} - {c}')
        await state.update_data(c=c)
        await Configuration.engine.set()
        await bot.send_message(user_id, et, reply_markup=keyboard)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_engine_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Бензин", callback_data="Бензин")
    button2 = InlineKeyboardButton(text="Дизель", callback_data="Дизель")
    button3 = InlineKeyboardButton(text="Гибрид", callback_data="Гибрид")
    button4 = InlineKeyboardButton(text="Электро", callback_data="Электро")
    button5 = InlineKeyboardButton(text="Газ", callback_data="Газ")
    keyboard.add(button1, button2, button3, button4, button5)
    return keyboard


def am_engine_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Բենզին", callback_data="Բենզին")
    button2 = InlineKeyboardButton(text="Դիզել", callback_data="Դիզել")
    button3 = InlineKeyboardButton(text="Հիբրիդ", callback_data="Հիբրիդ")
    button4 = InlineKeyboardButton(text="Էլեկտրո", callback_data="Էլեկտրո")
    button5 = InlineKeyboardButton(text="Գազ", callback_data="Գազ")
    keyboard.add(button1, button2, button3, button4, button5)
    return keyboard


async def engine_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        engine = callback_query.data
        await state.update_data(engine=engine)

        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            frst = cfg.ru_accept
            d = cfg.ru_d
            keyboard = ru_drive_keyboard()
        elif language == 'am':
            frst = cfg.am_accept
            d = cfg.am_d
            keyboard = am_drive_keyboard()

        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + engine
        # await bot.send_message(user_id, f'{frst} - {c}')
        await state.update_data(c=c)
        await Configuration.drive.set()
        await bot.send_message(user_id, d, reply_markup=keyboard)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


def ru_drive_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Передний", callback_data="Передний")
    button2 = InlineKeyboardButton(text="Задний", callback_data="Задний")
    button3 = InlineKeyboardButton(text="Полный", callback_data="Полный")

    keyboard.add(button1, button2, button3)
    return keyboard


def am_drive_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Ճակատ", callback_data="Ճակատ")
    button2 = InlineKeyboardButton(text="Հետեւի", callback_data="Հետեւի")
    button3 = InlineKeyboardButton(text="Ֆուլլ", callback_data="Ֆուլլ")

    keyboard.add(button1, button2, button3)
    return keyboard


async def drive_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        drive = callback_query.data
        await state.update_data(drive=drive)
        language = BotDB.get_user_lang(user_id)
        if language == 'ru':
            frst = cfg.ru_accept
        elif language == 'am':
            frst = cfg.am_accept
        data = await state.get_data()
        c = data.get('c')
        await Configuration.c.set()
        c = c + ', ' + drive
        # await bot.send_message(user_id, f'{frst} - {c}')
        await state.update_data(c=c)
        if language == 'ru':
            pt = cfg.ru_pt
        elif language == 'am':
            pt = cfg.am_pt
        await Configuration.part.set()
        await bot.send_message(user_id, pt)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


async def close_car(message: types.Message, state: FSMContext):
    global txt, keyboard
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
    brand = data.get('brand')
    model = data.get('model')
    year = data.get('year')
    print(year)
    engine_displacement = data.get('engine_displacement')
    motor_power = data.get('motor_power')
    car_body = data.get('car_body')
    auto_transmission = data.get('auto_transmission')
    engine = data.get('engine')
    drive = data.get('drive')
    part = data.get('part')
    status = 'processed'

    user_status = BotDB.get_user_status(user_id)
    await state.finish()
    # история запросов
    if user_status == 1:
        login = BotDB.get_user_login(user_id)
        enquiries = bot_db.get_enquiries_login(login[0])

        eq = list()

        if enquiries[0] is None:
            enq = brand + ' ' + model + ' ' + year
            eq.append(enq)
            erm = ', '.join(eq)
            bot_db.update_enquiries(erm, login[0])
            eq.clear()
        elif enquiries[0] is not None:
            enq = brand + ' ' + model + ' ' + year
            if ', ' in enquiries[0]:
                eq = enquiries[0].split(', ')
                if len(eq) > 9:
                    eq.pop(0)
                eq.append(enq)
                erm = ', '.join(eq)
                bot_db.update_enquiries(erm, login[0])
                eq.clear()
            else:
                eq.append(enquiries[0])
                eq.append(enq)
                erm = ', '.join(eq)
                bot_db.update_enquiries(erm, login[0])
                eq.clear()
    # добавление запроса в enquiries
    try:
        idd = bot_car.add_enquiry(brand, model, year, engine_displacement, motor_power, car_body, auto_transmission,
                                  engine,
                                  drive, None, None, part, c, user_id, status)
    except Exception as e:
        print(f'добавление запроса в enquiries error - {e}')
        await state.finish()
    years_list = bot_car.get_car_years(brand, model)
    years_lst = list()
    await state.finish()
    return await next_close_car(years_lst, years_list, year, brand, model, user_id, part, c, idd, motor_power, car_body,
                                auto_transmission, engine, drive, engine_displacement, state)


class Notifi(StatesGroup):
    login_list = State()


async def next_close_car(years_lst, years_list, year, brand, model, user_id, part, c, idd, motor_power, car_body,
                         auto_transmission, engine, drive, engine_displacement, state: FSMContext):
    await state.update_data(login_list=[])
    try:
        for i in years_list:

            first = i[:4:]
            second = i[5::]

            for j in range(int(first), int(second) + 1):

                if j == int(year):
                    years_lst.append(i)

        k = list()
        for r in years_lst:
            p = bot_car.select_car(brand, model, r)
            if p == 2 or p == 3:
                k.append(p)
            else:
                for row in p:
                    if row not in k:
                        k.append(row)

        if len(k) > 1:
            if 2 in k:
                k.remove(2)
            if 3 in k:
                k.remove(3)
        lk = len(k)
        if not k:
            k = [2]
        if type(k) != type([12, 31, 3]):
            k = [2]

        if k[0] != 2 and k[0] != 3 and k != 3 and k != 2:
            language = BotDB.get_user_lang(user_id)
            if language == 'ru':
                await bot.send_message(user_id, f'Запрос №{idd} принят в обработку')
                await bot.send_message(user_id, f'{c}')
                await bot.send_message(user_id, part)
                await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')
                await bot.send_message(1806719774,
                                       f'#Запрос номер {idd} отправлен {c}, {part} date - {datetime.datetime.now()}')
                await bot.send_message(1806719774, f"user_id - {user_id}")

                print(f'Запрос номер {idd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')
            elif language == 'am':
                await bot.send_message(user_id, f'Հարցում №{idd} ընդունվել է մշակման')
                await bot.send_message(user_id, f'{c}')
                await bot.send_message(user_id, part)
                await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')
                await bot.send_message(1806719774,
                                       f'#Запрос номер {idd} отправлен {c}, {part} date - {datetime.datetime.now()}')
                await bot.send_message(1806719774, f"user_id - {user_id}")

                print(f'Запрос номер {idd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')
            tasks = []

            num = 0
            for i in k:
                i = str(i).replace(' ', '')
                c_user_id = BotDB.get_user_id_login(i)

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
                            txt = f'''
Запрос № #{idd}\n
{c}\n
Объем двигателя - {engine_displacement}
Мощность двигателя - {motor_power}
Кузов - {car_body}
КПП - {auto_transmission}
Тип двигателя - {engine}
Привод авто - {drive}
    
Запчасть/деталь -  {part}
                            '''
                            keyboard = ru_change_keyboard(idd)
                        elif languag == 'am':
                            txt = f'''
Հարցում  № #{idd}\n
{c}\n
Շարժիչի ծավալը - {engine_displacement}
Շարժիչի հզորությունը - {motor_power}
Մարմին - {car_body}
PPC - {auto_transmission}
Շարժիչի տեսակը - {engine}
Ավտո drive - {drive}


Մաս -  {part}
                            '''
                            keyboard = am_change_keyboard(idd)
                        num = num + 1
                        try:

                            tasks.append(notification(idd, languag, txt, c_user_id, keyboard, num, lk, state))
                        except Exception as e:
                            print(e)
                    else:
                        print(f"User login {user_login} does not match.")
                else:
                    print(f"User login result {c_user_id} is None or empty.")
                    # await notification(mess, idd, languag)
            await asyncio.gather(*tasks)

        elif k[0] == 3 or k == 3:
            try:
                adm_id = 6061725297
                mess = f"Нет совпадений для: brand={brand}, model={model}, year={year}"
                await bot.send_message(adm_id, mess)
                language = BotDB.get_user_lang(user_id)

                if language == 'ru':
                    await bot.send_message(user_id,
                                           f'Автомобиль на разборах не найден, попробуйте найти запчасть в другом '
                                           f'поколении автомобиля {brand} {model}')

                elif language == 'am':
                    await bot.send_message(user_id,
                                           f'Մեքենան չի գտնվել վերլուծության մեջ, Փորձեք գտնել մեկ այլ պահեստամաս'
                                           f'մեքենայի սերունդ {brand} {model}')
                await bot.send_message(1806719774,
                                       f'Нет совпадений для: {brand} {model} {year} date - {datetime.datetime.now()}')
                print(f'Нет совпадений для: {brand} {model} {year} date - {datetime.datetime.now()}')
            except Exception as e:
                print(f'error - {e}')
        else:
            try:
                language = BotDB.get_user_lang(user_id)
                if language == 'ru':
                    await bot.send_message(user_id, f'Запрос №{idd} принят в обработку')
                    await bot.send_message(user_id, f'{c}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')
                    await bot.send_message(1806719774,
                                           f'#Запрос НЕОТВЕЧЕННЫЕ номер {idd} отправлен {c}, {part} date - {datetime.datetime.now()}')
                    await bot.send_message(1806719774, f"user_id - {user_id}")

                    print(
                        f'Запрос НЕОТВЕЧЕННЫЕ номер {idd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')
                elif language == 'am':
                    await bot.send_message(user_id, f'Հարցում №{idd} ընդունվել է մշակման')
                    await bot.send_message(user_id, f'{c}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')
                    await bot.send_message(1806719774,
                                           f'#Запрос НЕОТВЕЧЕННЫЕ номер {idd} отправлен {c}, {part} date - {datetime.datetime.now()}')
                    await bot.send_message(1806719774, f"user_id - {user_id}")
                    print(
                        f'Запрос НЕОТВЕЧЕННЫЕ номер {idd} отправлен {c}, {part} date - {datetime.datetime.now(), user_id}')
                if bot_car.get_stat(idd) == 'processed':
                    bot_car.update_stat(idd, 'unanswered')
            except Exception as e:
                print(f'error - {e}')


    except Exception as e:
        print(f'error - {e}')


async def notification(idd, languag, txt, c_user_id, keyboard, num, lk, state: FSMContext):
    try:
        mess = await bot.send_message(c_user_id, txt, reply_markup=keyboard)
        print(f'Доставлен запрос {num} из {lk}, {BotDB.get_user_login(c_user_id)[0]}')
        await asyncio.sleep(1)
    except Exception as e:
        login = BotDB.get_user_login(c_user_id)[0]
        await bot.send_message(1806719774, f'Заблокировал бота {c_user_id} {login} {datetime.datetime.now()}')

        print(f'Заблокировал бота {c_user_id} {login} {datetime.datetime.now()}')
        try:
            id_list = bot_car.get_id_list(BotDB.get_user_login(c_user_id)[0])
            print(id_list)
            for info in id_list:
                user_id = c_user_id
                id_listе = [int(info)]
                logins = bot_car.get_logins(id_listе)
                if login not in logins:
                    return
                if ', ' in logins:
                    s = list()
                    s = logins.split(', ')
                    s.remove(login)
                    bot_car.add_login(info, s)
                else:
                    bot_car.add_login(info, list())
                await bot.send_message(1806719774, f'{login} больше не разбирает авто - id{info}')
                print(f'{login} больше не разбирает авто - id{info}')

            dp = DP
            data = await dp.storage.get_data(user=c_user_id)
            user_state = dp.current_state(chat=c_user_id, user=c_user_id)
            login_list = data.get('login_list', [])
            try:
                login_list.remove(login)
            except Exception as e:
                pass
            await user_state.update_data(login_list=login_list)
            if len(login_list) == 0:
                print('state finish', idd)
                await user_state.finish()
            return
        except Exception as e:
            print(e)
            return
        return

    async with state.proxy() as data:
        login_list = data.get('login_list', [])
    ld = 0
    while BotDB.get_user_login(c_user_id)[0] in login_list:
        if ld != 24:
            ld += 1
        else:
            await bot.send_message(1806719774,
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
            chat_id = k.chat.id
            message_id = k.message_id
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
                k = await mess.reply(f'У вас есть неотвеченный запрос #{idd}')
            elif languag == 'am':
                k = await mess.reply(f'Դուք ունեք անպատասխան հարցում #{idd}')
        except Exception as e:
            pass
    try:
        await mess.delete()
    except Exception:
        pass
    return


class Change(StatesGroup):
    idd = State()
    types = State()
    summ = State()
    login = State()
    k = State()
    u_id = State()


def ru_change_keyboard(idd):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="✅ЕСТЬ НОВАЯ ОРИГИНАЛ", callback_data=f"neworig_{idd}")
    button2 = InlineKeyboardButton(text="✅ЕСТЬ Б/У ОРИГИНАЛ", callback_data=f"baorig_{idd}")
    button3 = InlineKeyboardButton(text="✅ЕСТЬ НОВАЯ КОПИЯ", callback_data=f"newcopy_{idd}")
    button4 = InlineKeyboardButton(text="✅ЕСТЬ Б/У КОПИЯ", callback_data=f"bacopy_{idd}")
    button5 = InlineKeyboardButton(text="❌Я не разбираю этот автомобиль", callback_data=f"NON_{idd}")
    button6 = InlineKeyboardButton(text="❌Нет в наличии такой запчасти", callback_data=f"NOT_{idd}")
    keyboard.add(button1, button2, button3, button4, button5, button6)
    return keyboard


def am_change_keyboard(idd):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="✅ԿԱ ՆՈՐ ԲՆՕՐԻՆԱԿ", callback_data=f"neworig_{idd}")
    button2 = InlineKeyboardButton(text="✅ՕԳՏԱԳՈՐԾՎԱԾ ԲՆՕՐԻՆԱԿ ԿԱ", callback_data=f"baorig_{idd}")
    button3 = InlineKeyboardButton(text="✅ԿԱ ՆՈՐ ՊԱՏՃԵՆ", callback_data=f"newcopy_{idd}")
    button4 = InlineKeyboardButton(text="✅ԿԱ ՕԳՏԱԳՈՐԾՎԱԾ ՊԱՏՃԵՆ", callback_data=f"bacopy_{idd}")
    button5 = InlineKeyboardButton(text="❌Ես չեմ ապամոնտաժում այս մեքենան", callback_data=f"NON_{idd}")
    button6 = InlineKeyboardButton(text="❌Նման պահեստամասեր մատչելի չեն", callback_data=f"NOT_{idd}")
    keyboard.add(button1, button2, button3, button4, button5, button6)
    return keyboard


async def change_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global k

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
            await bot.send_message(1806719774,
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
            await bot.send_message(1806719774,
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
            k = await bot.send_message(user_id, 'Введите цену за деталь')
        elif language == 'am':
            k = await bot.send_message(user_id, 'Մուտքագրեք գինը յուրաքանչյուր մասի համար')
        await Change.k.set()
        await state.update_data(k=k)
        await Change.summ.set()
    except Exception as e:
        print(f'error - {e}')
        await state.finish()


# noinspection PyArgumentList
async def change_finish(message: types.Message, state: FSMContext):
    global photo_1, photo_2, photo_3, y, caption, auto_name, address
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
    user_id = bot_car.get_user_id_by_id(idd)
    c = bot_car.get_c_by_id(idd)
    part = bot_car.get_part_by_id(idd)
    result = bot_db.user(login)  # Pass the login value as login[0]
    language = BotDB.get_user_lang(user_id)
    chat_id = message.chat.id
    message_id = message.message_id

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
    photo_1 = None
    photo_2 = None
    photo_3 = None

    for row in result:
        user_type_acc = row[3]
        auto_name = row[6]
        address = row[7]
        num_1 = row[8]
        num_2 = row[9]
        site = row[12]
        photo_1 = row[13]
        photo_2 = row[14]
        photo_3 = row[15]

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
            if photo_1 is None:
                await bot.send_message(user_id, caption)
            else:
                media = [InputMediaPhoto(media=str(photo_1), caption=caption)]

                if photo_2 is not None:
                    media.append(InputMediaPhoto(media=photo_2))

                if photo_3 is not None:
                    media.append(InputMediaPhoto(media=photo_3))

                await bot.send_media_group(chat_id=user_id, media=media)
        except Exception as e:
            print(f'Error - {e}')
            await state.finish()
    ui = message.from_user.id
    lang = BotDB.get_user_lang(ui)
    if lang == 'ru':
        await bot.send_message(ui, f'Предложение отправлено, номер - {idd}, \n\n{c},\n\n{f}')
        await bot.send_message(1806719774,
                               f'#ответ на запрос номер {idd} отправлен {c} {datetime.datetime.now(), login}')
        await bot.send_message(1806719774, caption)
        await bot.send_message(1806719774, user_id)
        print(f'#ответ на запрос номер {idd} отправлен {c} {datetime.datetime.now(), user_id}')
    if lang == 'am':
        await bot.send_message(ui, f'Առաջարկը ուղարկված է, թիվ - {idd}, \n\n{c},\n\n{f}')
        await bot.send_message(1806719774,
                               f'#ответ на запрос номер {idd} отправлен {c} {datetime.datetime.now(), login}')
        await bot.send_message(1806719774, caption)
        await bot.send_message(1806719774, user_id)
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
    dp.register_callback_query_handler(order_switch_callback, lambda c: c.data.startswith(('om-', 'omsk')))
    dp.register_message_handler(order, commands=['orderswitch', 'quick'])
    dp.register_callback_query_handler(models_callback_button, lambda c: c.data.startswith('firms|-|'))
    dp.register_callback_query_handler(year_callback_button, lambda c: c.data.startswith('gens_-_'))
    dp.register_callback_query_handler(years_callback_button, lambda c: c.data.startswith('omodel\-/'))
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
    dp.register_message_handler(change_finish, state=Change.summ)
