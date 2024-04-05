import datetime
import asyncio
import time
from handlers import order_handlers as ord
from handlers import reg_handlers as reg
from handlers import unanswered_requests as unan
from aiogram import types
from handlers import disassembly_handlers as dis
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from db import BotDB
import config as cfg

BotDB = BotDB()

# Главное меню

async def start(message: types.Message, state: FSMContext):

    try:
        await state.finish()
    except Exception:
        pass
    user_id = message.from_user.id

    if user_id in cfg.ban_list:
        return await bot.send_message(user_id, 'BAN')

    if message.from_user.username is None:
        c = message.from_user.first_name

    else:
        c = '@' + str(message.from_user.username)
    # Проверяем, есть ли пользователь в базе данны
    if BotDB.user_exists(user_id):
        # Если пользователь уже есть в базе данных, получаем его язык
        language = BotDB.get_user_lang(user_id)
        if language is None:
            print('New user: ' + c + ' | ' + str(message.from_user.id) + ' | ' +
                  str(datetime.datetime.now()))
            await set_language_command(message)
            return

    else:
        # Если пользователь новый, добавляем его в базу данных и предлагаем выбрать язык
        BotDB.add_user(user_id)
        print('New user: ' + c + ' | ' + str(message.from_user.id) + ' | ' +
              str(datetime.datetime.now()))
        await set_language_command(message)

        time.sleep(1)

    user_id = message.from_user.id
    name = message.from_user.first_name
    user_status = BotDB.get_user_status(user_id)
    language = BotDB.get_user_lang(user_id)
    for i in cfg.admin_id:
        if str(i) == str(user_id):

            await bot.send_message(user_id, '/admin_panel')

    if user_status == 0:

        if language == 'ru':

            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            button1 = types.KeyboardButton(text=cfg.t1)
            button3 = types.KeyboardButton(text=cfg.t3)
            button4 = types.KeyboardButton(text=cfg.t5)
            keyboard.row(button1)
            keyboard.add(button3, button4)

            text = f'Привет, {name}!'
            await bot.send_message(message.chat.id, text)
            await bot.send_message(message.chat.id, cfg.sm)
            await bot.send_message(message.chat.id, cfg.km)
            await bot.send_message(message.chat.id, cfg.fm)
            await bot.send_message(message.chat.id, cfg.tm, reply_markup=keyboard)

        elif language == 'am':

            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            button1 = types.KeyboardButton(text=cfg.c1)
            button3 = types.KeyboardButton(text=cfg.c3)
            button4 = types.KeyboardButton(text=cfg.c5)
            keyboard.row(button1)
            keyboard.add(button3, button4)

            text = f'Ողջույն {name}:'
            await bot.send_message(message.chat.id, text)
            await bot.send_message(message.chat.id, cfg.sc)
            await bot.send_message(message.chat.id, cfg.km)
            await bot.send_message(message.chat.id, cfg.fc)
            await bot.send_message(message.chat.id, cfg.cm, reply_markup=keyboard)

    else:

        if language == 'ru':

            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            button1 = types.KeyboardButton(text=cfg.t1)
            button3 = types.KeyboardButton(text=cfg.t3)
            button4 = types.KeyboardButton(text=cfg.t5)
            keyboard.row(button1)
            keyboard.add(button3, button4)

            text = f'Привет, {name}!'
            await bot.send_message(message.chat.id, text)
            await bot.send_message(message.chat.id, cfg.sm)
            await bot.send_message(message.chat.id, cfg.km)
            await bot.send_message(message.chat.id, cfg.fm)
            await bot.send_message(message.chat.id, cfg.tms, reply_markup=keyboard)

        elif language == 'am':

            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            button1 = types.KeyboardButton(text=cfg.c1)
            button3 = types.KeyboardButton(text=cfg.c3)
            button4 = types.KeyboardButton(text=cfg.c5)
            keyboard.row(button1)
            keyboard.add(button3, button4)

            text = f'Ողջույն {name}:'
            await bot.send_message(message.chat.id, text)
            await bot.send_message(message.chat.id, cfg.sc)
            await bot.send_message(message.chat.id, cfg.km)
            await bot.send_message(message.chat.id, cfg.fc)
            await bot.send_message(message.chat.id, cfg.cms, reply_markup=keyboard)


