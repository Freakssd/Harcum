import datetime
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, MediaGroup
from handlers import order_handlers as ord
from handlers import start_lang_handlers as stas
import config as cfg
from create_bot import bot
from db import BotDB, bot_db
from handlers import car_disassembly_handlers as cdh


bot_db = bot_db()
BotDB = BotDB()


stop_list = ['\start', '/start', '/stop', '/order', 'Запрос', 'Автосервисы (скоро)', 'Авто в разборе',
             'Аккаунт авторазборки',
             '/quick', '/disassembly','/feedback', '/language', '/login', '/account', 'register', 'reg',
             'Авторизация автразборки',
             'Հարցում', 'Ավտոսպասարկում (շուտով)', 'Ավտո վերլուծության մեջ', 'Թույլտվություն ինքնահավաք',
             'ինքնահավաք հաշիվ']

################################


class User(StatesGroup):
    Login = State()
    Password = State()


class Users(StatesGroup):
    account_type = State()
    Login = State()
    Password = State()


#################################


async def logins(message: types.Message):
    global keyboard_RA, b, a
    user_id = message.from_user.id
    if user_id in cfg.ban_list:
        return await bot.send_message(user_id, 'BAN')

    if BotDB.get_user_status(user_id) == 1:
        await account(message)

    else:
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            a = cfg.ru_a
            b = cfg.ru_b
            keyboard_RA = ru_logins_keyboard()
        elif language == 'am':
            a = cfg.am_a
            b = cfg.am_b
            keyboard_RA = am_logins_keyboard()
        await bot.send_message(user_id, a)
        await message.answer(b, reply_markup=keyboard_RA)


def ru_logins_keyboard():
    keyboard_ru_log = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="Aвторизация как авторазборкa", callback_data="reg_type_login"),
        InlineKeyboardButton(text="Регистрация как авторазборки", callback_data="reg_type_register"),

    ]
    keyboard_ru_log.add(*buttons)
    return keyboard_ru_log


def am_logins_keyboard():
    keyboard_am_log = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="Թույլտվություն", callback_data="reg_type_login"),
        InlineKeyboardButton(text="Գրանցվել որպես ինքնահավաք", callback_data="reg_type_register"),

    ]
    keyboard_am_log.add(*buttons)
    return keyboard_am_log


# noinspection PyTypeChecker
async def logins_call(callback_query: types.CallbackQuery):
    d_l = callback_query.data.split('_')[2]
    if d_l == 'login':
        await cmd_login(callback_query)
    elif d_l == 'register':
        await start_registration(callback_query)
    else:
        print('error')


#
#
#  Авторизация
#
#

# @dp.message_handler(Command("login"))
async def cmd_login(message: types.Message):
    # Запуск авторизации - запрос логина
    user_id = message.from_user.id
    if user_id in cfg.ban_list:
        return await bot.send_message(user_id, 'BAN')
    await User.Login.set()
    await bot.send_message(user_id, "Введите логин:")


# @dp.message_handler(state=User.Login)
async def process_login_login(message: types.Message, state: FSMContext):
    # Получение логина и сохранение в состояние
    language = BotDB.get_user_lang(message.from_user.id)
    login = message.text
    if login in stop_list:
        await state.finish()
        await stas.start(message, state)
        return
    if ' ' in login:
        old_login = login
        login = login.replace(' ',  '')
        if language == 'ru':
            await bot.send_message(message.from_user.id, f'В логине {old_login} был убран пробел \n'
                                            f'теперь логин такой - {login}')
        elif language == 'am':
            await bot.send_message(message.from_user.id, f'Մուտքանուն {old_login} մաքրվել է տարածությունը\n'
                                            f'այժմ մուտքն այսպիսին է -{login}')

    await state.update_data(login=login)

    # Запрос пароля
    await User.Password.set()
    await message.reply("Введите пароль:")


# @dp.message_handler(state=User.Password)
async def process_login_password(message: types.Message, state: FSMContext):
    # Получение пароля и логина из состояния
    data = await state.get_data()
    login = data.get('login')
    password = message.text
    if password in stop_list:
        await state.finish()
        await stas.start(message, state)
        return

    user_id = message.from_user.id
    # Проверка логина и пароля в базе данных
    account_d = bot_db.check_account(login, password)
    if account_d:
        # Авторизация успешна
        BotDB.update_user_status(1, login, user_id)
        await message.reply("Авторизация успешна!")
        print(f'Вход в аккаунт{login}, {password}')
    else:
        # Авторизация неуспешна
        await message.answer("Неверный логин или пароль!", reply_markup=reg_login_keyboard())
        await state.finish()
    # Сброс состояния FSM
    await state.finish()


