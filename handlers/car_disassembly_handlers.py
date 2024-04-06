from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup
from db import BotDB, bot_car, bot_db
from create_bot import dp, bot
import config as cfg
from db_cars import CarsDB

cars_db = CarsDB()
BotDB = BotDB()
bot_car = bot_car()
bot_db = bot_db()


async def car_disassembly(message: types.Message):
    try:
        user_id = message.from_user.id
        if user_id in cfg.ban_list:
            return await bot.send_message(user_id, 'BAN')
        language = BotDB.get_user_lang(user_id)

        login = BotDB.get_user_login(user_id)[0]
        if not login:
            return
        car_id_list = bot_car.get_car_id_list(login)[0][0]
        if car_id_list:

            if len(car_id_list) == 1 and car_id_list[0] == '':
                car_id_list = filter(filter(None, car_id_list))

            car_id_list = [num for num in car_id_list.split(',')]

            if True:
                if len(car_id_list) <= 100:
                    keyboard_buttons = []
                    for car_id in car_id_list:
                        car_info = cars_db.get_car_by_id(car_id)
                        keyboard_buttons.append(
                            InlineKeyboardButton(text=f"{car_info[2]}, {car_info[3]}, {car_info[4]}",
                                                 callback_data=f"button:{car_id}"))
                    keyboard = InlineKeyboardMarkup(row_width=1)
                    keyboard.add(*keyboard_buttons)

                    # Отправляем сообщение с клавиатурой
                    if language == 'ru':
                        await bot.send_message(user_id, text="Поколения авто которые вы разбираете:",
                                               reply_markup=keyboard)
                        keyboart = InlineKeyboardMarkup(row_width=3)
                        keyboart.row(
                            InlineKeyboardButton(text='Добавить авто', callback_data=f"button:add",
                                                 resize_keyboard=True))
                        await bot.send_message(user_id, text="_", reply_markup=keyboart)

                    elif language == 'am':
                        await bot.send_message(user_id, text="Ավտոմեքենաների սերունդներ, որոնք դուք ապամոնտաժում եք:",
                                               reply_markup=keyboard)
                        keyboart = InlineKeyboardMarkup(row_width=3)
                        keyboart.row(
                            InlineKeyboardButton(text='Ավելացնել ավտո', callback_data=f"button:add",
                                                 resize_keyboard=True))
                        await bot.send_message(user_id, text="_", reply_markup=keyboart)
                else:
                    # Отправляем сообщение с клавиатурой
                    car_list = ""
                    for car_id in car_id_list:
                        car_info = cars_db.get_car_by_id(car_id)
                        car_list += f"{car_info[2]}, {car_info[3]}, {car_info[4]}\n"
                    if language == 'ru':

                        await bot.send_message(user_id, text=f"Поколения авто которые вы разбираете:\n "
                                                             f"удалить поколение можно через тех. поддержку @sasapsa\n"
                                                             f"{car_list}")
                        keyboart = InlineKeyboardMarkup(row_width=3)
                        keyboart.row(
                            InlineKeyboardButton(text='Добавить авто', callback_data=f"button:add",
                                                 resize_keyboard=True))
                        await bot.send_message(user_id, text="_", reply_markup=keyboart)

                    elif language == 'am':
                        await bot.send_message(user_id, text=f"Ավտոմեքենաների սերունդներ, որոնք դուք ապամոնտաժում եք:\n"
                                                             f"դուք կարող եք հեռացնել "
                                                             f"սերունդը նրանց միջոցով: աջակցություն @sasapsa"
                                                             f"{car_list}")
                        keyboart = InlineKeyboardMarkup(row_width=3)
                        keyboart.row(
                            InlineKeyboardButton(text='Ավելացնել ավտո', callback_data=f"button:add",
                                                 resize_keyboard=True))
                        await bot.send_message(user_id, text="_", reply_markup=keyboart)

        else:
            await car_dis(message)

    except Exception as e:
        await car_dis(message)
        # Обработка исключения
        print(f"Произошла ошибка: {e}")