# Обработчик нажатия на кнопку
async def button_handler(message: types.Message):
    user_id = message.from_user.id
    if message.text == cfg.t1 or message.text == cfg.c1:
        await ord.order_switch(message)
    elif message.text == cfg.t3 or message.text == cfg.c3:
        await unan.unanswered(message)
    elif message.text == cfg.t2 or message.text == cfg.c2:
        await bot.send_message(user_id, 'Раздел скоро появится')
    elif message.text == cfg.t5 or message.text == cfg.c5:
        await reg.account(message)
    elif message.text == cfg.t4 or message.text == cfg.c4:
        await reg.logins(message)


# выбор языка
async def set_language_callback(callback_query: types.CallbackQuery):
    global c1, a1, b1
    user_id = callback_query.from_user.id
    language = callback_query.data

    user_status = BotDB.get_user_status(user_id)

    if BotDB.get_user_lang(user_id) == 'ru':
        BotDB.update_user_lang(language, user_id)

    elif BotDB.get_user_lang(user_id) == 'am':
        BotDB.update_user_lang(language, user_id)

    else:
        BotDB.insert_user_lang(user_id, language)

    await bot.answer_callback_query(callback_query.id)
    language = BotDB.get_user_lang(user_id)

    if user_status == 0:
        if language == 'ru':
            text1 = f'Привет, {callback_query.from_user.first_name}!'
            c1 = cfg.sm
            a1 = cfg.fm
            b1 = cfg.tm

        elif language == 'am':
            text1 = f'Ողջույն {callback_query.from_user.first_name}:'
            c1 = cfg.sc
            a1 = cfg.fc
            b1 = cfg.cm

        else:
            text1 = f'English, {callback_query.from_user.first_name}!'
            c1 = 'I can search for auto parts from Harcum-Pahestamaser.com partners.'
            a1 = '/start'
        await bot.edit_message_text(text1, callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, c1)
        await bot.send_message(callback_query.message.chat.id, a1)
        await bot.send_message(callback_query.message.chat.id, b1)
    else:

        if language == 'ru':
            text1 = f'Привет, {callback_query.from_user.first_name}!'
            c1 = cfg.sm
            a1 = cfg.fm
            b1 = cfg.tms

        elif language == 'am':
            text1 = f'Ողջույն {callback_query.from_user.first_name}:'
            c1 = cfg.sc
            a1 = cfg.fc
            b1 = cfg.cms

        await bot.edit_message_text(text1, callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, c1)
        await bot.send_message(callback_query.message.chat.id, a1)
        await bot.send_message(callback_query.message.chat.id, b1)


# команда language
# @dp.message_handler(commands=['language'])
async def set_language_command(message: types.Message):
    # user_id = message.from_user.id

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text='Русский', callback_data='ru'),
        types.InlineKeyboardButton(text='Հայերեն', callback_data='am')
    )

    await message.reply('Выберите язык / Ընտրեք լեզուն:', reply_markup=keyboard)


async def feedback_mess(message: types.Message):
    user_id = message.from_user.id
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        text = (
            'Если вы нашли ошибку в работе бота или хотите помочь работе бота, '
            'обращайтесь по контактам ниже\n\n'
            'чат - https://t.me/+rsp5qOiyXVdkMDNi\n'
            'деловые предложения - @AkErevanskiy002\n\n'
        )
    elif language == 'am':
        text = (
            'Եթե \ u200b \ u200bբոտի աշխատանքի մեջ սխալ եք գտել կամ ցանկանում եք օգնել բոտի աշխատանքին,'
            'կապվեք ստորև նշված կոնտակտների հետ\n'
            'Զրուցարան - https://t.me/+rsp5qOiyXVdkMDNi\n'
            'բիզնես առաջարկներ - @AkErevanskiy002\n\n'
        )
    else:
        text = 'Unsupported language'

    await bot.send_message(user_id, text, parse_mode="HTML")


def register_handlers_start(dp):
    dp.register_message_handler(button_handler, text=[cfg.t1, cfg.t2, cfg.t3, cfg.t4, cfg.t5, cfg.c1, cfg.c2, cfg.c3,
                                                      cfg.c4, cfg.c5], )

    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(set_language_command, commands=['language'])
    dp.register_callback_query_handler(set_language_callback, lambda c: c.data in ['ru', 'am'], state='*')
    dp.register_message_handler(feedback_mess, commands=['feedback'])
