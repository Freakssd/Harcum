import asyncio
import datetime
import requests

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup
from db import BotDB, bot_car, bot_db
from create_bot import dp, bot
from handlers import reg_handlers as reg
import config as cfg

BotDB = BotDB()
bot_car = bot_car()
bot_db = bot_db()


async def admin_panel(message: types.Message):
    updates = await bot.get_updates()
    user_id = message.from_user.id
    for update in updates:
        print(update)
    await bot.send_message(user_id, f"{message.from_user.id}")
    print('Админ - ', user_id, str(datetime.datetime.now())[5:-10])

    if str(user_id) in cfg.admin_id:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(

            types.InlineKeyboardButton(text='✅СТАТИСТИКА✅',
                                       callback_data='897979754_stat_5414541231'),

            types.InlineKeyboardButton(text='✅отправить сообщение разборкам✅',
                                       callback_data='897979754_send_message_auto5414541231'),

            types.InlineKeyboardButton(text='✅отправить фото и текст разборкам✅',
                                       callback_data='897979754_send_photo_auto5414541231'),

            types.InlineKeyboardButton(text='✅отправить сообщение пользовател✅',
                                       callback_data='897979754_send_message_user5414541231'),

            types.InlineKeyboardButton(text='❌отправить фото и текст пользователям',
                                       callback_data='897979754_send_photo_user5414541231'),

            types.InlineKeyboardButton(text='❌добавить авто в запрос',
                                       callback_data='897979754_add_car_5414541231'),

            types.InlineKeyboardButton(text='❌add_car',
                                       callback_data='897979754_add_car_5414541231'),

        )

        await bot.send_message(user_id, f'Админ - {user_id} {str(datetime.datetime.now())[5:-10]}',
                               reply_markup=keyboard)


class Send(StatesGroup):
    mess_auto = State()
    mess_user = State()
    photo_1 = State()