async def car_disassembly_callback(callback_query: types.CallbackQuery):
    info = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    language = BotDB.get_user_lang(user_id)
    if info == 'add':
        await car_dis(callback_query)
    else:
        car = cars_db.get_car_by_id(info)

        if language == 'ru':
            keyboard = ru_del_car(info)
            await bot.send_message(user_id, f"car id - <u>{info}</u>\n{car[2]}, {car[3]}, {car[4]}\nprice - {car[5]}",
                                   reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
        elif language == 'am':
            keyboard = ru_del_car(info)
            await bot.send_message(user_id, f'"car id - <u>{info}</u>\n{car[2]}, {car[3]}, {car[4]}\nprice - {car[5]}',
                                   reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


def ru_del_car(info):
    keyboard = InlineKeyboardMarkup(row_width=4)
    buttons = [
        InlineKeyboardButton(text="Удалить авто", callback_data=f"delcar:{info}"),
    ]

    keyboard.add(*buttons)
    return keyboard


def am_del_car(info):
    keyboard = InlineKeyboardMarkup(row_width=4)
    buttons = [
        InlineKeyboardButton(text="Հեռացնել մեքենան", callback_data=f"delcar:{info}"),
    ]

    keyboard.add(*buttons)
    return keyboard


async def del_car_callback(callback_query: types.CallbackQuery):
    car_id = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    login = BotDB.get_user_login(user_id)[0]
    car_id_list = bot_car.get_car_id_list(login)[0][0]
    car_id_list = [num for num in car_id_list.split(',')]
    # Удаляем car_id из списка, если он там есть
    if car_id in car_id_list:
        car_id_list.remove(car_id)
    # Обновляем запись в базе данных с новым car_id_list
    new_car_id_list = ','.join(car_id_list)
    bot_car.update_car_id_list(login, new_car_id_list)
    await bot.send_message(user_id, f'Вы больше не разбираете авто - id{car_id}')
    await bot.send_message(cfg.chat_id_logs, f'{login} больше не разбирает авто - id{car_id}')
    print(f'{login} больше не разбирает авто - id{car_id}')


async def car_dis(message: types.Message):
    user_id = message.from_user.id
    try:
        # Получаем предпочтение языка из базы данных на основе user_id
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            keyboard = generate_brands_inline_keyboard()
            await bot.send_message(user_id, "Выберите марку авто из списка:", reply_markup=keyboard)
        elif language == 'am':
            keyboard = generate_brands_inline_keyboard()
            await bot.send_message(user_id, "ընտրեք մակնիշը ավտոմեքենայի:", reply_markup=keyboard)
        else:
            # Логика для языка по умолчанию (английский или другой)
            await bot.send_message(user_id, 'Выберите язык / Ընտրեք լեզուն: - /language')
            # Остальная логика для языка по умолчанию

    except Exception as e:
        # Обработка исключения
        print(f"Произошла ошибка: {e}")
        await bot.send_message(user_id, "Произошла ошибка. Пожалуйста, повторите попытку позже.")


# Генерация инлайн кнопок(марки авто)
def generate_brands_inline_keyboard():
    try:
        keyboard_brands = InlineKeyboardMarkup(row_width=4)
        car_brands = cars_db.firms()
        buttons = []
        for i, brand in enumerate(car_brands):
            if i == len(car_brands) - 1:
                button = InlineKeyboardButton(text=brand, callback_data=f"firms|z-z|{brand}",
                                              resize_keyboard=True)
            else:
                button = InlineKeyboardButton(text=brand, callback_data=f"firms|z-z|{brand}")
            buttons.append(button)

        keyboard_brands.add(*buttons)
        return keyboard_brands

    except Exception as e:
        # Обработка исключения
        print(f"Произошла ошибка: {e}")


# Генерация инлайн кнопок(модели авто)
async def models_callback_button(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        firm = callback_query.data.split('|z-z|')[1]
        models = cars_db.models_by_firm(firm)

        # Разделение списка на части по 100 элементов
        button_chunks = [models[i:i + 100] for i in range(0, len(models), 100)]

        # Создание встроенной клавиатуры
        keyboard05 = types.InlineKeyboardMarkup(row_width=3)

        # Добавление кнопок из каждой части списка и отправка сообщений
        for chunk in button_chunks:
            buttons = [types.InlineKeyboardButton(text=model, callback_data=f"omodel\z-z/{model}\z-z/{firm}") for
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
        print(f"Произошла ошибка: {e}")
        await callback_query.message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


# Генерация инлайн кнопок(поколения авто)
async def years_callback_button(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    language = BotDB.get_user_lang(user_id)
    model = callback_query.data.split('\z-z/')[1]
    firm = callback_query.data.split('\z-z/')[2]

    gens = cars_db.years_by_model_and_firm(firm, model)

    keyboard06 = InlineKeyboardMarkup(row_width=1)
    buttons = list()

    for gen in gens:
        button = InlineKeyboardButton(text=gen, callback_data=f"gens_z-z_{gen}_z-z_{model}_z-z_{firm}")
        buttons.append(button)

    keyboard06.add(*buttons)
    if language == 'ru':
        await bot.send_message(callback_query.from_user.id, cfg.ru_change, reply_markup=keyboard06)
    else:
        await bot.send_message(callback_query.from_user.id, cfg.am_change, reply_markup=keyboard06)


async def year_callback_button(callback_query: types.CallbackQuery):
    global ac, vr, sp, vu
    user_id = callback_query.from_user.id
    firm = callback_query.data.split('_z-z_')[3]
    model = callback_query.data.split('_z-z_')[2]
    gen = callback_query.data.split('_z-z_')[1]
    c = '_' + firm + ', ' + model + ', ' + gen + '_'
    car_id = cars_db.get_car_id(firm, model, gen)
    if car_id is None:
        await bot.send_message('5659651535', f"{c} not in cars ID !!!!!!!!!!!!!")
        return await bot.send_message(user_id, "Կապվեք աջակցության հետ Обратитесь в поддержку, у вас возникла "
                                               "проблема 001. @sasapsa")

    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        sad = cfg.ru_sad
        ac = cfg.ru_accept
        sp = cfg.ru_sup
        vr = cfg.ru_vr
        vu = cfg.ru_vu
    elif language == 'am':
        sad = cfg.am_sad
        ac = cfg.am_accept
        sp = cfg.am_sup
        vr = cfg.am_vr
        vu = cfg.am_vu

    login = BotDB.get_user_login(user_id)[0]
    account_id = bot_db.get_id_login(login)
    account_status = bot_car.check_entry_account(login, str(account_id))
    if account_status == "one_inp":
        await bot.send_message(user_id, "Կապվեք աջակցության հետ Обратитесь в поддержку, у вас возникла проблема 002. "
                                        "@sasapsa")
        return
    if account_status:
        if account_status is not None and account_id is not None and login is not None:
            bot_car.add_car_info(login, account_id, car_id)
            await bot.send_message(user_id, f'{sp}')
            await bot.send_message(user_id, f'{vr} {c}',
                                   parse_mode="Markdown")
            await bot.send_message(cfg.chat_id_logs,
                                   f' #newauto {login} разбирает свое первое авто \n{c}',
                                   parse_mode="Markdown")

    else:
        add_status = bot_car.add_car_id(login, account_id, car_id)
        if add_status is True:
            await bot.send_message(user_id, f'{sp}')
            await bot.send_message(user_id, f'{vr} {c}',
                                   parse_mode="Markdown")
            await bot.send_message(cfg.chat_id_logs,
                                   f' #newauto {login} разбирает новое авто \n{c}',
                                   parse_mode="Markdown")

        elif add_status is False:
            await bot.send_message(user_id, f'{vu}')


def register_handlers_car_disassembly(dp: Dispatcher):
    dp.register_callback_query_handler(car_disassembly_callback, lambda c: c.data.startswith('button:'))
    dp.register_callback_query_handler(del_car_callback, lambda c: c.data.startswith('delcar:'))
    dp.register_message_handler(car_disassembly, commands=['car_disassembly'])
    dp.register_message_handler(car_disassembly, commands=['car_disassembly'])
    dp.register_callback_query_handler(models_callback_button, lambda c: c.data.startswith('firms|z-z|'))
    dp.register_callback_query_handler(years_callback_button, lambda c: c.data.startswith('omodel\z-z/'))
    dp.register_callback_query_handler(year_callback_button, lambda c: c.data.startswith('gens_z-z_'))