def reg_login_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="Попробовать снова", callback_data="login"),
        InlineKeyboardButton(text="Регистрация", callback_data="register"),

    ]
    keyboard.add(*buttons)
    return keyboard


# noinspection PyTypeChecker
async def login_reg(callback_query: types.CallbackQuery):
    f = callback_query.data
    if f == 'login':
        await cmd_login(callback_query)
    elif f == 'register':
        state = dp.current_state(chat=callback_query.message.chat.id, user=callback_query.from_user.id)
        await start_registration(callback_query, state)

#
#
#  регистрация
#
#

########################################
class RegistrationStates(StatesGroup):
    Login = State()
    Password = State()
    UserType = State(2)
    Name = State()
    Address = State()
    Phone = State()
    Description = State()


#########################################

async def start_registration(callback_query: types.CallbackQuery):
    global d
    if callback_query.from_user.id in cfg.ban_list:
        return await bot.send_message(callback_query.from_user.id, 'BAN')

    await RegistrationStates.Login.set()
    language = BotDB.get_user_lang(callback_query.from_user.id)


    if language == 'ru':
        d = cfg.ru_dd

    elif language == 'am':
        d = cfg.am_dd
    await bot.send_message(callback_query.from_user.id, d)


async def start_login(message: Message, state: FSMContext):
    user_id = message.from_user.id
    global e
    try:
        language = BotDB.get_user_lang(message.from_user.id)
        login = message.text
        # Если пользователь ввел логин, обновите его данные и перейдите к следующему состоянию
        if login in stop_list:
            await state.finish()
            await stas.start(message, state)
            return
        if '/' in login:
            old_login = login
            login = login.replace('/',  '')
            if language == 'ru':
                await bot.send_message(user_id, f'В логине {old_login} был убран слэш \n'
                                                    f'теперь логин такой - {login}')
            elif language == 'am':
                await bot.send_message(user_id, f'Մուտքանուն {old_login} մաքրվել է cлэш\n'
                                                    f'այժմ մուտքն այսպիսին է -{login}')
        if ' ' in login:
            old_login = login
            login = login.replace(' ',  '')
            if language == 'ru':
                await bot.send_message(user_id, f'В логине {old_login} был убран пробел \n'
                                                    f'теперь логин такой - {login}')
            elif language == 'am':
                await bot.send_message(user_id, f'Մուտքանուն {old_login} մաքրվել է տարածությունը\n'
                                                    f'այժմ մուտքն այսպիսին է -{login}')

        await state.update_data(Login=login)
        await RegistrationStates.Password.set()

        if language == 'ru':
            e = cfg.ru_e

        elif language == 'am':
            e = cfg.am_e
        await message.reply(e)
    except Exception as e:
        print(f'error - {e}')
        await state.finish()



async def process_reg_login(message: Message, state: FSMContext):
    global f, g, h
    try:
        passwor = message.text

        if passwor in stop_list:
            await state.finish()
            return
    except Exception:
        print(f'error - {e}')
        await state.finish()
        return
    await state.update_data(Password=passwor)
    user_id = message.from_user.id
    user_name = message.from_user.username

    data = await state.get_data()
    login = data.get('Login')
    password = data.get('Password')
    user_type_acc = data.get('UserType')
    language = BotDB.get_user_lang(message.from_user.id)

    if language == 'ru':
        f = cfg.ru_f
        g = cfg.ru_g
        h = cfg.ru_h

    elif language == 'am':
        f = cfg.am_f
        g = cfg.am_g
        h = cfg.am_h
    existing_account = bot_db.check_login(login)

    if existing_account:
        await message.answer(f)
        await state.finish()
        return
    else:
        await RegistrationStates.Name.set()
        await bot.send_message(user_id, h)


async def process_name(message: types.Message, state: FSMContext):
    global i
    name = message.text
    if name in stop_list:
        await state.finish()
        await stas.start(message, state)
        return
    await state.update_data(Name=name)
    user_id = message.from_user.id

    await RegistrationStates.Address.set()

    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        i = cfg.ru_i

    elif language == 'am':
        i = cfg.am_i

    await bot.send_message(user_id, i)


async def process_address(message: types.Message, state: FSMContext):
    global j
    address = message.text
    if address in stop_list:
        await state.finish()
        await stas.start(message, state)
        return
    await state.update_data(Address=address)

    language = BotDB.get_user_lang(message.from_user.id)

    if language == 'ru':
        j = cfg.ru_j

    elif language == 'am':
        j = cfg.am_j

    await RegistrationStates.Phone.set()

    await message.reply(j)


async def process_phone(message: types.Message, state: FSMContext):
    global k
    phone = message.text
    if phone in stop_list:
        await state.finish()
        await stas.start(message, state)
        return
    await state.update_data(Phone=phone)

    language = BotDB.get_user_lang(message.from_user.id)

    if language == 'ru':
        k = cfg.ru_k

    elif language == 'am':
        k = cfg.am_k

    await RegistrationStates.Description.set()
    await message.reply(k)