async def ap(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    c = callback.data

    if c == '897979754_send_message_auto5414541231':
        print("mess_auto")
        await Send.mess_auto.set()
        await bot.send_message(user_id, "Введите сообщение")

    elif c == '897979754_send_message_user5414541231':
        print("mess_user")
        await Send.mess_user.set()
        await bot.send_message(user_id, "Введите сообщение")

    elif c == '897979754_send_photo_auto5414541231':
        await add_photo_1(callback)
        print(1)

    elif c == '897979754_stat_5414541231':
        with open('auto_rb.txt', 'r') as f:
            rb = f.read()
        with open('users.txt', 'r') as f:
            us = f.read()

        k = bot_db.get_auto_rb()
        ka = f' ~{len(k)}~ примерное кол-во авторазборок б/у заблокированных'
        u = bot_db.get_len_users()
        lu = f' ~{u}~ примерное кол-во пользователей б/у заблокированных'
        txt = f'''СТАТИСТИКА\n\n{rb}\n\n{us}\n\n{ka}\n\n{lu}'''
        await bot.send_message(user_id, txt)


async def message_auto(message: types.Message, state: FSMContext):
    txt = message.text
    print(txt)
    idss = bot_db.get_all_user_ids()
    user_id = message.from_user.id
    data = await state.get_data()
    photo_1 = data.get('photo_1')

    ids = list(set(idss))
    print(ids)
    block = 0
    inn = 0
    media1 = types.InputMediaPhoto(media=photo_1, caption=txt)
    media = [media1]
    for i in ids:
        try:
            try:
                await bot.send_media_group(chat_id=i, media=media)
            except Exception:
                await bot.send_message(i, txt)
            print(True, i)
            inn += 1
        except Exception:
            print('block', i)
            block += 1
    await bot.send_message(user_id, f'blocked - {block}, in bot - {inn}')
    await state.finish()
    with open('auto_rb.txt', 'w') as f:
        f.write(f'AUTORAZBORKI:\nblocked - {block}, in bot - {inn} on date {str(datetime.datetime.now())[5:-10]}')


async def message_user(message: types.Message, state: FSMContext):
    txt = message.text
    print(txt)
    ids = bot_db.get_users_id()
    user_id = message.from_user.id
    data = await state.get_data()
    photo_1 = data.get('photo_1')

    print(ids)
    block = 0
    inn = 0
    media1 = types.InputMediaPhoto(media=photo_1, caption=txt)
    media = [media1]
    for i in ids:
        try:
            try:
                await bot.send_media_group(chat_id=i, media=media)
            except Exception:
                await bot.send_message(i, txt)
            print(True, i)
            inn += 1
        except Exception:
            print('block', i)
            block += 1
    await bot.send_message(user_id, f'users, blocked - {block}, in bot - {inn}')
    await state.finish()
    with open('users.txt', 'w') as f:
        f.write(f'USERS:\nblocked - {block}, in bot - {inn} on date {str(datetime.datetime.now())[5:-10]}')


async def add_photo_1(messadge: types.Message):
    print(2)
    user_id = messadge.from_user.id
    await Send.photo_1.set()
    await bot.send_message(user_id,
                           'Отправьте первую фотографию\n ❗️ОТПРАВЛЯЙТЕ ОДНУ ФОТОГРАФИЮ❗️\n\n Ուղարկեք առաջին լուսանկարը \n ❗ՈՒՂԱՐԿԵՔ ՄԵԿ ԼՈՒՍԱՆԿԱՐ️ ️❗️')


async def process_add_photo_1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    login = BotDB.get_user_login(user_id)
    file_id_1 = message.photo[-1].file_id  # Первая фотография
    await state.update_data(photo_1=file_id_1)
    print(file_id_1)

    await message.reply("1-ая Фотография сохраненa.\n1-ին լուսանկարը պահպանված է:")
    await Send.mess_auto.set()
    await bot.send_message(user_id, "Введите сообщение")


async def ban(message: types.Message):
    user_id = message.from_user.id
    # Проверяем, отправитель коамнды - администратор
    if str(user_id) in cfg.admin_id:
        # Получаем user_id из аргумента команды
        try:
            user_id_to_ban = int(message.text.split()[1])

            # Отправляем сообщение пользователю, что он забанен
            await bot.send_message(user_id_to_ban, 'You have been banned')

            # Баним пользователя в чате
            cfg.ban_list.append(user_id_to_ban)
            await bot.send_message(user_id, f"Пользователь {user_id_to_ban} забанен.")
            print(f"Пользователь {user_id_to_ban} забанен.")

        except Exception as e:
            print(cfg.ban_list)
            await bot.send_message(user_id, cfg.ban_list)
            result_message = "Некорректный формат команды. Используйте /ban [user_id]"
            # Отправляем результат в чат
            await message.reply(result_message)
    else:
        await bot.send_message(user_id, 'Вы не админ')


async def my_id(message: types.Message):
    print(message.from_user.id)
    await bot.send_message(message.from_user.id, message.from_user.id)


async def delete_order(message: types.Message):
    txt = message.text
    c = txt.split("_")
    print(c)
    await bot.delete_message(chat_id=int(c[3]), message_id=int(c[2]))


def register_handlers_admin_panel(dp: Dispatcher):
    dp.register_message_handler(ban, commands=['ban'])
    dp.register_message_handler(delete_order, commands=['delete_order'])
    dp.register_message_handler(my_id, commands=['myid'])
    dp.register_message_handler(admin_panel, commands=['admin_panel'])
    dp.register_callback_query_handler(ap, lambda c: c.data.startswith(
        ('897979754_add_car_5414541231', '897979754_add_car_5414541231',
         '897979754_send_message_auto5414541231', '897979754_send_photo_auto5414541231',
         '897979754_send_message_user5414541231', '897979754_send_photo_user5414541231', '897979754_stat_5414541231')))
    dp.register_message_handler(message_auto, state=Send.mess_auto)
    dp.register_message_handler(message_user, state=Send.mess_user)
    dp.register_message_handler(add_photo_1, commands=['add_photo_sdaasd'])
    dp.register_message_handler(process_add_photo_1, content_types=types.ContentType.PHOTO, state=Send.photo_1)