async def process_description(message: types.Message, state: FSMContext):
    global f, g
    description = message.text
    if description in stop_list:
        await state.finish()
        await stas.start(message, state)
        return
    await state.update_data(Description=description)
    user_name = message.from_user.username

    if user_name is None:
        user_name = message.from_user.first_name

    user_id = message.from_user.id
    data = await state.get_data()
    login = data.get('Login')
    passwordd = data.get('Password')
    user_typi = 2
    auto_name = data.get('Name')
    address = data.get('Address')
    phone = data.get('Phone')
    description = data.get('Description')
    language = BotDB.get_user_lang(message.from_user.id)
    if language == 'ru':
        f = cfg.ru_f
        g = cfg.ru_g

    elif language == 'am':
        f = cfg.am_f
        g = cfg.am_g

    existing_account = bot_db.check_login(login)
    num_1 = phone
    num_2 = None
    date_time = datetime.datetime.now()
    if existing_account:
        await message.reply(f)
    else:
        bot_db.new_user(login, passwordd, user_typi, user_id, user_name, auto_name, address, num_1, num_2, description,
                        date_time)
        BotDB.update_user_status(1, login, user_id)
        await message.reply(g)
        await bot.send_message(1806719774, f'#newacc Зарегистрировалась новая авторазборка  {login}, {user_id}, {num_1}, @{user_name}')
        print(f'Зарегистрировалась новая авторазборка  {login}, {user_id}, {num_1}, @{user_name}')
    await state.finish()


#
#
#
# Аккаунт
#
#
#


class Change(StatesGroup):
    Login = State()
    Password = State()


################################################################################

async def acc(message: types.Message, login, user_id):
    result = bot_db.user(login)  # Pass the login value as login[0]
    c_user_id = BotDB.get_user_id_login(login)
    user_status = BotDB.get_user_status(c_user_id)
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
        description = row[10]
        site = row[12]
        photo_1 = row[13]
        photo_2 = row[14]
        photo_3 = row[15]

    num_1 = f'☎️ +{num_1}'

    if num_2 is not None:
        num_2 = f'☎️ +{num_2}\n'
    else:
        num_2 = ''

    if site is not None:
        website = '🌎 ' + site
    else:
        website = ''

    if user_type_acc == 2 or user_type_acc == 3 and user_status == 1:
        print('photo', photo_1)
        caption = f'{auto_name}\n\n{address}\n\n{num_1}\n{num_2}\n{description}\n{website}'
        if photo_1 is None:
            await bot.send_message(user_id, caption)
        else:
            media = []

            media.append(types.InputMediaPhoto(media=photo_1, caption=caption))

            if photo_2 is not None:
                media.append(types.InputMediaPhoto(media=photo_2))

            if photo_3 is not None:
                media.append(types.InputMediaPhoto(media=photo_3))

            await bot.send_media_group(chat_id=user_id, media=media)


################################################################################

async def logout(message: types.Message):
    user_id = message.from_user.id
    user_status = BotDB.get_user_status(user_id)
    if user_status == 1:
        BotDB.update_user_status(0, None, user_id)
        language = BotDB.get_user_lang(message.from_user.id)
        if language == 'ru':
            l = cfg.ru_l

        elif language == 'am':
            l = cfg.am_l

        await bot.send_message(user_id, l)

    else:
        await bot.send_message(user_id, 'Вы не можете выйти из аккаунта, так как')
        await logins(message)


####################################################################################

async def change_login(message: types.Message):
    user_id = message.from_user.id
    await Change.Login.set()
    language = BotDB.get_user_lang(message.from_user.id)
    if language == 'ru':
        m = cfg.ru_m

    elif language == 'am':
        m = cfg.am_m
    await bot.send_message(user_id, m)


async def process_change_login(message: types.Message, state: FSMContext):
    language = BotDB.get_user_lang(message.from_user.id)
    new_login = message.text
    if ' ' in new_login:
        oltd_login = new_login
        login = new_login.replace(' ',  '')
        if language == 'ru':
            await bot.send_message(message.from_user.id, f'В логине {oltd_login} был убран пробел \n'
                                            f'теперь логин такой - {login}')
        elif language == 'am':
            await bot.send_message(message.from_user.id, f'Մուտքանուն {oltd_login} մաքրվել է տարածությունը\n'
                                            f'այժմ մուտքն այսպիսին է -{login}')
    user_id = message.from_user.id
    old_login = BotDB.get_user_login(user_id)
    id = bot_db.get_id_login(old_login[0])
    if language == 'ru':
        na = cfg.ru_na
        nb = cfg.ru_nb

    elif language == 'am':
        na = cfg.am_na
        nb = cfg.am_nb
    bot_db.update_login(new_login, id[0])
    BotDB.update_user_status(1, new_login, user_id)
    await bot.send_message(user_id, f'{na} {old_login[0]} {nb} {new_login}')
    await state.finish()


#############################################################################

async def change_password(message: types.Message):
    user_id = message.from_user.id
    language = BotDB.get_user_lang(message.from_user.id)
    if language == 'ru':
        o = cfg.ru_o
    elif language == 'am':
        o = cfg.am_o

    await Change.Password.set()
    await bot.send_message(user_id, o)


# noinspection PyGlobalUndefined
async def process_change_password(message: types.Message, state: FSMContext):
    global old_password
    new_password = message.text
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    res = bot_db.user(login[0])
    for row in res:
        old_password = row[2]
    bot_db.update_password(new_password, login[0])
    language = BotDB.get_user_lang(message.from_user.id)
    if language == 'ru':
        pa = cfg.ru_pa
        pb = cfg.ru_pb

    elif language == 'am':
        pa = cfg.am_pa
        pb = cfg.am_pb
    await bot.send_message(user_id, f'{pa} {old_password} {pb} {new_password}')
    await state.finish()


############################################################################


# noinspection PyGlobalUndefined
async def account(message: types.Message):

    global user_type, password, id_acc, date

    user_id = message.from_user.id
    if user_id in cfg.ban_list:
        return await bot.send_message(user_id, 'BAN')

    user_status = BotDB.get_user_status(user_id)

    if user_status == 1:
        login = BotDB.get_user_login(user_id)
        result = bot_db.user(login[0])  # Pass the login value as login[0]


        user_type = None
        for row in result:
            id_acc = row[0]
            login = row[1]
            password = row[2]
            user_type = row[3]
            date = row[11]
        if user_type is None:
            return
        if message.from_user.username is None:
            c = ' - ' + message.from_user.first_name
        else:
            c = '@' + str(message.from_user.username)
        language = BotDB.get_user_lang(message.from_user.id)
        if language == 'ru':
            if user_type == 1:

                text = f"""Тип аккаунта - <u>партнёр</u>\n
&#128100;Пользователь: {c}
&#128273;Логин: <code>{login}</code>
&#128272;Пароль: <code>{password}</code>
&#129706;Id аккаунта: {id_acc}
&#128467;Дата регистрации: {date[:10:]}"""
                await bot.send_message(user_id, text, parse_mode=types.ParseMode.HTML, reply_markup=ru_account_1_keyboard())
            elif user_type == 2:
                await message.answer(f"Тип аккаунта - <u>авторазборка</u>\n\n"
                                     f"&#128100;Пользователь: {c}\n"
                                     f"&#128273;Логин: <code>{login}</code>\n"
                                     f"&#128272;Пароль: <code>{password}</code>\n"
                                     f"&#129706;Id аккаунта: {id_acc}\n"
                                     f"&#128467;Дата регистрации: {date[:10:]}\n\n",
                                     parse_mode=types.ParseMode.HTML, reply_markup=ru_account_2_keyboard())
            elif user_type == 3:
                text = f"""Тип аккаунта - <u>автосервис</u>\n
&#128100;Пользователь: {c}
&#128273;Логин: <code>{login}</code>
&#128272;Пароль: <code>{password}</code>
&#129706;Id аккаунта: {id_acc}
&#128467;Дата регистрации: {date[:10:]}"""
                await message.answer(text, parse_mode=types.ParseMode.HTML, reply_markup=ru_account_3_keyboard())

        elif language == 'am':

            if user_type == 1:

                text = f"""Հաշվի տեսակը - <u>партнёр</u>\n
&#128100;Օգտատեր: {c}
&#128273;Մուտքանուն: <code>{login}</code>
&#128272;Գաղտնաբառ: <code>{password}</code>
&#129706;Հաշվի Իդ: {id_acc}
&#128467;Գրանցման ամսաթիվ: {date[:10:]}"""
                await bot.send_message(user_id, text, parse_mode=types.ParseMode.HTML,
                                       reply_markup=am_account_1_keyboard())
            elif user_type == 2:
                await message.answer(f"Հաշվի տեսակը - <u>ինքնահավաք</u>\n\n"
                                     f"&#128100;Օգտատեր: {c}\n"
                                     f"&#128273;Մուտքանուն: <code>{login}</code>\n"
                                     f"&#128272;Գաղտնաբառ: <code>{password}</code>\n"
                                     f"&#129706;Հաշվի Իդ: {id_acc}\n"
                                     f"&#128467;Գրանցման ամսաթիվ: {date[:10:]}\n\n",
                                     parse_mode=types.ParseMode.HTML, reply_markup=am_account_2_keyboard())
            elif user_type == 3:
                text = f"""Հաշվի տեսակը - <u>автосервис</u>\n
&#128100;Օգտատեր: {c}
&#128273;Մուտքանուն: <code>{login}</code>
&#128272;Գաղտնաբառ: <code>{password}</code>
&#129706;Հաշվի Իդ: {id_acc}
&#128467;Գրանցման ամսաթիվ: {date[:10:]}"""
                await message.answer(text, parse_mode=types.ParseMode.HTML, reply_markup=am_account_3_keyboard())


    else:
        await logins(message)


def ru_account_2_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Смена логина", callback_data="change_login")
    button2 = InlineKeyboardButton(text="Смена пароля", callback_data="change_password")
    button3 = InlineKeyboardButton(text="Авто в разборе/добавить авто", callback_data="car_wreck")
    button4 = InlineKeyboardButton(text="Моя авторазборка", callback_data="my_car_dismantling")
    button5 = InlineKeyboardButton(text="Выход из аккаунта", callback_data="logout", resize_keyboard=True)
    keyboard.row(button3)
    keyboard.row(button4)
    keyboard.add(button1, button2)
    keyboard.row(button5)
    return keyboard


def ru_account_3_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Смена логина", callback_data="change_login")
    button2 = InlineKeyboardButton(text="Смена пароля", callback_data="change_password")
    button4 = InlineKeyboardButton(text="Мой автосервис", callback_data="my_car_dismantling")
    button5 = InlineKeyboardButton(text="Выход из аккаунта", callback_data="logout", resize_keyboard=True)
    keyboard.row(button4)
    keyboard.add(button1, button2)
    keyboard.row(button5)
    return keyboard


def ru_account_1_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Смена логина", callback_data="change_login")
    button2 = InlineKeyboardButton(text="Смена пароля", callback_data="change_password")
    button3 = InlineKeyboardButton(text="Мои запросы", callback_data="my_query", resize_keyboard=True)
    button4 = InlineKeyboardButton(text="Выход из аккаунта", callback_data="logout", resize_keyboard=True)
    keyboard.row(button3)
    keyboard.add(button1, button2)
    keyboard.row(button4)
    return keyboard


def am_account_2_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Մուտքի փոփոխություն", callback_data="change_login")
    button2 = InlineKeyboardButton(text="Գաղտնաբառի փոփոխություն", callback_data="change_password")
    button3 = InlineKeyboardButton(text="Ես քանդում  եմ մեքենա։", callback_data="car_wreck")
    button4 = InlineKeyboardButton(text="Իմ ինքնահավաքումը", callback_data="my_car_dismantling")
    button5 = InlineKeyboardButton(text="Հաշվից դուրս գալը", callback_data="logout", resize_keyboard=True)
    keyboard.row(button3)
    keyboard.row(button4)
    keyboard.add(button1, button2)
    keyboard.row(button5)
    return keyboard


def am_account_3_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Մուտքի փոփոխություն", callback_data="change_login")
    button2 = InlineKeyboardButton(text="Գաղտնաբառի փոփոխություն", callback_data="change_password")
    button4 = InlineKeyboardButton(text="Իմ Ավտոսպասարկում", callback_data="my_car_dismantling")
    button5 = InlineKeyboardButton(text="Հաշվից դուրս գալը", callback_data="logout", resize_keyboard=True)
    keyboard.row(button4)
    keyboard.add(button1, button2)
    keyboard.row(button5)
    return keyboard


def am_account_1_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Մուտքի փոփոխություն", callback_data="change_login")
    button2 = InlineKeyboardButton(text="Գաղտնաբառի փոփոխություն", callback_data="change_password")
    button3 = InlineKeyboardButton(text="Իմ հարցումները", callback_data="my_query", resize_keyboard=True)
    button4 = InlineKeyboardButton(text="Հաշվից դուրս գալը", callback_data="logout", resize_keyboard=True)
    keyboard.row(button3)
    keyboard.add(button1, button2)
    keyboard.row(button4)
    return keyboard


#
#
#
# Аккаунт авторазборки
#
#
#

async def car_dismantling(message: types.Message):
    user_id = message.from_user.id
    user_status = BotDB.get_user_status(user_id)
    login = BotDB.get_user_login(user_id)

    result = bot_db.user(login[0])  # Pass the login value as login[0]


    user_type = None
    for row in result:
        id_acc = row[0]
        login = row[1]
        password = row[2]
        user_type = row[3]
        auto_name = row[6]
        address = row[7]
        num_1 = row[8]
        num_2 = row[9]
        description = row[10]
        date = row[11]
        site = row[12]
        photo_1 = row[13]
        photo_2 = row[14]
        photo_3 = row[15]

    num_1 = f'☎️ +{num_1}'

    if num_2 is not None:
        num_2 = f'☎️ +{num_2}\n'
    else:
        num_2 = ''

    if site is not None:
        website = '🌎 ' + site
    else:
        website = ''

    if user_type == 2 or user_type == 3 and user_status == 1:
        print(photo_1)
        caption = f'{auto_name}\n\n{address}\n\n{num_1}\n{num_2}\n{description}\n{website}'
        if photo_1 is None:
            await bot.send_message(user_id, caption)
        else:
            media = []

            media.append(types.InputMediaPhoto(media=photo_1, caption=caption))

            if photo_2 is not None:
                media.append(types.InputMediaPhoto(media=photo_2))

            if photo_3 is not None:
                media.append(types.InputMediaPhoto(media=photo_3))

            await bot.send_media_group(chat_id=user_id, media=media)
        language = BotDB.get_user_lang(user_id)

        if language == 'ru':
            r = cfg.ru_r
            keyboard = ru_account_car_keyboard()

        elif language == 'am':
            r = cfg.am_r
            keyboard = am_account_car_keyboard()
        await bot.send_message(user_id, r, reply_markup=keyboard)


def ru_account_car_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Добавить/Изменить второй номер телефона", callback_data="change_num_2")
    button2 = InlineKeyboardButton(text="Добавить/Изменить первый номер телефона", callback_data="change_num_1")
    button3 = InlineKeyboardButton(text="Добавить/Изменить фото", callback_data="change_photo")
    button7 = InlineKeyboardButton(text="Добавить/Изменить сайт", callback_data="change_site")
    button4 = InlineKeyboardButton(text="Изменить описание", callback_data="change_description")
    button5 = InlineKeyboardButton(text="Изменить название", callback_data="change_name")
    keyboard.add(button3)
    keyboard.row(button7)
    keyboard.row(button5, button4)
    keyboard.row(button1)
    keyboard.row(button2)
    return keyboard


def am_account_car_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Ավելացնել / փոխել երկրորդ հեռախոսահամարը", callback_data="change_num_2")
    button2 = InlineKeyboardButton(text="Ավելացնել / փոխել առաջին հեռախոսահամարը", callback_data="change_num_1")
    button3 = InlineKeyboardButton(text="Ավելացնել / խմբագրել լուսանկարը", callback_data="change_photo")
    button7 = InlineKeyboardButton(text="Ավելացնել / փոփոխել կայքը", callback_data="change_site")
    button4 = InlineKeyboardButton(text="Փոխել նկարագրությունը", callback_data="change_description")
    button5 = InlineKeyboardButton(text="Փոխել անունը", callback_data="change_name")
    keyboard.add(button3)
    keyboard.row(button7)
    keyboard.row(button5, button4)
    keyboard.row(button1)
    keyboard.row(button2)
    return keyboard


# noinspection PyTypeChecker
async def process_car_account(callback_query: types.CallbackQuery):
    call = callback_query.data
    if call == 'change_num_2':
        await change_num_2(callback_query)
    elif call == 'change_num_1':
        await change_num_1(callback_query)
    elif call == 'change_photo':
        await add_photo_1(callback_query)
    elif call == 'change_description':
        await change_description(callback_query)
    elif call == 'change_name':
        await change_name(callback_query)
    elif call == 'change_site':
        await change_ssite(callback_query)
    elif call == 'delete_account':
        await bot.send_message(callback_query.from_user.id, 'Для удаления аккаунта пишите в поддержку - /feedback')


#
#
#
#
#
#
#
#


class Change_account_car(StatesGroup):
    num_1 = State()
    num_2 = State()
    photo_1 = State()
    photo_2 = State()
    photo_3 = State()
    description = State()
    name = State()
    site = State()


###################################################################


async def change_ssite(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.site.set()
    await bot.send_message(user_id, 'Введите url сайта:\n Մուտքագրեք կայքի url-ն:')


# noinspection PyGlobalUndefined
async def process_change_ssite(message: types.Message, state: FSMContext):
    site = message.text
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    bot_db.update_site(site, login[0])
    await bot.send_message(user_id, f'Вы добавили сайт\nԴուք ավելացրել եք կայք')
    await state.finish()


###################################################################


async def change_name(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.name.set()
    await bot.send_message(user_id, 'Введите новое название:\nՄուտքագրեք նոր անուն:')


# noinspection PyGlobalUndefined
async def process_change_name(message: types.Message, state: FSMContext):
    name = message.text
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    bot_db.update_name(name, login[0])
    await bot.send_message(user_id, f'Вы изменили название\nԴուք փոխել եք անունը')
    await state.finish()


###################################################################


async def change_description(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.description.set()
    await bot.send_message(user_id, 'Введите новое описание:\nՄուտքագրեք նոր Նկարագրություն:')


# noinspection PyGlobalUndefined
async def process_change_description(message: types.Message, state: FSMContext):
    description = message.text
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    bot_db.update_description(description, login[0])
    await bot.send_message(user_id, f'Вы изменили описание\nԴուք փոխել եք նկարագրությունը')
    await state.finish()


###################################################################


async def change_num_2(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.num_2.set()
    await bot.send_message(user_id, 'Введите второй номер телефона:\nՄուտքագրեք երկրորդ հեռախոսահամարը:')


# noinspection PyGlobalUndefined
async def process_change_num_2(message: types.Message, state: FSMContext):
    num_2 = message.text
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    bot_db.update_num_2(num_2, login[0])
    await bot.send_message(user_id, f'Вы изменили второй номер телефона\nԴուք փոխել եք երկրորդ հեռախոսահամարը')
    await state.finish()


##################################################################


async def change_num_1(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.num_1.set()
    await bot.send_message(user_id, 'Введите первый номер телефона:\nՄուտքագրեք առաջին հեռախոսահամարը:')


# noinspection PyGlobalUndefined
async def process_change_num_1(message: types.Message, state: FSMContext):
    num_1 = message.text
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    bot_db.update_num_1(num_1, login[0])
    await bot.send_message(user_id, f'Вы изменили первый номер телефона\nԴուք փոխել եք առաջին հեռախոսահամարը')
    await state.finish()


####################################################################


async def add_photo_1(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.photo_1.set()
    await bot.send_message(user_id, 'Отправьте первую фотографию\n ❗️ОТПРАВЛЯЙТЕ ОДНУ ФОТОГРАФИЮ❗️\n\n Ուղարկեք առաջին լուսանկարը \n ❗ՈՒՂԱՐԿԵՔ ՄԵԿ ԼՈՒՍԱՆԿԱՐ️ ️❗️')


async def process_add_photo_1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    file_id_1 = message.photo[-1].file_id  # Первая фотография
    bot_db.update_photo_1(file_id_1, login[0])
    await state.finish()
    await message.reply("1-ая Фотография сохраненa.\n1-ին լուսանկարը պահպանված է:", reply_markup=photo_keyboard_1())
    # Завершаем FSM-состояние


def photo_keyboard_1():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Добавить eщё фото\nԱվելացնել ավելի շատ լուսանկարներ", callback_data="ad_photo_2")
    button2 = InlineKeyboardButton(text="Оставить одну фотографию\nԹողնել մեկ լուսանկար", callback_data="leave_photo_2")
    keyboard.row(button1)
    keyboard.row(button2)
    return keyboard


# noinspection PyTypeChecker
async def process_photo_1(callback_query: types.CallbackQuery):
    call = callback_query.data
    if call == 'ad_photo_2':
        await add_photo_2(callback_query)

    elif call == 'leave_photo_2':
        await bot.send_message(callback_query.from_user.id, 'Добавлена одна фотография\nԱվելացված է մեկ լուսանկար')


async def add_photo_2(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.photo_2.set()
    await bot.send_message(user_id, "Отправьте вторую фотографию\n❗️ОТПРАВЛЯЙТЕ ОДНУ ФОТОГРАФИЮ❗️\n\nՈւղարկեք երկրորդ լուսանկարը\n ❗ՈՒՂԱՐԿԵՔ ՄԵԿ ԼՈՒՍԱՆԿԱՐ❗️")


async def process_add_photo_2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    file_id_2 = message.photo[-1].file_id  # Первая фотография
    bot_db.update_photo_2(file_id_2, login[0])

    await message.reply("2-ая Фотография сохраненa.\n2-րդ լուսանկարը պահպանված է:", reply_markup=photo_keyboard_2())
    await state.finish()  # Завершаем FSM-состояние


def photo_keyboard_2():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Добавить eщё фото\nԱվելացնել ավելի շատ լուսանկարներ", callback_data="addd_photo_3")
    button2 = InlineKeyboardButton(text="Оставить две фотографии\nԹողնել երկու լուսանկար", callback_data="leave_photo_3")
    keyboard.row(button1)
    keyboard.row(button2)
    return keyboard


# noinspection PyTypeChecker
async def process_photo_2(callback_query: types.CallbackQuery):
    call = callback_query.data
    if call == 'addd_photo_3':
        await add_photo_3(callback_query)

    elif call == 'leave_photo_3':
        await bot.send_message(callback_query.from_user.id, 'Добавлена вторая фотография\nԱվելացված է երկրորդ լուսանկարը')


async def add_photo_3(message: types.Message):
    user_id = message.from_user.id
    await Change_account_car.photo_3.set()
    await bot.send_message(user_id, "Отправьте третью фотографию\n❗️ОТПРАВЛЯЙТЕ ОДНУ ФОТОГРАФИЮ❗️\n\nՈւղարկեք երրորդ Լուսանկարը")


async def process_add_photo_3(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    file_id_2 = message.photo[-1].file_id  # Первая фотография
    bot_db.update_photo_3(file_id_2, login[0])

    await message.reply("3 фотографии сохранены.\n3 լուսանկարները պահպանված են:")
    await state.finish()  # Завершаем FSM-состояние


# noinspection PyTypeChecker
async def process_account(callback_query: types.CallbackQuery):
    call = callback_query.data
    if call == 'logout':
        await logout(callback_query)
    elif call == 'change_login':
        await change_login(callback_query)
    elif call == 'my_query':
        await ord.order_switch(callback_query, s=1)
    elif call == 'change_password':
        await change_password(callback_query)
    elif call == 'car_wreck':
        await cdh.car_disassembly(callback_query)
    elif call == 'my_car_dismantling':
        await car_dismantling(callback_query)


def register_handlers_reg(dp: Dispatcher):
    dp.register_message_handler(logins, commands=['login', 'register'])
    dp.register_callback_query_handler(logins_call, lambda query: query.data.startswith('reg_type_'))
    # Авторизация
    dp.register_message_handler(cmd_login, commands=['log'])
    dp.register_message_handler(process_login_login, state=User.Login)
    dp.register_message_handler(process_login_password, state=User.Password)
    dp.register_callback_query_handler(login_reg, lambda query: query.data.startswith(('login', 'register')))
    # Регистрация
    dp.register_message_handler(start_registration, commands=['reg'])
    dp.register_message_handler(start_login, state=RegistrationStates.Login)
    dp.register_message_handler(process_reg_login, state=RegistrationStates.Password)

    dp.register_message_handler(process_name, state=RegistrationStates.Name)
    dp.register_message_handler(process_phone, state=RegistrationStates.Phone)
    dp.register_message_handler(process_address, state=RegistrationStates.Address)
    dp.register_message_handler(process_description, state=RegistrationStates.Description)
    # Аккаунт
    dp.register_message_handler(logout, commands=['logout'])
    dp.register_message_handler(account, commands=['account'])
    dp.register_message_handler(change_login, commands=['change_login'])
    dp.register_message_handler(process_change_login, state=Change.Login)
    dp.register_message_handler(change_password, commands=['change_password'])
    dp.register_message_handler(process_change_password, state=Change.Password)
    dp.register_callback_query_handler(process_account, lambda query: query.data.startswith(('logout', "my_query",
                                                                                             "change_password",
                                                                                             "change_login",
                                                                                             "my_car_dismantling",
                                                                                             "car_wreck")))
    # аккаунт авторазборки
    dp.register_message_handler(car_dismantling, commands=['car_dismanting'])
    dp.register_callback_query_handler(process_car_account, lambda query: query.data.startswith(('change_num_2',
                                                                                                 'change_num_1',
                                                                                                 'add_photo',
                                                                                                 'change_photo',
                                                                                                 'change_description',
                                                                                                 'delete_account',
                                                                                                 'change_name',
                                                                                                 'change_site'
                                                                                                 )))
    dp.register_message_handler(change_num_2, commands=['change_num_2'])
    dp.register_message_handler(process_change_num_2, state=Change_account_car.num_2)
    dp.register_message_handler(change_num_1, commands=['change_num_1'])
    dp.register_message_handler(process_change_num_1, state=Change_account_car.num_1)
    dp.register_message_handler(add_photo_1, commands=['add_photo'])
    dp.register_message_handler(process_add_photo_1, content_types=types.ContentType.PHOTO,
                                state=Change_account_car.photo_1)
    dp.register_callback_query_handler(process_photo_1,
                                       lambda query: query.data.startswith(('ad_photo_2', 'leave_photo_2')))
    dp.register_message_handler(add_photo_2, commands=['add_photo_2'])
    dp.register_message_handler(process_add_photo_2, content_types=types.ContentType.PHOTO,
                                state=Change_account_car.photo_2)
    dp.register_callback_query_handler(process_photo_2,
                                       lambda query: query.data.startswith(('addd_photo_3', 'leave_photo_3')))
    dp.register_message_handler(add_photo_3, commands=['add_photo_3'])
    dp.register_message_handler(process_add_photo_3, content_types=types.ContentType.PHOTO,
                                state=Change_account_car.photo_3)
    dp.register_message_handler(change_description, commands=['change_description'])
    dp.register_message_handler(process_change_description, state=Change_account_car.description)

    dp.register_message_handler(change_name, commands=['change_name'])
    dp.register_message_handler(process_change_name, state=Change_account_car.name)

    dp.register_message_handler(change_ssite, commands=['change_site'])
    dp.register_message_handler(process_change_ssite, state=Change_account_car.site)
