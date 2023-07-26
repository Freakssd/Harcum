import tracemalloc

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InputMediaPhoto
from aiogram.types import InlineKeyboardMarkup

import config as cfg

tracemalloc.start()
from db import BotDB, bot_car, bot_db
from create_bot import bot

BotDB = BotDB()
bot_car = bot_car()
bot_db = bot_db()


def switches_ru(eq):
    keyboard = InlineKeyboardMarkup(row_width=2)
    es = eq.split(', ')
    buttons = [InlineKeyboardButton(text=model, callback_data=f"om-{model}") for model in es]
    keyboard.add(*buttons)
    button = InlineKeyboardButton(text='Нет нужного автомобиля в списке', callback_data='omsk')
    keyboard.row(button)
    return keyboard


def switches_am(eq):
    keyboard = InlineKeyboardMarkup(row_width=2)
    es = eq.split(', ')
    buttons = [InlineKeyboardButton(text=model, callback_data=f"om-{model}") for model in es]
    keyboard.add(*buttons)
    button = InlineKeyboardButton(text='Theանկում ճիշտ մեքենա չկա', callback_data='omsk')
    keyboard.row(button)
    return keyboard


# ... (остальной код)


async def order_switch(message: types.Message, s=0):
    global kl
    try:
        user_id = message.from_user.id
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
                            keyboard = switches_ru(enq[0])

                        elif language == 'am':
                            keyboard = switches_am(enq[0])
                        # В этом месте обработаем enq[0]
                        await bot.send_message(user_id, kl, reply_markup=keyboard)
                    else:
                        eq.extend(enq)
                        if language == 'ru':
                            keyboard = switches_ru(", ".join(eq))

                        elif language == 'am':
                            keyboard = switches_am(", ".join(eq))

                        await bot.send_message(user_id, kl, reply_markup=keyboard)
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
    user_id = callback_query.from_user.id
    data = callback_query.data
    if data == 'omsk':
        await order(callback_query)
        return
    data = data[3::]
    print(data)
    dt = data.split(' ')
    print(dt)
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
        print(f"11Произошла ошибка: {e}")
        await message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


# Генерация инлайн кнопок
def generate_brands_inline_keyboard():
    try:
        keyboard_brands = InlineKeyboardMarkup(row_width=4)
        car_brands = [
            "Audi", "BMW", "Cadillac", "Chevrolet", "Chrysler", "Citroen", "Daewoo",
            "Dodge", "Fiat", "Ford", "Honda", "Hyundai", "Infiniti", "Jeep", "Kia",
            "Land Rover", "Lexus", "Mazda", "Mercedes", "Mitsubishi", "Nissan", "Opel",
            "Peugeot", "Porsche", "Renault", "Skoda", "SsangYong", "Subaru", "Suzuki",
            "Toyota", "Volkswagen", "Volvo", "Нет марки авто в моем списке"
        ]

        buttons = []
        for i, brand in enumerate(car_brands):
            if i == len(car_brands) - 1:
                button = InlineKeyboardButton(text=brand, callback_data=f"ocondition-{brand}",
                                              resize_keyboard=True)
            else:
                button = InlineKeyboardButton(text=brand, callback_data=f"ocondition-{brand}")
            buttons.append(button)

        keyboard_brands.add(*buttons)
        return keyboard_brands

    except Exception as e:
        # Обработка исключения
        print(f"22Произошла ошибка: {e}")


# @dp.callback_query_handler(lambda c: c.data.startswith('condition:'))
async def models_callback_button(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        brand = callback_query.data.split('-')[1]
        language = BotDB.get_user_lang(user_id)
        brand_keyboard_mapping = {
            'BMW': generate_bmw_models_inline_keyboard,
            'Audi': generate_audi_models_inline_keyboard,
            'Cadillac': generate_cadillac_models_inline_keyboard,
            'Chevrolet': generate_chevrolet_models_inline_keyboard,
            'Chrysler': generate_chrysler_models_inline_keyboard,
            'Citroen': generate_citroen_models_inline_keyboard,
            'Daewoo': generate_daewoo_models_inline_keyboard,
            'Dodge': generate_dodge_models_inline_keyboard,
            'Fiat': generate_fiat_models_inline_keyboard,
            'Ford': generate_ford_models_inline_keyboard,
            'Honda': generate_honda_models_inline_keyboard,
            'Hyundai': generate_hyundai_models_inline_keyboard,
            'Infiniti': generate_infiniti_models_inline_keyboard,
            'Jeep': generate_jeep_models_inline_keyboard,
            'Kia': generate_kia_models_inline_keyboard,
            'Land Rover': generate_land_rover_models_inline_keyboard,
            'Lexus': generate_lexus_models_inline_keyboard,
            'Mazda': generate_mazda_models_inline_keyboard,
            'Mercedes': generate_mercedes_models_inline_keyboard,
            'Mitsubishi': generate_mitsubishi_models_inline_keyboard,
            'Nissan': generate_nissan_models_inline_keyboard,
            'Opel': generate_opel_models_inline_keyboard,
            'Peugeot': generate_peugeot_models_inline_keyboard,
            'Porsche': generate_porsche_models_inline_keyboard,
            'Renault': generate_renault_models_inline_keyboard,
            'Skoda': generate_skoda_models_inline_keyboard,
            'SsangYong': generate_ssangyong_models_inline_keyboard,
            'Subaru': generate_subaru_models_inline_keyboard,
            'Suzuki': generate_suzuki_models_inline_keyboard,
            'Toyota': generate_toyota_models_inline_keyboard,
            'Volkswagen': generate_volkswagen_models_inline_keyboard,
            'Volvo': generate_volvo_models_inline_keyboard,
        }
        if language == 'ru':
            if brand in brand_keyboard_mapping:
                keyboard = brand_keyboard_mapping[brand](brand, language)
                await bot.send_message(callback_query.from_user.id, cfg.ru_message)
                await bot.send_message(callback_query.from_user.id, brand)
                await bot.send_message(callback_query.from_user.id, cfg.ru_model_message)
                await bot.send_message(callback_query.from_user.id, cfg.ru_change, reply_markup=keyboard)
            else:
                keyboard = other_car_brands_inline_keyboard()
                await bot.send_message(callback_query.from_user.id, cfg.ru_other_mark, reply_markup=keyboard)

        else:
            if brand in brand_keyboard_mapping:
                keyboard = brand_keyboard_mapping[brand](brand, language)
                await bot.send_message(callback_query.from_user.id, cfg.am_message)
                await bot.send_message(callback_query.from_user.id, brand)
                await bot.send_message(callback_query.from_user.id, cfg.am_model_message)
                await bot.send_message(callback_query.from_user.id, cfg.am_change, reply_markup=keyboard)
            else:
                keyboard = other_car_brands_inline_keyboard()
                await bot.send_message(callback_query.from_user.id, cfg.am_other_mark, reply_markup=keyboard)

    except Exception as e:
        # Обработка исключения
        print(f"33Произошла ошибка: {e}")
        await callback_query.message.reply("Произошла ошибка. Пожалуйста, повторите попытку позже.")


def generate_models_inline_keyboard(brand, models, language):
    keyboard = InlineKeyboardMarkup(row_width=4)
    buttons = []
    for model in models:
        cmodel = model
        model = model.replace('&', '')
        model = model.replace("-", "_")
        button = InlineKeyboardButton(text=cmodel, callback_data=f"omodel-{model}-{brand}")
        buttons.append(button)
    other_brand = f'other_{brand}'
    other_brand = other_brand.lower()
    keyboard.add(*buttons)
    if language == 'ru':
        keyboard.row(
            InlineKeyboardButton(text=cfg.ru_other_brnd, callback_data=f"omodel-{other_brand}-{brand}",
                                 resize_keyboard=True))
    elif language == 'am':
        keyboard.row(
            InlineKeyboardButton(text=cfg.am_other_brnd, callback_data=f"omodel-{other_brand}-{brand}",
                                 resize_keyboard=True))
    return keyboard


def generate_audi_models_inline_keyboard(brand, language):
    models = ["100", "80", "A3", "A4", "A5", "A6", "A7", "A8", "Allroad", "Q3", "Q5", "Q7", "TT"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_bmw_models_inline_keyboard(brand, language):
    models = ["1er", "3er", "5 GT", "5er", "6er", "7er", "X1", "X3", "X5", "X6"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_cadillac_models_inline_keyboard(brand, language):
    models = ["ATS", "BLS", "CTS", "Escalade", "SRX", "STS", "XT5"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_chevrolet_models_inline_keyboard(brand, language):
    models = ["Aveo", "Blazer", "Camaro", "Captiva", "Cobalt", "Cruze", "Epica", "Evanda", "Express", "Lacetti",
              "Lanos", "Niva", "Orlando", "Rezzo", "Spark", "Suburban", "Tahoe", "Tracker", "TrailBlazer", "Viva"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_chrysler_models_inline_keyboard(brand, language):
    models = ["300C", "300M", "Concorde", "Grand Voyager", "Pacifica", "PT Cruiser", "Sebring", "Town Country",
              "Voyager"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_citroen_models_inline_keyboard(brand, language):
    models = ["Berlingo", "C-Crosser", "C-Elysee", "C2", "C3", "C3 Picasso", "C4", "C4 Aircross", "C4 Picasso", "C5",
              "DS4", "Jumper", "Jumpy", "Xsara", "Xsara Picasso"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_daewoo_models_inline_keyboard(brand, language):
    models = ["Espero", "Gentra", "Leganza", "Matiz", "Nexia", "Nubira"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_dodge_models_inline_keyboard(brand, language):
    models = ["Caliber", "Caravan", "Grand Caravan", "Intrepid", "Journey", "Neon", "Nitro", "Ram", "Stratus"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_fiat_models_inline_keyboard(brand, language):
    models = ["Albea", "Brava", "Bravo", "Croma", "Doblo", "Ducato", "Linea", "Marea", "Palio", "Panda", "Punto",
              "Scudo", "Stilo", "Tempra", "Tipo", "Ulysse"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_ford_models_inline_keyboard(brand, language):
    models = ["C-Max", "Escape", "Explorer", "Fiesta", "Focus", "Fusion", "Galaxy", "Kuga", "Maverick", "Mondeo",
              "Ranger", "S Max", "Tourneo Connect", "Transit", "Transit Connect"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_honda_models_inline_keyboard(brand, language):
    models = ["Accord", "Civic", "CR-V", "Crosstour", "Element", "Fit", "HR-V", "Inspire", "Integra", "Jazz", "Legend",
              "Logo", "Odyssey", "Pilot", "Prelude", "Stepwgn", "Stream"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_hyundai_models_inline_keyboard(brand, language):
    models = ["Accent", "Creta", "Elantra", "Equus", "Galloper", "Getz", "Grand Starex", "Grandeur", "H-1", "i20",
              "i30", "ix35", "ix55", "Lantra", "Matrix", "NF", "Porter", "Santa Fe", "Solaris", "Sonata", "Starex",
              "Terracan", "Trajet", "Tucson"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_infiniti_models_inline_keyboard(brand, language):
    models = ["EX", "FX", "G", "JX", "M", "Q", "QX"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_jeep_models_inline_keyboard(brand, language):
    models = ["Cherokee", "Commander", "Compass", "Grand Cherokee", "Liberty", "Patriot", "Wrangler"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_kia_models_inline_keyboard(brand, language):
    models = ["Bongo", "Carens", "Carnival", "Ceed", "Cerato", "K5", "Magentis", "Mohave", "Optima", "Picanto",
              "Quoris", "Rio", "Rio X line", "Seltos", "Shuma", "Sorento", "Soul", "Spectra", "Sportage", "Venga"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_land_rover_models_inline_keyboard(brand, language):
    models = ["Defender", "Discovery", "Freelander", "Range Rover", "Range Rover Evoque", "Range Rover Sport"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_lexus_models_inline_keyboard(brand, language):
    models = ["ES", "GS", "GX", "IS", "LS", "LX", "RX"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_mazda_models_inline_keyboard(brand, language):
    models = ["2", "3", "323", "5", "6", "626", "Bongo", "BT-50", "Capella", "CX 5", "CX 7", "CX 9", "Demio", "Familia",
              "MPV", "Premacy", "RX-8", "Tribute"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_mercedes_models_inline_keyboard(brand, language):
    models = ["A class", "B class", "C class", "CL class", "CLA class", "CLC class", "CLK class", "CLS class",
              "E class", "G class", "GL class", "GLA class", "GLB class", "GLC class", "GLE class", "GLK class",
              "GLS class", "M class", "R class", "S class", "SL class", "SLK class", "Sprinter", "V class", "Vito"]
    return generate_models_inline_keyboard(brand, models, language)


def generate_mitsubishi_models_inline_keyboard(brand, language):
    models = [
        "ASX", "Carisma", "Colt", "Galant", "Grandis", "L200", "Lancer", "Outlander",
        "Outlander XL", "Pajero", "Pajero Sport", "RVR"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_nissan_models_inline_keyboard(brand, language):
    models = [
        "Almera", "Almera Classic", "Juke", "Maxima", "Maxima QX", "Micra", "Murano", "Navara",
        "Note", "Pathfinder", "Patrol", "Primera", "Qashqai", "Skyline", "Sunny", "Terrano",
        "Tiida", "X-Trail"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_opel_models_inline_keyboard(brand, language):
    models = [
        "Agila", "Antara", "Astra", "Combo", "Corsa", "Frontera", "Insignia", "Meriva",
        "Mokka", "Movano", "Omega", "Sintra", "Vectra", "Vivaro", "Zafira"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_peugeot_models_inline_keyboard(brand, language):
    models = [
        "107", "206", "3008", "307", "308", "4007", "406", "407", "408",
        "Boxer", "Expert", "Partner", "Traveller"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_porsche_models_inline_keyboard(brand, language):
    models = [
        "911", "Cayenne", "Cayman", "Macan", "Panamera"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_renault_models_inline_keyboard(brand, language):
    models = [
        "Arkana", "Clio", "Dokker", "Duster", "Fluence", "Kangoo", "Kaptur", "Koleos",
        "Laguna", "Logan", "Master", "Megane", "Sandero", "Scenic", "Symbol", "Trafic"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_skoda_models_inline_keyboard(brand, language):
    models = [
        "Fabia", "Felicia", "Kodiaq", "Octavia", "Rapid", "Roomster", "Karoq", "Superb", "Yeti"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_ssangyong_models_inline_keyboard(brand, language):
    models = [
        "Actyon", "Actyon Sports", "Istana", "Korando", "Kyron", "Musso", "Rexton", "Stavic"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_subaru_models_inline_keyboard(brand, language):
    models = [
        "Forester", "Impreza", "Impreza WRX", "Legacy", "Outback", "Tribeca", "XV"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_suzuki_models_inline_keyboard(brand, language):
    models = [
        "Aerio", "Baleno", "Cultus", "Escudo", "Grand Vitara", "Ignis", "Jimny",
        "Liana", "Splash", "Swift", "SX4", "SX4 Sedan", "Vitara", "Wagon R", "XL-7"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_toyota_models_inline_keyboard(brand, language):
    models = [
        "4 Runner", "Alphard", "Auris", "Avensis", "Caldina", "Camry", "Carina",
        "Carina E", "Celica", "Chaser", "Corolla", "Crown", "Estima", "Harrier",
        "Highlander", "Hilux Pick Up", "Land Cruiser", "Land Cruiser Prado", "Mark II",
        "Matrix", "Prius", "RAV4", "Tundra", "Venza", "Verso", "Yaris"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_volkswagen_models_inline_keyboard(brand, language):
    models = [
        "Amarok", "Bora", "Caddy", "Caravelle", "Crafter", "Golf", "Golf Plus",
        "Jetta", "Multivan", "Passat", "Phaeton", "Polo", "Scirocco", "Sharan",
        "Tiguan", "Touareg", "Touran", "Transporter", "Vento"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def generate_volvo_models_inline_keyboard(brand, language):
    models = [
        "850", "960", "C30", "S40", "S60", "S70", "S80", "V40", "V70", "XC60",
        "XC70", "XC90"
    ]
    return generate_models_inline_keyboard(brand, models, language)


def other_car_brands_inline_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=4)
    buttons = [
        InlineKeyboardButton(text="Acura", callback_data=f"oyear-Non-Non-Acura"),
        InlineKeyboardButton(text="Alfa Romeo", callback_data=f"oyear-Non-Non-Alfa Romeo"),
        InlineKeyboardButton(text="Aston Martin", callback_data=f"oyear-Non-Non-Aston Martin"),
        InlineKeyboardButton(text="Aurus", callback_data="oyear-Non-Non-Aurus"),
        InlineKeyboardButton(text="Bentley", callback_data="oyear-Non-Non-Bentley"),
        InlineKeyboardButton(text="Brilliance", callback_data="oyear-Non-Non-Brilliance"),
        InlineKeyboardButton(text="Buick", callback_data="oyear-Non-Non-Buick"),
        InlineKeyboardButton(text="BYD", callback_data="oyear-Non-Non-BYD"),
        InlineKeyboardButton(text="Changan", callback_data="oyear-Non-Non-Changan"),
        InlineKeyboardButton(text="Chery", callback_data="oyear-Non-Non-Chery"),
        InlineKeyboardButton(text="Daihatsu", callback_data="oyear-Non-Non-Daihatsu"),
        InlineKeyboardButton(text="Datsun", callback_data="oyear-Non-Non-Datsun"),
        InlineKeyboardButton(text="DongFeng", callback_data="oyear-Non-Non-DongFeng"),
        InlineKeyboardButton(text="Evolute", callback_data="oyear-Non-Non-Evolute"),
        InlineKeyboardButton(text="Exeed", callback_data="oyear-Non-Non-Exeed"),
        InlineKeyboardButton(text="FAW", callback_data="oyear-Non-Non-FAW"),
        InlineKeyboardButton(text="Ferrari", callback_data="oyear-Non-Non-Ferrari"),
        InlineKeyboardButton(text="Foton", callback_data="oyear-Non-Non-Foton"),
        InlineKeyboardButton(text="GAC", callback_data="oyear-Non-Non-GAC"),
        InlineKeyboardButton(text="GAZ", callback_data="oyear-Non-Non-GAZ"),
        InlineKeyboardButton(text="Geely", callback_data="oyear-Non-Non-Geely"),
        InlineKeyboardButton(text="Genesis", callback_data="oyear-Non-Non-Genesis"),
        InlineKeyboardButton(text="GMC", callback_data="oyear-Non-Non-GMC"),
        InlineKeyboardButton(text="Great Wall", callback_data="oyear-Non-Non-Great Wall"),
        InlineKeyboardButton(text="Hafei", callback_data="oyear-Non-Non-Hafei"),
        InlineKeyboardButton(text="Haima", callback_data="oyear-Non-Non-Haima"),
        InlineKeyboardButton(text="Haval", callback_data="oyear-Non-Non-Haval"),
        InlineKeyboardButton(text="Hawtai", callback_data="oyear-Non-Non-Hawtai"),
        InlineKeyboardButton(text="Hongqi", callback_data="oyear-Non-Non-Hongqi"),
        InlineKeyboardButton(text="Hummer", callback_data="oyear-Non-Non-Hummer"),
        InlineKeyboardButton(text="Iran Khordo", callback_data="oyear-Non-Non-Iran Khordo"),
        InlineKeyboardButton(text="Isuzu", callback_data="oyear-Non-Non-Isuzu"),
        InlineKeyboardButton(text="JAC", callback_data="oyear-Non-Non-JAC"),
        InlineKeyboardButton(text="Jaguar", callback_data="oyear-Non-Non-Jaguar"),
        InlineKeyboardButton(text="LADA", callback_data="oyear-Non-Non-LADA"),
        InlineKeyboardButton(text="Lamborghini", callback_data="oyear-Non-Non-Lamborghini"),
        InlineKeyboardButton(text="Lancia", callback_data="oyear-Non-Non-Lancia"),
        InlineKeyboardButton(text="Lifan", callback_data="oyear-Non-Non-Lifan"),
        InlineKeyboardButton(text="Lincoln", callback_data="oyear-Non-Non-Lincoln"),
        InlineKeyboardButton(text="Luxgen", callback_data="oyear-Non-Non-Luxgen"),
        InlineKeyboardButton(text="Maserati", callback_data="oyear-Non-Non-Maserati"),
        InlineKeyboardButton(text="Maybach", callback_data="oyear-Non-Non-Maybach"),
        InlineKeyboardButton(text="Mercury", callback_data="oyear-Non-Non-Mercury"),
        InlineKeyboardButton(text="MG", callback_data="oyear-Non-Non-MG"),
        InlineKeyboardButton(text="Mini", callback_data="oyear-Non-Non-Mini"),
        InlineKeyboardButton(text="Moskvich", callback_data="oyear-Non-Non-Moskvich"),
        InlineKeyboardButton(text="Omoda", callback_data="oyear-Non-Non-Omoda"),
        InlineKeyboardButton(text="Plymouth", callback_data="oyear-Non-Non-Plymouth"),
        InlineKeyboardButton(text="Pontiac", callback_data="oyear-Non-Non-Pontiac"),
        InlineKeyboardButton(text="Ravon", callback_data="oyear-Non-Non-"),
        InlineKeyboardButton(text="Rolls-Royce", callback_data="oyear-Non-Non-Rolls Royce"),
        InlineKeyboardButton(text="Rover", callback_data="oyear-Non-Non-Rover"),
        InlineKeyboardButton(text="Saab", callback_data="oyear-Non-Non-Saab"),
        InlineKeyboardButton(text="Saturn", callback_data="oyear-Non-Non-Saturn"),
        InlineKeyboardButton(text="Scion", callback_data="oyear-Non-Non-Scion"),
        InlineKeyboardButton(text="Seat", callback_data="oyear-Non-Non-Seat"),
        InlineKeyboardButton(text="Smart", callback_data="oyear-Non-Non-Smart"),
        InlineKeyboardButton(text="TagAZ", callback_data="oyear-Non-Non-TagAZ"),
        InlineKeyboardButton(text="Tesla", callback_data="oyear-Non-Non-Tesla"),
        InlineKeyboardButton(text="UAZ", callback_data="oyear-Non-Non-UAZ"),
        InlineKeyboardButton(text="Vortex", callback_data="oyear-Non-Non-Vortex"),
        InlineKeyboardButton(text="ZAZ", callback_data="oyear-Non-Non-ZAZ"),
        InlineKeyboardButton(text="Zotye", callback_data="oyear-Non-Non-Zotye"),
        InlineKeyboardButton(text="ZX auto", callback_data="oyear-Non-Non-ZX auto")
    ]

    keyboard.add(*buttons)
    return keyboard


# @dp.callback_query_handler(lambda c: c.data.startswith('model:'))
async def years_callback_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    model = callback_query.data.split('-')[1]
    brand = callback_query.data.split('-')[2]
    if '_' in model:
        model = model.replace("_", " ")

    c = '_*' + brand + ' ' + model + '*_'
    language = BotDB.get_user_lang(user_id)

    aa = 'Հիանալի է, Հիմա ես գիտեմ ձեր մեքենայի մակնիշը և մոդելը'
    ba = 'Դուք պետք է նշեք թողարկման տարին'
    ca = "Ընտրեք նշված ցուցակից"
    car_models = {
        "100": generate_years_audi_100,
        "80": generate_years_audi_80,
        "A3": generate_years_audi_A3,
        "A4": generate_years_audi_A4,
        "A5": generate_years_audi_A5,
        "A6": generate_years_audi_A6,
        "A7": generate_years_audi_A7,
        "A8": generate_years_audi_A8,
        "Allroad": generate_years_audi_Allroad,
        "Q3": generate_years_audi_Q3,
        "Q5": generate_years_audi_Q5,
        "Q7": generate_years_audi_Q7,
        "TT": generate_years_audi_TT,

        "1er": generate_years_bmw_1er,
        "3er": generate_years_bmw_3er,
        "5 GT": generate_years_bmw_5GT,
        "5er": generate_years_bmw_5er,
        "6er": generate_years_bmw_6er,
        "7er": generate_years_bmw_7er,
        "X1": generate_years_bmw_X1,
        "X3": generate_years_bmw_X3,
        "X5": generate_years_bmw_X5,
        "X6": generate_years_bmw_X6,

        "ATS": generate_years_cadillac_ATS,
        "BLS": generate_years_cadillac_BLS,
        "CTS": generate_years_cadillac_CTS,
        "Escalade": generate_years_cadillac_Escalade,
        "SRX": generate_years_cadillac_SRX,
        "STS": generate_years_cadillac_STS,
        "XT5": generate_years_cadillac_XT5,

        "Aveo": generate_years_chevrolet_Aveo,
        "Blazer": generate_years_chevrolet_Blazer,
        "Camaro": generate_years_chevrolet_Camaro,
        "Captiva": generate_years_chevrolet_Captiva,
        "Cobalt": generate_years_chevrolet_Cobalt,
        "Cruze": generate_years_chevrolet_Cruze,
        "Epica": generate_years_chevrolet_Epica,
        "Evanda": generate_years_chevrolet_Evanda,
        "Express": generate_years_chevrolet_Express,
        "Lacetti": generate_years_chevrolet_Lacetti,
        "Lanos": generate_years_chevrolet_Lanos,
        "Niva": generate_years_chevrolet_Niva,
        "Orlando": generate_years_chevrolet_Orlando,
        "Rezzo": generate_years_chevrolet_Rezzo,
        "Spark": generate_years_chevrolet_Spark,
        "Suburban": generate_years_chevrolet_Suburban,
        "Tahoe": generate_years_chevrolet_Tahoe,
        "Tracker": generate_years_chevrolet_Tracker,
        "TrailBlazer": generate_years_chevrolet_TrailBlazer,
        "Viva": generate_years_chevrolet_Viva,

        "300C": generate_years_chrysler_300C,
        "300M": generate_years_chrysler_300M,
        "Concorde": generate_years_chrysler_Concorde,
        "Grand Voyager": generate_years_chrysler_Grand_Voyager,
        "Pacifica": generate_years_chrysler_Pacifica,
        "PT Cruiser": generate_years_chrysler_PT_cruiser,
        "Sebring": generate_years_chrysler_Sebring,
        "Town Country": generate_years_chrysler_Town_Country,
        "Voyager": generate_years_chrysler_Voyager,

        "Berlingo": generate_years_citroen_berlingo,
        "C Crosser": generate_years_citroen_c_crosser,
        "C Elysee": generate_years_citroen_c_elysee,
        "C2": generate_years_citroen_c2,
        "C3": generate_years_citroen_c3,
        "C3 Picasso": generate_years_citroen_c3_picasso,
        "C4": generate_years_citroen_c4,
        "C4 Aircross": generate_years_citroen_c4_aircross,
        "C4 Picasso": generate_years_citroen_c4_picasso,
        "C5": generate_years_citroen_c5,
        "DS4": generate_years_citroen_ds4,
        "Jumper": generate_years_citroen_jumper,
        "Jumpy": generate_years_citroen_jumpy,
        "Xsara": generate_years_citroen_xsara,
        "Xsara Picasso": generate_years_citroen_xsara_picasso,

        "Espero": generate_years_daewoo_espero,
        "Gentra": generate_years_daewoo_gentra,
        "Leganza": generate_years_daewoo_leganza,
        "Matiz": generate_years_daewoo_matiz,
        "Nexia": generate_years_daewoo_nexia,
        "Nubira": generate_years_daewoo_nubira,

        "Caliber": generate_years_dodge_caliber,
        "Caravan": generate_years_dodge_caravan,
        "Grand Caravan": generate_years_dodge_grand_caravan,
        "Intrepid": generate_years_dodge_intrepid,
        "Journey": generate_years_dodge_journey,
        "Neon": generate_years_dodge_neon,
        "Nitro": generate_years_dodge_nitro,
        "Ram": generate_years_dodge_ram,
        "Stratus": generate_years_dodge_stratus,

        "Albea": generate_years_fiat_Albea,
        "Brava": generate_years_fiat_Brava,
        "Bravo": generate_years_fiat_Bravo,
        "Croma": generate_years_fiat_Croma,
        "Doblo": generate_years_fiat_Doblo,
        "Ducato": generate_years_fiat_Ducato,
        "Linea": generate_years_fiat_Linea,
        "Marea": generate_years_fiat_Marea,
        "Palio": generate_years_fiat_Palio,
        "Panda": generate_years_fiat_Panda,
        "Punto": generate_years_fiat_Punto,
        "Scudo": generate_years_fiat_Scudo,
        "Stilo": generate_years_fiat_Stilo,
        "Tempra": generate_years_fiat_Tempra,
        "Tipo": generate_years_fiat_Tipo,
        "Ulysse": generate_years_fiat_Ulysse,

        "C Max": generate_years_ford_C_Max,
        "Escape": generate_years_ford_Escape,
        "Explorer": generate_years_ford_Explorer,
        "Fiesta": generate_years_ford_Fiesta,
        "Focus": generate_years_ford_Focus,
        "Fusion": generate_years_ford_Fusion,
        "Galaxy": generate_years_ford_Galaxy,
        "Kuga": generate_years_ford_Kuga,
        "Maverick": generate_years_ford_Maverick,
        "Mondeo": generate_years_ford_Mondeo,
        "Ranger": generate_years_ford_Ranger,
        "S Max": generate_years_ford_S_Max,
        "Tourneo Connect": generate_years_ford_Tourneo_Connect,
        "Transit": generate_years_ford_Transit,
        "Transit Connect": generate_years_ford_Transit_Connect,

        "Accord": generate_years_honda_Accord,
        "Civic": generate_years_honda_Civic,
        "CR V": generate_years_honda_CR_V,
        "Crosstour": generate_years_honda_Crosstour,
        "Element": generate_years_honda_Element,
        "Fit": generate_years_honda_Fit,
        "HR V": generate_years_honda_HR_V,
        "Inspire": generate_years_honda_Inspire,
        "Integra": generate_years_honda_Integra,
        "Jazz": generate_years_honda_Jazz,
        "Legend": generate_years_honda_Legend,
        "Logo": generate_years_honda_Logo,
        "Odyssey": generate_years_honda_Odyssey,
        "Pilot": generate_years_honda_Pilot,
        "Prelude": generate_years_honda_Prelude,
        "Stepwgn": generate_years_honda_Stepwgn,
        "Stream": generate_years_honda_Stream,

        "Accent": generate_years_hyundai_Accent,
        "Creta": generate_years_hyundai_Creta,
        "Elantra": generate_years_hyundai_Elantra,
        "Equus": generate_years_hyundai_Equus,
        "Galloper": generate_years_hyundai_Galloper,
        "Getz": generate_years_hyundai_Getz,
        "Grand Starex": generate_years_hyundai_Grand_Starex,
        "Grandeur": generate_years_hyundai_Grandeur,
        "H 1": generate_years_hyundai_H_1,
        "i20": generate_years_hyundai_i20,
        "i30": generate_years_hyundai_i30,
        "i40": generate_years_hyundai_i40,
        "ix35": generate_years_hyundai_ix35,
        "ix55": generate_years_hyundai_ix55,
        "Lantra": generate_years_hyundai_Lantra,
        "Matrix": generate_years_hyundai_Matrix,
        "NF": generate_years_hyundai_NF,
        "Porter": generate_years_hyundai_Porter,
        "Santa Fe": generate_years_hyundai_Santa_Fe,
        "Solaris": generate_years_hyundai_Solaris,
        "Sonata": generate_years_hyundai_Sonata,
        "Starex": generate_years_hyundai_Starex,
        "Terracan": generate_years_hyundai_Terracan,
        "Trajet": generate_years_hyundai_Trajet,
        "Tucson": generate_years_hyundai_Tucson,

        "EX": generate_years_infiniti_EX,
        "FX": generate_years_infiniti_FX,
        "G": generate_years_infiniti_G,
        "JX": generate_years_infiniti_JX,
        "M": generate_years_infiniti_M,
        "Q": generate_years_infiniti_Q,
        "QX": generate_years_infiniti_QX,

        "Cherokee": generate_years_jeep_Cherokee,
        "Commander": generate_years_jeep_Commander,
        "Compass": generate_years_jeep_Compass,
        "Grand Cherokee": generate_years_jeep_Grand_Cherokee,
        "Liberty": generate_years_jeep_Liberty,
        "Patriot": generate_years_jeep_Patriot,
        "Wrangler": generate_years_jeep_Wrangler,

        "Bongo": generate_years_kia_Bongo,
        "Carens": generate_years_kia_Carens,
        "Carnival": generate_years_kia_Carnival,
        "Ceed": generate_years_kia_Ceed,
        "Cerato": generate_years_kia_Cerato,
        "K5": generate_years_kia_K5,
        "Magentis": generate_years_kia_Magentis,
        "Mohave": generate_years_kia_Mohave,
        "Optima": generate_years_kia_Optima,
        "Picanto": generate_years_kia_Picanto,
        "Quoris": generate_years_kia_Quoris,
        "Rio": generate_years_kia_Rio,
        "Rio X line": generate_years_kia_Rio_X_line,
        "Seltos": generate_years_kia_Seltos,
        "Shuma": generate_years_kia_Shuma,
        "Sorento": generate_years_kia_Sorento,
        "Soul": generate_years_kia_Soul,
        "Spectra": generate_years_kia_Spectra,
        "Sportage": generate_years_kia_Sportage,
        "Venga": generate_years_kia_Venga,

        "Defender": generate_years_land_rover_Defender,
        "Discovery": generate_years_land_rover_Discovery,
        "Freelander": generate_years_land_rover_Freelander,
        "Range Rover": generate_years_land_rover_Range_Rover,
        "Range Rover Evoque": generate_years_land_rover_Range_Rover_Evoque,
        "Range Rover Sport": generate_years_land_rover_Range_Rover_Sport,

        "ES": generate_years_lexus_ES,
        "GS": generate_years_lexus_GS,
        "GX": generate_years_lexus_GX,
        "IS": generate_years_lexus_IS,
        "LS": generate_years_lexus_LS,
        "LX": generate_years_lexus_LX,
        "RX": generate_years_lexus_RX,

        "2": generate_years_mazda_2,
        "3": generate_years_mazda_3,
        "323": generate_years_mazda_323,
        "5": generate_years_mazda_5,
        "6": generate_years_mazda_6,
        "626": generate_years_mazda_626,
        "Bongo": generate_years_mazda_Bongo,
        "BT 50": generate_years_mazda_BT_50,
        "Capella": generate_years_mazda_Capella,
        "CX 5": generate_years_mazda_CX_5,
        "CX 7": generate_years_mazda_CX_7,
        "CX 9": generate_years_mazda_CX_9,
        "Demio": generate_years_mazda_Demio,
        "Familia": generate_years_mazda_Familia,
        "MPV": generate_years_mazda_MPV,
        "Premacy": generate_years_mazda_Premacy,
        "RX 8": generate_years_mazda_RX_8,

        "Tribute": generate_years_mazda_Tribute,
        "A class": generate_years_mercedes_A_class,
        "B class": generate_years_mercedes_B_class,
        "C class": generate_years_mercedes_C_class,
        "CL class": generate_years_mercedes_CL_class,
        "CLA class": generate_years_mercedes_CLA_class,
        "CLC class": generate_years_mercedes_CLC_class,
        "CLK class": generate_years_mercedes_CLK_class,
        "CLS class": generate_years_mercedes_CLS_class,
        "E class": generate_years_mercedes_E_class,
        "G class": generate_years_mercedes_G_class,
        "GL class": generate_years_mercedes_GL_class,
        "GLA class": generate_years_mercedes_GLA_class,
        "GLB class": generate_years_mercedes_GLB_class,
        "GLC class": generate_years_mercedes_GLC_class,
        "GLE class": generate_years_mercedes_GLE_class,
        "GLK class": generate_years_mercedes_GLK_class,
        "GLS class": generate_years_mercedes_GLS_class,
        "M class": generate_years_mercedes_M_class,
        "R class": generate_years_mercedes_R_class,
        "S class": generate_years_mercedes_S_class,
        "SL class": generate_years_mercedes_SL_class,
        "SLK class": generate_years_mercedes_SLK_class,
        "Sprinter": generate_years_mercedes_Sprinter,
        "V class": generate_years_mercedes_V_class,
        "Vito": generate_years_mercedes_Vito,

        "ASX": generate_years_mitsubishi_ASX,
        "Carisma": generate_years_mitsubishi_Carisma,
        "Colt": generate_years_mitsubishi_Colt,
        "Galant": generate_years_mitsubishi_Galant,
        "Grandis": generate_years_mitsubishi_Grandis,
        "L200": generate_years_mitsubishi_L200,
        "Lancer": generate_years_mitsubishi_Lancer,
        "Outlander": generate_years_mitsubishi_Outlander,
        "Outlander XL": generate_years_mitsubishi_Outlander_XL,
        "Pajero": generate_years_mitsubishi_Pajero,
        "Pajero Sport": generate_years_mitsubishi_Pajero_Sport,
        "RVR": generate_years_mitsubishi_RVR,

        "Almera": generate_years_nissan_Almera,
        "Almera Classic": generate_years_nissan_Almera_Classic,
        "Juke": generate_years_nissan_Juke,
        "Maxima": generate_years_nissan_Maxima,
        "Maxima QX": generate_years_nissan_Maxima_QX,
        "Micra": generate_years_nissan_Micra,
        "Murano": generate_years_nissan_Murano,
        "Navara": generate_years_nissan_Navara,
        "Note": generate_years_nissan_Note,
        "Pathfinder": generate_years_nissan_Pathfinder,
        "Patrol": generate_years_nissan_Patrol,
        "Primera": generate_years_nissan_Primera,
        "Qashqai": generate_years_nissan_Qashqai,
        "Sunny": generate_years_nissan_Sunny,
        "Terrano": generate_years_nissan_Terrano,
        "Skyline": generate_years_nissan_Skyline,
        "Teana": generate_years_nissan_Teana,
        "Tiida": generate_years_nissan_Tiida,
        "X Trail": generate_years_nissan_X_Trail,

        "Agila": generate_years_opel_Agila,
        "Antara": generate_years_opel_Antara,
        "Astra": generate_years_opel_Astra,
        "Combo": generate_years_opel_Combo,
        "Corsa": generate_years_opel_Corsa,
        "Frontera": generate_years_opel_Frontera,
        "Insignia": generate_years_opel_Insignia,
        "Meriva": generate_years_opel_Meriva,
        "Mokka": generate_years_opel_Mokka,
        "Movano": generate_years_opel_Movano,
        "Omega": generate_years_opel_Omega,
        "Sintra": generate_years_opel_Sintra,
        "Vectra": generate_years_opel_Vectra,
        "Vivaro": generate_years_opel_Vivaro,
        "Zafira": generate_years_opel_Zafira,

        "107": generate_years_peugeot_107,
        "206": generate_years_peugeot_206,
        "3008": generate_years_peugeot_3008,
        "307": generate_years_peugeot_307,
        "308": generate_years_peugeot_308,
        "4007": generate_years_peugeot_4007,
        "406": generate_years_peugeot_406,
        "407": generate_years_peugeot_407,
        "408": generate_years_peugeot_408,
        "Boxer": generate_years_peugeot_Boxer,
        "Expert": generate_years_peugeot_Expert,
        "Partner": generate_years_peugeot_Partner,
        "Traveller": generate_years_peugeot_Traveller,

        "911": generate_years_porsche_911,
        "Cayenne": generate_years_porsche_Cayenne,
        "Cayman": generate_years_porsche_Cayman,
        "Macan": generate_years_porsche_Macan,
        "Panamera": generate_years_porsche_Panamera,

        "Arkana": generate_years_renault_Arkana,
        "Clio": generate_years_renault_Clio,
        "Dokker": generate_years_renault_Dokker,
        "Duster": generate_years_renault_Duster,
        "Fluence": generate_years_renault_Fluence,
        "Kangoo": generate_years_renault_Kangoo,
        "Kaptur": generate_years_renault_Kaptur,
        "Koleos": generate_years_renault_Koleos,
        "Laguna": generate_years_renault_Laguna,
        "Logan": generate_years_renault_Logan,
        "Master": generate_years_renault_Master,
        "Megane": generate_years_renault_Megane,
        "Sandero": generate_years_renault_Sandero,
        "Scenic": generate_years_renault_Scenic,
        "Symbol": generate_years_renault_Symbol,
        "Trafic": generate_years_renault_Trafic,

        "Fabia": generate_years_skoda_Fabia,
        "Felicia": generate_years_skoda_Felicia,
        "Kodiaq": generate_years_skoda_Kodiaq,
        "Octavia": generate_years_skoda_Octavia,
        "Rapid": generate_years_skoda_Rapid,
        "Roomster": generate_years_skoda_Roomster,
        "Karoq": generate_years_skoda_Karoq,
        "Superb": generate_years_skoda_Superb,
        "Yeti": generate_years_skoda_Yeti,

        "Actyon": generate_years_ssangyong_Actyon,
        "Actyon Sports": generate_years_ssangyong_Actyon_Sports,
        "Istana": generate_years_ssangyong_Istana,
        "Korando": generate_years_ssangyong_Korando,
        "Kyron": generate_years_ssangyong_Kyron,
        "Musso": generate_years_ssangyong_Musso,
        "Rexton": generate_years_ssangyong_Rexton,
        "Stavic": generate_years_ssangyong_Stavic,

        "Forester": generate_years_subaru_Forester,
        "Impreza": generate_years_subaru_Impreza,
        "Impreza WRX": generate_years_subaru_Impreza_WRX,
        "Legacy": generate_years_subaru_Legacy,
        "Outback": generate_years_subaru_Outback,
        "Tribeca": generate_years_subaru_Tribeca,
        "XV": generate_years_subaru_XV,

        "Aerio": generate_years_suzuki_Aerio,
        "Baleno": generate_years_suzuki_Baleno,
        "Cultus": generate_years_suzuki_Cultus,
        "Escudo": generate_years_suzuki_Escudo,
        "Grand Vitara": generate_years_suzuki_Grand_Vitara,
        "Ignis": generate_years_suzuki_Ignis,
        "Splash": generate_years_suzuki_Splash,
        "Swift": generate_years_suzuki_Swift,
        "SX4": generate_years_suzuki_SX4,
        "SX4 Sedan": generate_years_suzuki_SX4_Sedan,
        "Jimny": generate_years_suzuki_Jimny,
        "XL 7": generate_years_suzuki_XL_7,
        "Vitara": generate_years_suzuki_Vitara,
        "Wagon R": generate_years_suzuki_Wagon_R,
        "Liana": generate_years_suzuki_Liana,

        "4 Runner": generate_years_toyota_4_Runner,
        "Alphard": generate_years_toyota_Alphard,
        "Auris": generate_years_toyota_Auris,
        "Avensis": generate_years_toyota_Avensis,
        "Caldina": generate_years_toyota_Caldina,
        "Camry": generate_years_toyota_Camry,
        "Carina": generate_years_toyota_Carina,
        "Carina E": generate_years_toyota_Carina_E,
        "Celica": generate_years_toyota_Celica,
        "Chaser": generate_years_toyota_Chaser,
        "Corolla": generate_years_toyota_Corolla,
        "Crown": generate_years_toyota_Crown,
        "Estima": generate_years_toyota_Estima,
        "Harrier": generate_years_toyota_Harrier,
        "Highlander": generate_years_toyota_Highlander,
        "Hilux Pick Up": generate_years_toyota_Hilux_Pick_Up,
        "Land Cruiser": generate_years_toyota_Land_Cruiser,
        "Land Cruiser Prado": generate_years_toyota_Land_Cruiser_Prado,
        "Mark II": generate_years_toyota_Mark_II,
        "Matrix": generate_years_toyota_Matrix,
        "Prius": generate_years_toyota_Prius,
        "RAV4": generate_years_toyota_RAV4,
        "Tundra": generate_years_toyota_Tundra,
        "Venza": generate_years_toyota_Venza,
        "Verso": generate_years_toyota_Verso,
        "Yaris": generate_years_toyota_Yaris,

        "Amarok": generate_years_volkswagen_Amarok,
        "Bora": generate_years_volkswagen_Bora,
        "Caddy": generate_years_volkswagen_Caddy,
        "Caravelle": generate_years_volkswagen_Caravelle,
        "Crafter": generate_years_volkswagen_Crafter,
        "Golf": generate_years_volkswagen_Golf,
        "Golf Plus": generate_years_volkswagen_Golf_Plus,
        "Jetta": generate_years_volkswagen_Jetta,
        "Multivan": generate_years_volkswagen_Multivan,
        "Passat": generate_years_volkswagen_Passat,
        "Phaeton": generate_years_volkswagen_Phaeton,
        "Polo": generate_years_volkswagen_Polo,
        "Tiguan": generate_years_volkswagen_Tiguan,
        "Touareg": generate_years_volkswagen_Touareg,
        "Touran": generate_years_volkswagen_Touran,
        "Transporter": generate_years_volkswagen_Transporter,
        "Vento": generate_years_volkswagen_Vento,
        "Scirocco": generate_years_volkswagen_Scirocco,
        "Sharan": generate_years_volkswagen_Sharan,

        "850": generate_years_volvo_850,
        "960": generate_years_volvo_960,
        "C30": generate_years_volvo_C30,
        "S40": generate_years_volvo_S40,
        "S60": generate_years_volvo_S60,
        "S70": generate_years_volvo_S70,
        "S80": generate_years_volvo_S80,
        "V40": generate_years_volvo_V40,
        "V70": generate_years_volvo_V70,
        "XC60": generate_years_volvo_XC60,
        "XC70": generate_years_volvo_XC70,
        "XC90": generate_years_volvo_XC90,

    }
    car_models_other = {
        "other_audi": generate_other_models_audi,
        "other_bmw": generate_other_models_bmw,
        "other_cadillac": generate_other_models_cadillac,
        "other_chevrolet": generate_other_models_chevrolet,
        "other_chrysler": generate_other_models_chrysler,
        "other_citroen": generate_other_models_citroen,
        "other_daewoo": generate_other_models_daewoo,
        "other_dodge": generate_other_models_dodge,
        "other_fiat": generate_other_models_fiat,
        "other_ford": generate_other_models_ford,
        "other_honda": generate_other_models_honda,
        "other_hyundai": generate_other_models_hyundai,
        "other_infiniti": generate_other_models_infiniti,
        "other_jeep": generate_other_models_jeep,
        "other_kia": generate_other_models_kia,
        "other_land_rover": generate_other_models_land_rover,
        "other_lexus": generate_other_models_lexus,
        "other_mazda": generate_other_models_mazda,
        "other_mercedes": generate_other_models_mercedes,
        "other_mitsubishi": generate_other_models_mitsubishi,
        "other_nissan": generate_other_models_nissan,
        "other_opel": generate_other_models_opel,
        "other_peugeot": generate_other_models_peugeot,
        "other_porsche": generate_other_models_porsche,
        "other_renault": generate_other_models_renault,
        "other_skoda": generate_other_models_skoda,
        "other_ssangyong": generate_other_models_ssangyong,
        "other_subaru": generate_other_models_subaru,
        "other_suzuki": generate_other_models_suzuki,
        "other_toyota": generate_other_models_toyota,
        "other_volkswagen": generate_other_models_volkswagen,
        "other_volvo": generate_other_models_volvo
    }

    if language == 'ru':

        if model in car_models:
            if car_models[model] is not None:
                await bot.send_message(user_id, cfg.ru_aa)
                await bot.send_message(user_id, c, parse_mode='MarkdownV2')
                keyboard = car_models[model](model, brand)
                await bot.send_message(user_id, cfg.ru_ba)
                await bot.send_message(user_id, cfg.ru_ca, reply_markup=keyboard)

        else:
            model = model.replace(' ', '_')
            # Когда модель отсутствует в списке
            keyboard = car_models_other[model](model)  # Используем функцию generate_other_models_audi
            await bot.send_message(user_id, cfg.ru_ca, reply_markup=keyboard)
            # Обработка других моделей
            if model == 'other_toyota':
                keyboard = generate_other_models_toyotas(brand)
                await bot.send_message(user_id, '-', reply_markup=keyboard)
            if model == 'other_nissan':
                keyboard = generate_other_models_nissans(brand)
                await bot.send_message(user_id, '-', reply_markup=keyboard)

    elif language == 'am':
        if model in car_models:
            if car_models[model] is not None:
                await bot.send_message(user_id, cfg.am_aa)
                await bot.send_message(user_id, c, parse_mode='MarkdownV2')
                keyboard = car_models[model](model, brand)
                await bot.send_message(user_id, cfg.am_ba)
                await bot.send_message(user_id, cfg.am_ca, reply_markup=keyboard)
        else:
            model = model.replace(' ', '_')
            # Когда модель отсутствует в списке
            keyboard = car_models_other[model](model)  # Используем функцию generate_other_models_audi
            await bot.send_message(user_id, cfg.am_ca, reply_markup=keyboard)
            # Обработка других моделей
            if model == 'other_toyota':
                keyboard = generate_other_models_toyotas(brand)
                await bot.send_message(user_id, '-', reply_markup=keyboard)
            if model == 'other_nissan':
                keyboard = generate_other_models_nissans(brand)
                await bot.send_message(user_id, '-', reply_markup=keyboard)


def generate_years(model, brand, start_year, end_year):
    keyboard = InlineKeyboardMarkup(row_width=5)
    years = reversed(range(start_year, end_year + 1))
    buttons = [InlineKeyboardButton(text=str(year), callback_data=f"oyear-{year}-{model}-{brand}")
               for year in years]
    keyboard.add(*buttons)
    return keyboard


def generate_other_models(brand, models):
    keyboard = InlineKeyboardMarkup(row_width=4)
    year = 'Non'
    buttons = [InlineKeyboardButton(text=model, callback_data=f"oyear-{year}-{model}-{brand}") for model in models]
    keyboard.add(*buttons)
    return keyboard


def generate_other_models_audi(brand):
    return generate_other_models(brand, ['200', '90', 'A1', 'A2', 'Coupe', 'e-tron S', 'e-tron Sport',
                                         'Q2 e-tron', 'Q4 e-tron', 'Q5 e-tron', 'Q6', 'Q8', 'R8', 'RS Q3', 'RS4',
                                         'RS5', 'RS6', 'RS7', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8',
                                         'SQ5 Sportback', 'V8'])


def generate_other_models_bmw(brand):
    return generate_other_models(brand, ['2er', '3 GT', '4er', '6 GT', '8er', 'i3', 'i4', 'i8', 'iX', 'iX1',
                                         'M3', 'M4', 'M5', 'M6', 'X2', 'X4', 'X7', 'Z'])


def generate_other_models_cadillac(brand):
    return generate_other_models(brand, ['Catera', 'CT6', 'De Ville', 'DTS', 'Eldorado', 'ELR', 'Fleetwood',
                                         'Seville', 'XLR', 'XT4', 'XT6'])


def generate_other_models_chevrolet(brand):
    return generate_other_models(brand, ['Alero', 'Astro', 'Avalanche', 'Beretta', 'Caprice', 'Caprice Classic',
                                         'Cavalier',
                                         'Colorado', 'Corsica', 'Corvette', 'Equinox', 'HHR', 'Impala', 'Lumina',
                                         'Malibu', 'Metro', 'Monte Carlo', 'Optra' 'Prizm', 'Silverado', 'SSR',
                                         'Tacuma', 'Traverse', 'Uplander', 'Van', 'Venture', 'Vivant', 'Volt'])


def generate_other_models_chrysler(brand):
    return generate_other_models(brand, ['Cirrus', 'Crossfire', 'Intrepid', 'LHS', 'Neon', 'New Yorker', 'Saratoga',
                                         'Stratus', 'Vision'])


def generate_other_models_citroen(brand):
    return generate_other_models(brand, ['BX', 'C1', 'C4 Cactus', 'C5 Aircross', 'C6', 'C8', 'DS3', 'DS5', 'Evasion',
                                         'Nemo', 'Saxo', 'Spacetourer', 'Xantia', 'ZX'])


def generate_other_models_daewoo(brand):
    return generate_other_models(brand, ['Damas', 'Evanda', 'Lacetti', 'Lanos', 'Prince', 'Rezzo', 'Tacuma', 'Tico',
                                         'Lemans', 'Tosca', 'Magnus', 'Winstorm', 'Novus'])


def generate_other_models_dodge(brand):
    return generate_other_models(brand, ['Avenger', 'Challenger', 'Charger', 'Dakota', 'Dart', 'Durango', 'Magnum',
                                         'Ram VAN', 'Shadow', 'Spirit', 'Stealth', 'Viper'])


def generate_other_models_fiat(brand):
    return generate_other_models(brand, ['500', 'Barchetta', 'Cinquecento', 'Coupe', 'Fiorino', 'Freemont', 'Fullback',
                                         'idea', 'Multipla', 'Sedici', 'Seicento', "Siena", 'Uno'])


def generate_other_models_ford(brand):
    return generate_other_models(brand, ['Aerostar', 'Cargo', 'Contour', 'Cougar', 'Crown Victoria', 'Econoline',
                                         'Econovan', 'EcoSport', 'EDGE', 'Escort', 'Excursion', 'Expedition', 'F-150',
                                         'F-Series', 'Freestyle', 'Granada', 'Ka',
                                         'Mustang', 'Orion', 'Probe', 'Puma', 'Scorpio', 'Sierra', 'Taurus',
                                         'Thunderbird', 'Tourneo', 'Tourneo Custom', 'Windstar', ])


def generate_other_models_honda(brand):
    return generate_other_models(brand, ['Accord Aerodeck', 'Accord Coupe', 'Accord Inspire', 'Accord Tourer',
                                         'Accord Wagon', 'Acty Truck', 'Acty Van', 'Airwave', "Ascot", 'Ascot Innova',
                                         'Avancier', 'Beat', 'Capa', 'City', 'Civic Aerodeck', 'Civic Ferio',
                                         'Civic Shuttle', 'Civic Type R', 'Clarity', 'Concerto', 'CR-X', 'CR-X Delsol',
                                         'CR-Z', 'Crossroad',
                                         'CRX', 'Domani', 'E', 'Edix', 'Elysion', 'Fit Aria', 'Fit Hybrid',
                                         'Fit Shuttle', 'FR-V', 'Freed', 'Freed +', 'Freed Spike', 'Grace', 'Horizon',
                                         'Insight', 'Integra SJ', 'Jade', 'Jump', 'Lagreat', 'Life', 'Life Dunk', 'MDX',
                                         'Mobilio', 'Mobilio Spike', 'N-Box', 'N-BOX Slash', 'N-ONE', 'N-WGN', 'NSX',
                                         'Odyssey (USA)', 'Orthia', 'Partner', 'Passport', 'Quint', 'Rafaga',
                                         'Ridgeline', 'S-MX', 'S2000', 'S660', 'Saber', 'Shuttle', 'Street', "That's",
                                         'Today', 'Torneo', 'Vamos', 'Vamos Hobio', 'Vezel', 'Vigor', "Z", "Zest"
                                         ])


def generate_other_models_hyundai(brand):
    return generate_other_models(brand, ['Aero City', 'Aero Queen', 'Aero Town', 'Atos', 'Avante', 'Centennial',
                                         'Country', 'Coupe', 'Genesis', 'Genesis Coupe', 'Gold', 'Grace',
                                         'Grand Santa Fe',
                                         'H-100', 'H350', 'HD Heavy', 'HD Light', 'HD Medium', 'HD120', 'HD35', 'HD65',
                                         'HD72', 'HD78', 'i10', 'Ioniq', 'Ioniq 5', 'ix20', 'Kona Electric', 'Lavita',
                                         'Mega Truck', 'Palisade', 'Pony', 'Real', 'S Coupe', 'Santa Fe Classic',
                                         'Santamo', 'Staria', 'Tiburon', 'Veloster', 'Veracruz', 'Verna', 'XG'])


def generate_other_models_infiniti(brand):
    return generate_other_models(brand, ['I', 'J'])


def generate_other_models_jeep(brand):
    return generate_other_models(brand, ['Gladiator', 'Renegade'])


def generate_other_models_kia(brand):
    return generate_other_models(brand, ['Amanti', 'Avella', 'Besta', 'Cadenza', 'Clarus', 'Concord', 'Forte', 'Joice',
                                         'K8', 'K900', 'Morning', 'Niro', 'Opirus', 'Pregio', 'Pride', 'ProCeed',
                                         'Retona', 'Sedona', 'Sephia', 'Stinger', 'Telluride', 'Xceed'])


def generate_other_models_land_rover(brand):
    return generate_other_models(brand, ['Discovery Sport', 'Range Rover Velar'])


def generate_other_models_lexus(brand):
    return generate_other_models(brand, ['CT', 'HS', 'LC', 'LFA', 'NX', 'RC', 'SC', 'UX'])


def generate_other_models_mazda(brand):
    return generate_other_models(brand, ['121', '929', 'Atenza', 'Atenza Sport', 'Atenza Sport Wagon', 'Autozam AZ-1',
                                         'Autozam AZ-3', 'Autozam Clef', 'Axela', 'AZ-Offroad', 'AZ-Wagon', 'B-Series',
                                         'B2500', 'Biante', 'Bongo Brawny', 'Bongo Brawny Van', 'Bongo Friendee',
                                         'Bongo Van',
                                         'Carol', 'Cronos', 'CX 3', 'CX-30', 'CX-8', 'E-Series', 'Efini MPV',
                                         'Efini M5-6', 'Efini MS-8',
                                         'Efini MS-9', 'Efini RX-7', 'Eunos 100', 'Eunos 300', 'Eunos 500', 'Eunos 800',
                                         'Eunos Cargo',
                                         'Eunos Cosmo', 'Eunos Presso', 'Eunos Roadster', 'Flair', 'Flair Crossover',
                                         'Lantis', 'Laputa',
                                         'Luce', 'Millenia', 'MX-3', 'MX-30', 'MX-5', 'MX-6', 'Persona', 'Proceed',
                                         'Proceed Levante',
                                         'Protege', 'Revue', 'Roadster', 'RX-7', 'Scrum', 'Sentia', 'Splano', 'Titan',
                                         'Verisa', 'Xedos 6', 'Xedos 9'])


def generate_other_models_mercedes(brand):
    return generate_other_models(brand, ['190', 'Actros', "AMG GT", "Antos", 'Arocs', 'Atego', 'Axor', "CapaCity",
                                         'Citan', 'Citaro', 'Cito', 'Conecto', 'Econic I', 'EQC', 'EQV',
                                         'GLE class Coupe', 'Integro', 'Intouro', 'LK/LN2', 'MB 100', 'MK', 'NG',
                                         'O 100',
                                         'O 303', 'O 304', 'O 307', 'O 309', 'O 330', 'O 340', 'O 402', 'O 403',
                                         'O 404', 'O 405', 'O 407', 'O 408', 'OF Series', 'OH Series', 'SK',
                                         'SLC Class', 'SLR', 'SLS AMG', 'Sprinter Classic', 'T1', 'Tourino', 'Tourismo',
                                         'Touro', 'Travego', 'Unimog', 'Vaneo', 'Vario', 'X class', 'Zetros'])


def generate_other_models_mitsubishi(brand):
    return generate_other_models(brand, ['3000 GT', 'Airtrel', 'Aspire', 'Bravo', 'Challenger', 'Chariot',
                                         'Chariot Grandis', 'Colt Plus', 'Debonair', 'Delica', 'Delica Cargo',
                                         'Delica D:2', 'Delica D:3', 'Delica D:5', 'Delica Van', 'Diamante',
                                         'Diamante Wagon', 'Dignity', 'Dingo', 'Dion', 'Eclipse', 'Eclipse Cross',
                                         'eK-Active', 'eK-Classy', 'ek Custom', 'eK Space', 'eK-Sport', 'eK-Wagon',
                                         'Emeraude', 'Endeavor', 'Eterna', 'Eterna Sava', 'Expo LRV', 'FTO',
                                         'Fuso Canter', 'Fuso Fighter', 'Fuso Rosa', 'Galant Fortis',
                                         'Galant Fortis Sportback', 'GTO', 'i', 'i-MiEV', 'Jeep', 'L300', 'L400',
                                         'Lancer Gargo', 'Lancer Cedia', 'Lancer Evolution', 'Lancer Evolution Wagon',
                                         'Lancer Sportback', 'Legnum', 'Libero', 'Mighty Max', 'Minica', 'Minica Toppo',
                                         'Minicab', 'Mirage', 'Montero', 'Montero Sport', 'Nimbus', 'Outlander Sport',
                                         'Pajero IO', 'Pajero Junior', 'Pajero Mini', 'Pajero Pinin', 'Precis',
                                         'Proudia',
                                         'Raider', 'Savrin', 'Sigma', 'Space Gear', 'Space Runner', 'Space Star',
                                         'Space Wagon', 'Strada', 'Toppo', 'Toppo BJ', 'Toppo BJ Wide', 'Town Box',
                                         'Town Box Wide', 'Triton'])


def generate_other_models_nissan(brand):
    return generate_other_models(brand, ['100NX', '180SX', '240SX', '300ZX', '350Z', '370Z', 'AD', 'AD Expert',
                                         'AD-MAX Wagon', 'Almera Tino', 'Altima', 'Armada', 'Atlas', 'Atleon',
                                         'Avenir', 'Avenit Salut', 'Bassara', 'Bluebird', 'Bluebird Sylph', 'Cabstar',
                                         'Cabstar E', 'Caravan', 'Caravan Elgrand', ' Cedric', 'Cedric Wagon', 'Cefiro',
                                         'Cefiro Wagon', 'Cima', 'Clipper', 'Crew', 'Cube', 'Cube Cubic', 'Datsun',
                                         'DAYZ', 'DAYZ Roox', 'Dualis', 'e-NV200', 'Elgrand', 'Expert', 'Fairlady Z',
                                         'Figaro', 'Frontier', 'Fuga', 'Gloria', 'Gloria Cima', 'GT-R', 'Homy',
                                         'Homy Elgrand', 'Interstar', 'Kix', 'L-Serie', 'Lafesta', 'Largo', 'Latio',
                                         'Laurel', 'Leaf', 'Leopard', 'Liberty', 'Lucino', 'March', 'Mirca C+C',
                                         'Mistral', 'Moco', 'NP300', 'NV 200', 'NV 400', 'NV 100 Clipper',
                                         'NV350 Caravan', 'NX-Coupe', 'Otti', 'Pickup', 'Pino', 'Pixo', 'Prairie',
                                         'Prairie Joy', 'Presage', 'Presea', 'President', 'Primastar', 'Primera Camino',
                                         'Primera Camino Wagon', 'Primera Wagon', 'Pulsar', 'Qashqai+2', 'Quest',
                                         'Rasheen', 'Rnessa',
                                         'Rogue', 'Roox', 'Safari', 'Sentra',
                                         'Serena', 'Silvia', 'Skyline Crossover', 'Skyline GT-R', 'Stagea', 'Stanza',
                                         'Sunny California', 'Sylphy', 'Terrano II'])


def generate_other_models_nissans(brand):
    return generate_other_models(brand, ['Terrano Regulus', 'Tiida Latio', 'Tino', 'Titan', 'Trade', 'Urvan', 'Vanette',
                                         'Vanette Serena', 'Vanette Truck', 'Versa', 'Wingroad', 'Xterra'])


def generate_other_models_opel(brand):
    return generate_other_models(brand,
                                 ['Adam', 'Ampera', 'Astra Family', 'Calibra', 'Campo', 'Crossland', 'Grandland X',
                                  'GT',
                                  'Monterey', 'Signum', 'Speedster', 'Tigra', 'Vita', 'Zafira Life'])


def generate_other_models_peugeot(brand):
    return generate_other_models(brand, ['1007', '106', '108', '2008', '205', '207', '208', '301', '305', '306', '309',
                                         '4008', '405', '5008', '508', '605', '607', '806', '807', 'Bipper', 'J5',
                                         'Partner Tepee', 'RCZ'])


def generate_other_models_porsche(brand):
    return generate_other_models(brand, ['918', '924', '928', '944', '968', '996', 'Boxster', "Cayenne Coupe",
                                         'Taycan'])


def generate_other_models_renault(brand):
    return generate_other_models(brand, ['11', '19', '21', '25', '5', '9', 'Avantime', 'Clio Symbol', 'Dokker Stepway',
                                         'Espace', 'Kadjar', 'KWID', 'Latitude', 'Logan Stapway', 'Modus',
                                         'Rapid', 'Safrane', 'Talisman', 'Twingo', 'Sandero Stepway', ' Twizy',
                                         'Vel Satis', 'ZOE', 'Wind'])


def generate_other_models_skoda(brand):
    return generate_other_models(brand, ['Citigo', 'Favorit', 'Praktik', 'Scala'])


def generate_other_models_ssangyong(brand):
    return generate_other_models(brand, ['Chairman', 'Musso Sports', 'Nomad', 'Rodius', 'Tivoli', 'XLV'])


def generate_other_models_subaru(brand):
    return generate_other_models(brand, ['Alcyone', 'Alcyone SVX', 'Baja', 'BRZ', 'Chiffon', 'Dex', 'Dias Wagon',
                                         'Domingo', 'Exiga', 'Exiga Crossover 7', 'Impreza WRX STI', 'Impreza XV',
                                         'Justy', 'Legacy B4', 'Legacy Lancaster', 'Leone', 'Levorg', 'Libero', 'Lucra',
                                         'Pleo', 'Pleo Plus', 'R1', 'R2', 'Rex', 'Sambar', 'Sambar Truck', 'Stella',
                                         'Traviq', 'Trezia', 'VIvio'])


def generate_other_models_suzuki(brand):
    return generate_other_models(brand, ['Alto', 'Alto Lapin', 'Cappuccino', 'Cara', 'Carry Truck', 'Carry Van',
                                         'Cervo', 'Cervo Mode', 'Equator', 'Esteem', 'Every', 'Every Landy',
                                         'Every Plus', 'Forenza', 'Grand Vitara XL-7', 'Grand Escudo', 'Hustler',
                                         'Jimny Sierra', 'Jimmy Wide', 'Kei', 'Kizashi', 'Landy', 'Lapin', 'MR Wagon',
                                         'Palette', 'Reno', 'Samurai', 'Sidekick', 'Solio', 'Spacia', 'Twin', 'Verona',
                                         'Wagon R Plus', 'Wagon R Solio', 'Wagon R Wide', 'X-90', 'Xbee'])


def generate_other_models_toyota(brand):
    return generate_other_models(brand, ['Allex', 'Allion', 'Altezza', 'Aqua', 'Aristo', 'Avalon',
                                         'Avensis Verso', 'Aygo', 'bB', 'Belta', 'Balde', 'Brevis', 'C-HR', 'Cami',
                                         'Camry Gracia', 'Camry Prominent', 'Carib', 'Carina ED', 'Carina Wagon',
                                         'Cavalier',
                                         'Celsior', 'Century', 'Corolla Altis', 'Corolla Axio', 'Corolla Ceres',
                                         'Corolla Fielder', 'Corolla FX', 'Corolla II', 'Corolla Levin',
                                         'Corolla Rumion', 'Corolla Runx', 'Corolla Spacio', 'Corolla Verso',
                                         'Corolla Wagon',
                                         'Corona', 'Corona EXiV', 'Corona Premio', 'Corona SF', 'Corsa', 'Cresta',
                                         'Crown Estate', 'Crown Hybrid', ' Crown Majesta', ' Crown Wagon',
                                         'Curren', 'Cynos', 'Duet', 'Dyna', 'Echo', 'Esquire', 'Estima Emina',
                                         'Estima Hybrid', 'Estima Lucida', 'FJ Cruiser', 'Fortuner', 'Funcargo',
                                         'Gaia', 'GranAce', 'Grand Hiace', 'Granvia', 'GT86', 'Harrier Hybrid',
                                         'Hiace', 'Hiace Regius', 'Hilux Surf', 'Ipsum', 'iQ', 'Ist', 'Isis',
                                         'Kluger', 'Land Cruiser Cygnus', 'Lite Ace', 'Lite Ace Noah', 'Lite Ace Truck',
                                         'Lite Ace Van', 'Liteace', 'Mark II Wagon', 'Mark II Wagon Blit',
                                         'Mark II Wagon Qualis', 'Mark X', 'Mark X Zio', 'Master Ace Surf',
                                         'Mega Cruiser', 'Mirai', 'MR-S', 'MR2', 'Nadia', 'Noah', 'Opa', 'Origin',
                                         'Paseo', 'Passo', 'Passo Sette', 'Picnic', 'Pixis Epoch', 'Pixis Joy',
                                         'Pixis Mega', 'Pixis Space', 'Pixis Van', 'Platz'])


def generate_other_models_toyotas(brand):
    return generate_other_models(brand, ['Porte', 'Premio', 'Previa', 'Prius a', 'Prius c', 'Prius PHV', 'Prius Prime',
                                         'Prius v', 'Probox', 'Proges', 'Pronard', 'Ractis', 'Raize', 'Raum', 'Regius',
                                         'Regius Ace', 'Roomy', 'Rush', 'Sai', 'Scepter', 'Sequola', 'Sera', 'Sienna',
                                         'Sienta', 'Soarer', 'Solara', 'Spade', 'Sparky', 'Sprinter', 'Sprinter Marino',
                                         ' Sprinter Trueno', 'Sprinter Carib', 'Scarlet', 'Succeed', 'Supra', 'Surf',
                                         'Tacoma', 'Tank', 'Tercel', 'Touring Hiace', 'Town Ace', 'Town Ace Noah',
                                         'Town Ace Truck', 'Town Ace Van', 'Urban Cruiser', 'Vanguard', 'Vellfire',
                                         'Verossa', 'Vista', 'Vista Ardeo', 'Vitz', 'Voltz', 'Voxy',
                                         'WILL Cypha', 'WiLL VI', 'WILL VS', 'Windom', 'Wish', 'Yaris Verso'])


def generate_other_models_volkswagen(brand):
    return generate_other_models(brand, ['Arteon', 'Beetle', 'Caddy Maxi', 'California', 'Constellation', 'Corrado',
                                         'Eos', 'Fox', 'Gol', 'ID.3', 'ID.4', 'ID.6 Crozz', 'ID.6 X', 'Kaefer',
                                         'L 80', 'LT', 'Lupo', 'New Beetle', 'Parati', 'Passat CC', 'Pointer',
                                         'Rabbit', 'Routan', 'Saveiro', 'Taos', 'Taro', 'Teramont', 'Up', 'Volksbus',
                                         'Worker', 'XL1'])


def generate_other_models_volvo(brand):
    return generate_other_models(brand, ['242', '244', '360', '440', '460', '480', '740', '744', '760', '7700', '8500',
                                         '8700', '940', '945', '9700', '9900', 'A-Series', 'B 10', 'B12', 'B 6', 'B 7',
                                         'B 9', 'C70', 'F10', 'F12', 'F16', 'FE', 'FH', 'FL', 'FLC', 'FM', 'FMX',
                                         'FS 7', 'NH 12', 'S90', 'V50', 'V60', 'V90', 'VNL', 'XC40'])


def generate_years_audi_100(model, brand):
    return generate_years(model, brand, 1976, 1994)


def generate_years_audi_80(model, brand):
    return generate_years(model, brand, 1978, 1995)


def generate_years_audi_A3(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_audi_A4(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_audi_A5(model, brand):
    return generate_years(model, brand, 2007, 2022)


def generate_years_audi_A6(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_audi_A7(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_audi_A8(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_audi_Allroad(model, brand):
    return generate_years(model, brand, 2000, 2019)


def generate_years_audi_Q3(model, brand):
    return generate_years(model, brand, 2011, 2023)


def generate_years_audi_Q5(model, brand):
    return generate_years(model, brand, 2008, 2023)


def generate_years_audi_Q7(model, brand):
    return generate_years(model, brand, 2006, 2023)


def generate_years_audi_TT(model, brand):
    return generate_years(model, brand, 1998, 2023)


def generate_years_bmw_1er(model, brand):
    return generate_years(model, brand, 2004, 2020)


def generate_years_bmw_3er(model, brand):
    return generate_years(model, brand, 1975, 2023)


def generate_years_bmw_5GT(model, brand):
    return generate_years(model, brand, 2010, 2017)


def generate_years_bmw_5er(model, brand):
    return generate_years(model, brand, 1981, 2023)


def generate_years_bmw_6er(model, brand):
    return generate_years(model, brand, 1981, 2018)


def generate_years_bmw_7er(model, brand):
    return generate_years(model, brand, 1977, 2023)


def generate_years_bmw_X1(model, brand):
    return generate_years(model, brand, 2009, 2023)


def generate_years_bmw_X3(model, brand):
    return generate_years(model, brand, 2003, 2023)


def generate_years_bmw_X5(model, brand):
    return generate_years(model, brand, 1999, 2023)


def generate_years_bmw_X6(model, brand):
    return generate_years(model, brand, 2009, 2023)


def generate_years_cadillac_ATS(model, brand):
    return generate_years(model, brand, 2012, 2016)


def generate_years_cadillac_BLS(model, brand):
    return generate_years(model, brand, 2006, 2010)


def generate_years_cadillac_CTS(model, brand):
    return generate_years(model, brand, 2002, 2019)


def generate_years_cadillac_Escalade(model, brand):
    return generate_years(model, brand, 1998, 2023)


def generate_years_cadillac_SRX(model, brand):
    return generate_years(model, brand, 2004, 2017)


def generate_years_cadillac_STS(model, brand):
    return generate_years(model, brand, 2005, 2011)


def generate_years_cadillac_XT5(model, brand):
    return generate_years(model, brand, 2016, 2023)


def generate_years_chevrolet_Aveo(model, brand):
    return generate_years(model, brand, 2002, 2015)


def generate_years_chevrolet_Blazer(model, brand):
    return generate_years(model, brand, 1991, 2005)


def generate_years_chevrolet_Camaro(model, brand):
    return generate_years(model, brand, 1981, 2023)


def generate_years_chevrolet_Captiva(model, brand):
    return generate_years(model, brand, 2006, 2015)


def generate_years_chevrolet_Cobalt(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_chevrolet_Cruze(model, brand):
    return generate_years(model, brand, 2000, 2019)


def generate_years_chevrolet_Epica(model, brand):
    return generate_years(model, brand, 2006, 2013)


def generate_years_chevrolet_Evanda(model, brand):
    return generate_years(model, brand, 2004, 2006)


def generate_years_chevrolet_Express(model, brand):
    return generate_years(model, brand, 1995, 2022)


def generate_years_chevrolet_Lacetti(model, brand):
    return generate_years(model, brand, 2004, 2013)


def generate_years_chevrolet_Lanos(model, brand):
    return generate_years(model, brand, 1997, 2009)


def generate_years_chevrolet_Niva(model, brand):
    return generate_years(model, brand, 1998, 2020)


def generate_years_chevrolet_Orlando(model, brand):
    return generate_years(model, brand, 2009, 2018)


def generate_years_chevrolet_Rezzo(model, brand):
    return generate_years(model, brand, 2004, 2008)


def generate_years_chevrolet_Spark(model, brand):
    return generate_years(model, brand, 2000, 2023)


def generate_years_chevrolet_Suburban(model, brand):
    return generate_years(model, brand, 1973, 2023)


def generate_years_chevrolet_Tahoe(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_chevrolet_Tracker(model, brand):
    return generate_years(model, brand, 1989, 2015)


def generate_years_chevrolet_TrailBlazer(model, brand):
    return generate_years(model, brand, 2001, 2023)


def generate_years_chevrolet_Viva(model, brand):
    return generate_years(model, brand, 2003, 2008)


def generate_years_chrysler_300C(model, brand):
    return generate_years(model, brand, 2004, 2021)


def generate_years_chrysler_300M(model, brand):
    return generate_years(model, brand, 1998, 2004)


def generate_years_chrysler_Concorde(model, brand):
    return generate_years(model, brand, 1992, 2004)


def generate_years_chrysler_Grand_Voyager(model, brand):
    return generate_years(model, brand, 1995, 2015)


def generate_years_chrysler_Pacifica(model, brand):
    return generate_years(model, brand, 2003, 2020)


def generate_years_chrysler_PT_cruiser(model, brand):
    return generate_years(model, brand, 2000, 2010)


def generate_years_chrysler_Sebring(model, brand):
    return generate_years(model, brand, 1995, 2010)


def generate_years_chrysler_Town_Country(model, brand):
    return generate_years(model, brand, 1990, 2016)


def generate_years_chrysler_Voyager(model, brand):
    return generate_years(model, brand, 1991, 2015)


def generate_years_citroen_berlingo(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_citroen_c_crosser(model, brand):
    return generate_years(model, brand, 2007, 2012)


def generate_years_citroen_c_elysee(model, brand):
    return generate_years(model, brand, 2012, 2017)


def generate_years_citroen_c2(model, brand):
    return generate_years(model, brand, 2003, 2009)


def generate_years_citroen_c3(model, brand):
    return generate_years(model, brand, 2001, 2014)


def generate_years_citroen_c3_picasso(model, brand):
    return generate_years(model, brand, 2008, 2016)


def generate_years_citroen_c4(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_citroen_c4_aircross(model, brand):
    return generate_years(model, brand, 2012, 2016)


def generate_years_citroen_c4_picasso(model, brand):
    return generate_years(model, brand, 2006, 2018)


def generate_years_citroen_c5(model, brand):
    return generate_years(model, brand, 2001, 2017)


def generate_years_citroen_ds4(model, brand):
    return generate_years(model, brand, 2011, 2023)


def generate_years_citroen_jumper(model, brand):
    return generate_years(model, brand, 1981, 2023)


def generate_years_citroen_jumpy(model, brand):
    return generate_years(model, brand, 1995, 2023)


def generate_years_citroen_xsara(model, brand):
    return generate_years(model, brand, 1997, 2006)


def generate_years_citroen_xsara_picasso(model, brand):
    return generate_years(model, brand, 1999, 2009)


def generate_years_daewoo_espero(model, brand):
    return generate_years(model, brand, 1991, 2000)


def generate_years_daewoo_gentra(model, brand):
    return generate_years(model, brand, 2005, 2016)


def generate_years_daewoo_leganza(model, brand):
    return generate_years(model, brand, 1997, 2003)


def generate_years_daewoo_matiz(model, brand):
    return generate_years(model, brand, 1997, 2015)


def generate_years_daewoo_nexia(model, brand):
    return generate_years(model, brand, 1995, 2016)


def generate_years_daewoo_nubira(model, brand):
    return generate_years(model, brand, 1997, 2004)


def generate_years_dodge_caliber(model, brand):
    return generate_years(model, brand, 2006, 2012)


def generate_years_dodge_caravan(model, brand):
    return generate_years(model, brand, 1988, 2007)


def generate_years_dodge_grand_caravan(model, brand):
    return generate_years(model, brand, 1983, 2020)


def generate_years_dodge_intrepid(model, brand):
    return generate_years(model, brand, 1992, 2004)


def generate_years_dodge_journey(model, brand):
    return generate_years(model, brand, 2008, 2020)


def generate_years_dodge_neon(model, brand):
    return generate_years(model, brand, 1994, 2005)


def generate_years_dodge_nitro(model, brand):
    return generate_years(model, brand, 2006, 2011)


def generate_years_dodge_ram(model, brand):
    return generate_years(model, brand, 1988, 2023)


def generate_years_dodge_stratus(model, brand):
    return generate_years(model, brand, 1995, 2006)


def generate_years_fiat_Albea(model, brand):
    return generate_years(model, brand, 1996, 2012)


def generate_years_fiat_Brava(model, brand):
    return generate_years(model, brand, 1995, 2001)


def generate_years_fiat_Bravo(model, brand):
    return generate_years(model, brand, 1995, 2011)


def generate_years_fiat_Croma(model, brand):
    return generate_years(model, brand, 1985, 2010)


def generate_years_fiat_Doblo(model, brand):
    return generate_years(model, brand, 2001, 2023)


def generate_years_fiat_Ducato(model, brand):
    return generate_years(model, brand, 1981, 2023)


def generate_years_fiat_Linea(model, brand):
    return generate_years(model, brand, 2007, 2012)


def generate_years_fiat_Marea(model, brand):
    return generate_years(model, brand, 1996, 2002)


def generate_years_fiat_Palio(model, brand):
    return generate_years(model, brand, 1996, 2017)


def generate_years_fiat_Panda(model, brand):
    return generate_years(model, brand, 1980, 2012)


def generate_years_fiat_Punto(model, brand):
    return generate_years(model, brand, 1993, 2016)


def generate_years_fiat_Scudo(model, brand):
    return generate_years(model, brand, 1996, 2016)


def generate_years_fiat_Stilo(model, brand):
    return generate_years(model, brand, 2001, 2007)


def generate_years_fiat_Tempra(model, brand):
    return generate_years(model, brand, 1990, 1996)


def generate_years_fiat_Tipo(model, brand):
    return generate_years(model, brand, 1987, 1996)


def generate_years_fiat_Ulysse(model, brand):
    return generate_years(model, brand, 1994, 2010)


def generate_years_ford_C_Max(model, brand):
    return generate_years(model, brand, 2003, 2015)


def generate_years_ford_Escape(model, brand):
    return generate_years(model, brand, 2000, 2019)


def generate_years_ford_Explorer(model, brand):
    return generate_years(model, brand, 1990, 2019)


def generate_years_ford_Fiesta(model, brand):
    return generate_years(model, brand, 1976, 2019)


def generate_years_ford_Focus(model, brand):
    return generate_years(model, brand, 1998, 2019)


def generate_years_ford_Fusion(model, brand):
    return generate_years(model, brand, 2002, 2010)


def generate_years_ford_Galaxy(model, brand):
    return generate_years(model, brand, 1995, 2015)


def generate_years_ford_Kuga(model, brand):
    return generate_years(model, brand, 2008, 2019)


def generate_years_ford_Maverick(model, brand):
    return generate_years(model, brand, 1993, 2007)


def generate_years_ford_Mondeo(model, brand):
    return generate_years(model, brand, 1993, 2019)


def generate_years_ford_Ranger(model, brand):
    return generate_years(model, brand, 1982, 2015)


def generate_years_ford_S_Max(model, brand):
    return generate_years(model, brand, 2006, 2015)


def generate_years_ford_Tourneo_Connect(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_ford_Transit(model, brand):
    return generate_years(model, brand, 1978, 2023)


def generate_years_ford_Transit_Connect(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_honda_Accord(model, brand):
    return generate_years(model, brand, 1989, 2020)


def generate_years_honda_Civic(model, brand):
    return generate_years(model, brand, 1991, 2015)


def generate_years_honda_CR_V(model, brand):
    return generate_years(model, brand, 1995, 2023)


def generate_years_honda_Crosstour(model, brand):
    return generate_years(model, brand, 2009, 2016)


def generate_years_honda_Element(model, brand):
    return generate_years(model, brand, 2002, 2011)


def generate_years_honda_Fit(model, brand):
    return generate_years(model, brand, 2001, 2023)


def generate_years_honda_HR_V(model, brand):
    return generate_years(model, brand, 1998, 2023)


def generate_years_honda_Inspire(model, brand):
    return generate_years(model, brand, 1992, 2012)


def generate_years_honda_Integra(model, brand):
    return generate_years(model, brand, 1985, 2006)


def generate_years_honda_Jazz(model, brand):
    return generate_years(model, brand, 2002, 2020)


def generate_years_honda_Legend(model, brand):
    return generate_years(model, brand, 1990, 2021)


def generate_years_honda_Logo(model, brand):
    return generate_years(model, brand, 1996, 2002)


def generate_years_honda_Odyssey(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_honda_Pilot(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_honda_Stream(model, brand):
    return generate_years(model, brand, 2000, 2014)


def generate_years_honda_Prelude(model, brand):
    return generate_years(model, brand, 1983, 2001)


def generate_years_honda_Stepwgn(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_hyundai_Accent(model, brand):
    return generate_years(model, brand, 1994, 2017)


def generate_years_hyundai_Creta(model, brand):
    return generate_years(model, brand, 2016, 2023)


def generate_years_hyundai_Elantra(model, brand):
    return generate_years(model, brand, 1990, 2023)


def generate_years_hyundai_Equus(model, brand):
    return generate_years(model, brand, 1999, 2017)


def generate_years_hyundai_Galloper(model, brand):
    return generate_years(model, brand, 1991, 2003)


def generate_years_hyundai_Getz(model, brand):
    return generate_years(model, brand, 2002, 2011)


def generate_years_hyundai_Grand_Starex(model, brand):
    return generate_years(model, brand, 2007, 2021)


def generate_years_hyundai_Grandeur(model, brand):
    return generate_years(model, brand, 1986, 2015)


def generate_years_hyundai_H_1(model, brand):
    return generate_years(model, brand, 1997, 2023)


def generate_years_hyundai_i20(model, brand):
    return generate_years(model, brand, 2008, 2012)


def generate_years_hyundai_i30(model, brand):
    return generate_years(model, brand, 2007, 2023)


def generate_years_hyundai_i40(model, brand):
    return generate_years(model, brand, 2011, 2018)


def generate_years_hyundai_ix35(model, brand):
    return generate_years(model, brand, 2009, 2016)


def generate_years_hyundai_ix55(model, brand):
    return generate_years(model, brand, 2006, 2013)


def generate_years_hyundai_Lantra(model, brand):
    return generate_years(model, brand, 1990, 2000)


def generate_years_hyundai_Matrix(model, brand):
    return generate_years(model, brand, 2001, 2010)


def generate_years_hyundai_NF(model, brand):
    return generate_years(model, brand, 2005, 2012)


def generate_years_hyundai_Porter(model, brand):
    return generate_years(model, brand, 1996, 2018)


def generate_years_hyundai_Santa_Fe(model, brand):
    return generate_years(model, brand, 2000, 2023)


def generate_years_hyundai_Solaris(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_hyundai_Sonata(model, brand):
    return generate_years(model, brand, 1988, 2023)


def generate_years_hyundai_Starex(model, brand):
    return generate_years(model, brand, 1997, 2017)


def generate_years_hyundai_Terracan(model, brand):
    return generate_years(model, brand, 2001, 2007)


def generate_years_hyundai_Trajet(model, brand):
    return generate_years(model, brand, 1999, 2008)


def generate_years_hyundai_Tucson(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_infiniti_EX(model, brand):
    return generate_years(model, brand, 2007, 2013)


def generate_years_infiniti_FX(model, brand):
    return generate_years(model, brand, 2003, 2014)


def generate_years_infiniti_G(model, brand):
    return generate_years(model, brand, 1989, 2014)


def generate_years_infiniti_JX(model, brand):
    return generate_years(model, brand, 2012, 2014)


def generate_years_infiniti_M(model, brand):
    return generate_years(model, brand, 2002, 2014)


def generate_years_infiniti_Q(model, brand):
    return generate_years(model, brand, 1989, 2021)


def generate_years_infiniti_QX(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_jeep_Cherokee(model, brand):
    return generate_years(model, brand, 1983, 2020)


def generate_years_jeep_Commander(model, brand):
    return generate_years(model, brand, 2005, 2010)


def generate_years_jeep_Compass(model, brand):
    return generate_years(model, brand, 2006, 2023)


def generate_years_jeep_Grand_Cherokee(model, brand):
    return generate_years(model, brand, 1992, 2023)


def generate_years_jeep_Liberty(model, brand):
    return generate_years(model, brand, 2001, 2012)


def generate_years_jeep_Patriot(model, brand):
    return generate_years(model, brand, 2006, 2016)


def generate_years_jeep_Wrangler(model, brand):
    return generate_years(model, brand, 1986, 2023)


def generate_years_kia_Bongo(model, brand):
    return generate_years(model, brand, 1980, 2019)


def generate_years_kia_Carens(model, brand):
    return generate_years(model, brand, 2000, 2018)


def generate_years_kia_Carnival(model, brand):
    return generate_years(model, brand, 1998, 2023)


def generate_years_kia_Ceed(model, brand):
    return generate_years(model, brand, 2006, 2023)


def generate_years_kia_Cerato(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_kia_K5(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_kia_Magentis(model, brand):
    return generate_years(model, brand, 2000, 2010)


def generate_years_kia_Mohave(model, brand):
    return generate_years(model, brand, 2008, 2023)


def generate_years_kia_Optima(model, brand):
    return generate_years(model, brand, 2000, 2020)


def generate_years_kia_Picanto(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_kia_Quoris(model, brand):
    return generate_years(model, brand, 2012, 2019)


def generate_years_kia_Rio(model, brand):
    return generate_years(model, brand, 2000, 2023)


def generate_years_kia_Rio_X_line(model, brand):
    return generate_years(model, brand, 2017, 2023)


def generate_years_kia_Seltos(model, brand):
    return generate_years(model, brand, 2019, 2023)


def generate_years_kia_Shuma(model, brand):
    return generate_years(model, brand, 1996, 2004)


def generate_years_kia_Sorento(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_kia_Soul(model, brand):
    return generate_years(model, brand, 2008, 2023)


def generate_years_kia_Spectra(model, brand):
    return generate_years(model, brand, 2000, 2011)


def generate_years_kia_Sportage(model, brand):
    return generate_years(model, brand, 1993, 2023)


def generate_years_kia_Venga(model, brand):
    return generate_years(model, brand, 2009, 2017)


def generate_years_land_rover_Defender(model, brand):
    return generate_years(model, brand, 1990, 2023)


def generate_years_land_rover_Discovery(model, brand):
    return generate_years(model, brand, 1989, 2023)


def generate_years_land_rover_Freelander(model, brand):
    return generate_years(model, brand, 1998, 2014)


def generate_years_land_rover_Range_Rover(model, brand):
    return generate_years(model, brand, 1981, 2023)


def generate_years_land_rover_Range_Rover_Evoque(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_land_rover_Range_Rover_Sport(model, brand):
    return generate_years(model, brand, 2005, 2023)


def generate_years_lexus_ES(model, brand):
    return generate_years(model, brand, 1989, 2023)


def generate_years_lexus_GS(model, brand):
    return generate_years(model, brand, 1993, 2020)


def generate_years_lexus_GX(model, brand):
    return generate_years(model, brand, 2003, 2023)


def generate_years_lexus_IS(model, brand):
    return generate_years(model, brand, 1999, 2023)


def generate_years_lexus_LS(model, brand):
    return generate_years(model, brand, 1990, 2023)


def generate_years_lexus_LX(model, brand):
    return generate_years(model, brand, 1995, 2023)


def generate_years_lexus_RX(model, brand):
    return generate_years(model, brand, 1998, 2023)


def generate_years_mazda_2(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_mazda_3(model, brand):
    return generate_years(model, brand, 2003, 2023)


def generate_years_mazda_323(model, brand):
    return generate_years(model, brand, 1980, 2004)


def generate_years_mazda_5(model, brand):
    return generate_years(model, brand, 2004, 2015)


def generate_years_mazda_6(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_mazda_626(model, brand):
    return generate_years(model, brand, 1979, 2002)


def generate_years_mazda_Bongo(model, brand):
    return generate_years(model, brand, 1990, 2020)


def generate_years_mazda_BT_50(model, brand):
    return generate_years(model, brand, 2005, 2012)


def generate_years_mazda_Capella(model, brand):
    return generate_years(model, brand, 1988, 2002)


def generate_years_mazda_CX_5(model, brand):
    return generate_years(model, brand, 2011, 2023)


def generate_years_mazda_CX_7(model, brand):
    return generate_years(model, brand, 2006, 2012)


def generate_years_mazda_CX_9(model, brand):
    return generate_years(model, brand, 2007, 2023)


def generate_years_mazda_Demio(model, brand):
    return generate_years(model, brand, 1996, 2019)


def generate_years_mazda_Familia(model, brand):
    return generate_years(model, brand, 1989, 2018)


def generate_years_mazda_MPV(model, brand):
    return generate_years(model, brand, 1990, 2016)


def generate_years_mazda_Premacy(model, brand):
    return generate_years(model, brand, 1999, 2018)


def generate_years_mazda_RX_8(model, brand):
    return generate_years(model, brand, 2003, 2012)


def generate_years_mazda_Tribute(model, brand):
    return generate_years(model, brand, 2000, 2011)


def generate_years_mercedes_A_class(model, brand):
    return generate_years(model, brand, 1997, 2023)


def generate_years_mercedes_B_class(model, brand):
    return generate_years(model, brand, 2005, 2023)


def generate_years_mercedes_C_class(model, brand):
    return generate_years(model, brand, 1993, 2023)


def generate_years_mercedes_CL_class(model, brand):
    return generate_years(model, brand, 1992, 2014)


def generate_years_mercedes_CLA_class(model, brand):
    return generate_years(model, brand, 2013, 2023)


def generate_years_mercedes_CLC_class(model, brand):
    return generate_years(model, brand, 2001, 2012)


def generate_years_mercedes_CLK_class(model, brand):
    return generate_years(model, brand, 1997, 2010)


def generate_years_mercedes_CLS_class(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_mercedes_E_class(model, brand):
    return generate_years(model, brand, 1972, 2023)


def generate_years_mercedes_GLC_class(model, brand):
    return generate_years(model, brand, 2015, 2023)


def generate_years_mercedes_GLE_class(model, brand):
    return generate_years(model, brand, 2015, 2023)


def generate_years_mercedes_G_class(model, brand):
    return generate_years(model, brand, 1979, 2023)


def generate_years_mercedes_GLK_class(model, brand):
    return generate_years(model, brand, 2008, 2016)


def generate_years_mercedes_GL_class(model, brand):
    return generate_years(model, brand, 2006, 2016)


def generate_years_mercedes_V_class(model, brand):
    return generate_years(model, brand, 2014, 2023)


def generate_years_mercedes_M_class(model, brand):
    return generate_years(model, brand, 1997, 2015)


def generate_years_mercedes_GLB_class(model, brand):
    return generate_years(model, brand, 2020, 2023)


def generate_years_mercedes_GLA_class(model, brand):
    return generate_years(model, brand, 2013, 2023)


def generate_years_mercedes_R_class(model, brand):
    return generate_years(model, brand, 2004, 2013)


def generate_years_mercedes_Vito(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_mercedes_S_class(model, brand):
    return generate_years(model, brand, 1972, 2023)


def generate_years_mercedes_SLK_class(model, brand):
    return generate_years(model, brand, 1996, 2016)


def generate_years_mercedes_Sprinter(model, brand):
    return generate_years(model, brand, 1995, 2023)


def generate_years_mercedes_GLS_class(model, brand):
    return generate_years(model, brand, 2016, 2023)


def generate_years_mercedes_SL_class(model, brand):
    return generate_years(model, brand, 1989, 2019)


def generate_years_mitsubishi_ASX(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_mitsubishi_Carisma(model, brand):
    return generate_years(model, brand, 1995, 2006)


def generate_years_mitsubishi_Colt(model, brand):
    return generate_years(model, brand, 1978, 2011)


def generate_years_mitsubishi_Galant(model, brand):
    return generate_years(model, brand, 1980, 2012)


def generate_years_mitsubishi_Grandis(model, brand):
    return generate_years(model, brand, 1997, 2011)


def generate_years_mitsubishi_L200(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_mitsubishi_Lancer(model, brand):
    return generate_years(model, brand, 1979, 2016)


def generate_years_mitsubishi_Outlander(model, brand):
    return generate_years(model, brand, 2003, 2023)


def generate_years_mitsubishi_Outlander_XL(model, brand):
    return generate_years(model, brand, 2002, 2012)


def generate_years_mitsubishi_Pajero(model, brand):
    return generate_years(model, brand, 1982, 2020)


def generate_years_mitsubishi_Pajero_Sport(model, brand):
    return generate_years(model, brand, 1997, 2023)


def generate_years_mitsubishi_RVR(model, brand):
    return generate_years(model, brand, 1991, 2019)


def generate_years_nissan_Almera(model, brand):
    return generate_years(model, brand, 1995, 2019)


def generate_years_nissan_Almera_Classic(model, brand):
    return generate_years(model, brand, 1995, 2019)


def generate_years_nissan_Juke(model, brand):
    return generate_years(model, brand, 2010, 2020)


def generate_years_nissan_Maxima(model, brand):
    return generate_years(model, brand, 1988, 2015)


def generate_years_nissan_Maxima_QX(model, brand):
    return generate_years(model, brand, 1994, 2007)


def generate_years_nissan_Micra(model, brand):
    return generate_years(model, brand, 1982, 2017)


def generate_years_nissan_Murano(model, brand):
    return generate_years(model, brand, 2002, 2022)


def generate_years_nissan_Navara(model, brand):
    return generate_years(model, brand, 1997, 2021)


def generate_years_nissan_Note(model, brand):
    return generate_years(model, brand, 2005, 2020)


def generate_years_nissan_Pathfinder(model, brand):
    return generate_years(model, brand, 1986, 2023)


def generate_years_nissan_Patrol(model, brand):
    return generate_years(model, brand, 1980, 2023)


def generate_years_nissan_Primera(model, brand):
    return generate_years(model, brand, 1990, 2007)


def generate_years_nissan_Qashqai(model, brand):
    return generate_years(model, brand, 2006, 2023)


def generate_years_nissan_Skyline(model, brand):
    return generate_years(model, brand, 1985, 2023)


def generate_years_nissan_Sunny(model, brand):
    return generate_years(model, brand, 1986, 2004)


def generate_years_nissan_Teana(model, brand):
    return generate_years(model, brand, 2006, 2020)


def generate_years_nissan_Terrano(model, brand):
    return generate_years(model, brand, 1986, 2022)


def generate_years_nissan_Tiida(model, brand):
    return generate_years(model, brand, 2004, 2016)


def generate_years_nissan_X_Trail(model, brand):
    return generate_years(model, brand, 2000, 2022)


def generate_years_opel_Agila(model, brand):
    return generate_years(model, brand, 2000, 2014)


def generate_years_opel_Antara(model, brand):
    return generate_years(model, brand, 2006, 2017)


def generate_years_opel_Astra(model, brand):
    return generate_years(model, brand, 1991, 2022)


def generate_years_opel_Combo(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_opel_Corsa(model, brand):
    return generate_years(model, brand, 1982, 2014)


def generate_years_opel_Frontera(model, brand):
    return generate_years(model, brand, 1992, 2003)


def generate_years_opel_Insignia(model, brand):
    return generate_years(model, brand, 2008, 2017)


def generate_years_opel_Meriva(model, brand):
    return generate_years(model, brand, 2003, 2015)


def generate_years_opel_Mokka(model, brand):
    return generate_years(model, brand, 2012, 2015)


def generate_years_opel_Movano(model, brand):
    return generate_years(model, brand, 1998, 2023)


def generate_years_opel_Omega(model, brand):
    return generate_years(model, brand, 1986, 2003)


def generate_years_opel_Sintra(model, brand):
    return generate_years(model, brand, 1996, 1999)


def generate_years_opel_Vectra(model, brand):
    return generate_years(model, brand, 1988, 2008)


def generate_years_opel_Vivaro(model, brand):
    return generate_years(model, brand, 2001, 2023)


def generate_years_opel_Zafira(model, brand):
    return generate_years(model, brand, 1999, 2015)


def generate_years_peugeot_107(model, brand):
    return generate_years(model, brand, 2005, 2015)


def generate_years_peugeot_206(model, brand):
    return generate_years(model, brand, 1998, 2010)


def generate_years_peugeot_3008(model, brand):
    return generate_years(model, brand, 2009, 2023)


def generate_years_peugeot_307(model, brand):
    return generate_years(model, brand, 2000, 2008)


def generate_years_peugeot_308(model, brand):
    return generate_years(model, brand, 2007, 2018)


def generate_years_peugeot_4007(model, brand):
    return generate_years(model, brand, 2007, 2014)


def generate_years_peugeot_406(model, brand):
    return generate_years(model, brand, 1995, 2005)


def generate_years_peugeot_407(model, brand):
    return generate_years(model, brand, 2004, 2011)


def generate_years_peugeot_408(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_peugeot_Boxer(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_peugeot_Expert(model, brand):
    return generate_years(model, brand, 1995, 2023)


def generate_years_peugeot_Partner(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_peugeot_Traveller(model, brand):
    return generate_years(model, brand, 2017, 2023)


def generate_years_porsche_911(model, brand):
    return generate_years(model, brand, 1984, 2023)


def generate_years_porsche_Cayenne(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_porsche_Cayman(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_porsche_Macan(model, brand):
    return generate_years(model, brand, 2014, 2023)


def generate_years_porsche_Panamera(model, brand):
    return generate_years(model, brand, 2009, 2023)


def generate_years_renault_Panamera(model, brand):
    return generate_years(model, brand, 2009, 2023)


def generate_years_renault_Arkana(model, brand):
    return generate_years(model, brand, 2018, 2023)


def generate_years_renault_Clio(model, brand):
    return generate_years(model, brand, 1990, 2023)


def generate_years_renault_Dokker(model, brand):
    return generate_years(model, brand, 2012, 2020)


def generate_years_renault_Duster(model, brand):
    return generate_years(model, brand, 2010, 2023)


def generate_years_renault_Fluence(model, brand):
    return generate_years(model, brand, 2009, 2017)


def generate_years_renault_Kangoo(model, brand):
    return generate_years(model, brand, 1997, 2016)


def generate_years_renault_Kaptur(model, brand):
    return generate_years(model, brand, 2016, 2023)


def generate_years_renault_Koleos(model, brand):
    return generate_years(model, brand, 2008, 2020)


def generate_years_renault_Laguna(model, brand):
    return generate_years(model, brand, 1993, 2015)


def generate_years_renault_Logan(model, brand):
    return generate_years(model, brand, 2004, 2023)


def generate_years_renault_Master(model, brand):
    return generate_years(model, brand, 1980, 2019)


def generate_years_renault_Megane(model, brand):
    return generate_years(model, brand, 1995, 2016)


def generate_years_renault_Sandero(model, brand):
    return generate_years(model, brand, 2007, 2023)


def generate_years_renault_Scenic(model, brand):
    return generate_years(model, brand, 1996, 2016)


def generate_years_renault_Symbol(model, brand):
    return generate_years(model, brand, 2002, 2012)


def generate_years_renault_Trafic(model, brand):
    return generate_years(model, brand, 1980, 2019)


def generate_years_skoda_Kodiaq(model, brand):
    return generate_years(model, brand, 2016, 2023)


def generate_years_skoda_Fabia(model, brand):
    return generate_years(model, brand, 1999, 2015)


def generate_years_skoda_Felicia(model, brand):
    return generate_years(model, brand, 1994, 2002)


def generate_years_skoda_Octavia(model, brand):
    return generate_years(model, brand, 1996, 2023)


def generate_years_skoda_Rapid(model, brand):
    return generate_years(model, brand, 2012, 2023)


def generate_years_skoda_Roomster(model, brand):
    return generate_years(model, brand, 2006, 2015)


def generate_years_skoda_Karoq(model, brand):
    return generate_years(model, brand, 2017, 2023)


def generate_years_skoda_Superb(model, brand):
    return generate_years(model, brand, 2001, 2023)


def generate_years_skoda_Yeti(model, brand):
    return generate_years(model, brand, 2009, 2018)


def generate_years_ssangyong_Actyon(model, brand):
    return generate_years(model, brand, 2009, 2018)


def generate_years_ssangyong_Actyon_Sports(model, brand):
    return generate_years(model, brand, 2007, 2016)


def generate_years_ssangyong_Istana(model, brand):
    return generate_years(model, brand, 1992, 2004)


def generate_years_ssangyong_Korando(model, brand):
    return generate_years(model, brand, 1988, 2018)


def generate_years_ssangyong_Kyron(model, brand):
    return generate_years(model, brand, 2005, 2016)


def generate_years_ssangyong_Musso(model, brand):
    return generate_years(model, brand, 1995, 2011)


def generate_years_ssangyong_Rexton(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_ssangyong_Stavic(model, brand):
    return generate_years(model, brand, 2013, 2016)


def generate_years_subaru_Forester(model, brand):
    return generate_years(model, brand, 1997, 2023)


def generate_years_subaru_Impreza(model, brand):
    return generate_years(model, brand, 1992, 2023)


def generate_years_subaru_Impreza_WRX(model, brand):
    return generate_years(model, brand, 1992, 2021)


def generate_years_subaru_Legacy(model, brand):
    return generate_years(model, brand, 1989, 2021)


def generate_years_subaru_Outback(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_subaru_Tribeca(model, brand):
    return generate_years(model, brand, 2004, 2014)


def generate_years_subaru_XV(model, brand):
    return generate_years(model, brand, 2011, 2023)


def generate_years_suzuki_Aerio(model, brand):
    return generate_years(model, brand, 2001, 2007)


def generate_years_suzuki_Baleno(model, brand):
    return generate_years(model, brand, 1995, 2020)


def generate_years_suzuki_Cultus(model, brand):
    return generate_years(model, brand, 1988, 2002)


def generate_years_suzuki_Escudo(model, brand):
    return generate_years(model, brand, 1988, 2022)


def generate_years_suzuki_Grand_Vitara(model, brand):
    return generate_years(model, brand, 1998, 2016)


def generate_years_suzuki_Ignis(model, brand):
    return generate_years(model, brand, 2000, 2023)


def generate_years_suzuki_Splash(model, brand):
    return generate_years(model, brand, 2008, 2015)


def generate_years_suzuki_Swift(model, brand):
    return generate_years(model, brand, 1989, 2015)


def generate_years_suzuki_SX4(model, brand):
    return generate_years(model, brand, 2006, 2023)


def generate_years_suzuki_SX4_Sedan(model, brand):
    return generate_years(model, brand, 2007, 2014)


def generate_years_suzuki_Jimny(model, brand):
    return generate_years(model, brand, 1987, 2023)


def generate_years_suzuki_XL_7(model, brand):
    return generate_years(model, brand, 2002, 2009)


def generate_years_suzuki_Vitara(model, brand):
    return generate_years(model, brand, 1988, 2023)


def generate_years_suzuki_Wagon_R(model, brand):
    return generate_years(model, brand, 1993, 2023)


def generate_years_suzuki_Liana(model, brand):
    return generate_years(model, brand, 2001, 2007)


def generate_years_toyota_4_Runner(model, brand):
    return generate_years(model, brand, 1987, 2020)


def generate_years_toyota_Alphard(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_toyota_Auris(model, brand):
    return generate_years(model, brand, 2006, 2018)


def generate_years_toyota_Avensis(model, brand):
    return generate_years(model, brand, 1997, 2018)


def generate_years_toyota_Caldina(model, brand):
    return generate_years(model, brand, 1992, 2007)


def generate_years_toyota_Camry(model, brand):
    return generate_years(model, brand, 1983, 2023)


def generate_years_toyota_Carina(model, brand):
    return generate_years(model, brand, 1981, 2001)


def generate_years_toyota_Carina_E(model, brand):
    return generate_years(model, brand, 1992, 1998)


def generate_years_toyota_Celica(model, brand):
    return generate_years(model, brand, 1985, 2006)


def generate_years_toyota_Chaser(model, brand):
    return generate_years(model, brand, 1988, 2001)


def generate_years_toyota_Corolla(model, brand):
    return generate_years(model, brand, 1979, 2023)


def generate_years_toyota_Crown(model, brand):
    return generate_years(model, brand, 1987, 2023)


def generate_years_toyota_Estima(model, brand):
    return generate_years(model, brand, 1990, 2019)


def generate_years_toyota_Harrier(model, brand):
    return generate_years(model, brand, 1997, 2023)


def generate_years_toyota_Highlander(model, brand):
    return generate_years(model, brand, 2001, 2023)


def generate_years_toyota_Hilux_Pick_Up(model, brand):
    return generate_years(model, brand, 1983, 2023)


def generate_years_toyota_Land_Cruiser(model, brand):
    return generate_years(model, brand, 1974, 2023)


def generate_years_toyota_Land_Cruiser_Prado(model, brand):
    return generate_years(model, brand, 1987, 2023)


def generate_years_toyota_Mark_II(model, brand):
    return generate_years(model, brand, 1988, 2004)


def generate_years_toyota_Matrix(model, brand):
    return generate_years(model, brand, 2002, 2013)


def generate_years_toyota_Prius(model, brand):
    return generate_years(model, brand, 1997, 2019)


def generate_years_toyota_RAV4(model, brand):
    return generate_years(model, brand, 1994, 2023)


def generate_years_toyota_Tundra(model, brand):
    return generate_years(model, brand, 1999, 2022)


def generate_years_toyota_Venza(model, brand):
    return generate_years(model, brand, 2008, 2016)


def generate_years_toyota_Verso(model, brand):
    return generate_years(model, brand, 2009, 2016)


def generate_years_toyota_Yaris(model, brand):
    return generate_years(model, brand, 1999, 2020)


def generate_years_volkswagen_Amarok(model, brand):
    return generate_years(model, brand, 2010, 2020)


def generate_years_volkswagen_Bora(model, brand):
    return generate_years(model, brand, 1998, 2005)


def generate_years_volkswagen_Caddy(model, brand):
    return generate_years(model, brand, 1982, 2020)


def generate_years_volkswagen_Caravelle(model, brand):
    return generate_years(model, brand, 1990, 2022)


def generate_years_volkswagen_Crafter(model, brand):
    return generate_years(model, brand, 2006, 2023)


def generate_years_volkswagen_Golf(model, brand):
    return generate_years(model, brand, 1974, 2023)


def generate_years_volkswagen_Golf_Plus(model, brand):
    return generate_years(model, brand, 2004, 2014)


def generate_years_volkswagen_Polo(model, brand):
    return generate_years(model, brand, 1981, 2023)


def generate_years_volkswagen_Scirocco(model, brand):
    return generate_years(model, brand, 1980, 2017)


def generate_years_volkswagen_Jetta(model, brand):
    return generate_years(model, brand, 1978, 2023)


def generate_years_volkswagen_Sharan(model, brand):
    return generate_years(model, brand, 1995, 2022)


def generate_years_volkswagen_Tiguan(model, brand):
    return generate_years(model, brand, 2007, 2023)


def generate_years_volkswagen_Multivan(model, brand):
    return generate_years(model, brand, 1990, 2022)


def generate_years_volkswagen_Touran(model, brand):
    return generate_years(model, brand, 2003, 2015)


def generate_years_volkswagen_Passat(model, brand):
    return generate_years(model, brand, 1980, 2023)


def generate_years_volkswagen_Transporter(model, brand):
    return generate_years(model, brand, 1978, 2023)


def generate_years_volkswagen_Phaeton(model, brand):
    return generate_years(model, brand, 2002, 2016)


def generate_years_volkswagen_Touareg(model, brand):
    return generate_years(model, brand, 2002, 2023)


def generate_years_volkswagen_Vento(model, brand):
    return generate_years(model, brand, 1991, 1998)


def generate_years_volvo_850(model, brand):
    return generate_years(model, brand, 1991, 1997)


def generate_years_volvo_960(model, brand):
    return generate_years(model, brand, 1990, 1998)


def generate_years_volvo_C30(model, brand):
    return generate_years(model, brand, 2006, 2013)


def generate_years_volvo_S40(model, brand):
    return generate_years(model, brand, 1995, 2012)


def generate_years_volvo_S60(model, brand):
    return generate_years(model, brand, 2000, 2023)


def generate_years_volvo_S70(model, brand):
    return generate_years(model, brand, 1996, 2000)


def generate_years_volvo_S80(model, brand):
    return generate_years(model, brand, 1998, 2016)


def generate_years_volvo_V40(model, brand):
    return generate_years(model, brand, 1995, 2019)


def generate_years_volvo_V70(model, brand):
    return generate_years(model, brand, 1996, 2016)


def generate_years_volvo_XC60(model, brand):
    return generate_years(model, brand, 2008, 2023)


def generate_years_volvo_XC70(model, brand):
    return generate_years(model, brand, 1997, 2016)


def generate_years_volvo_XC90(model, brand):
    return generate_years(model, brand, 2002, 2023)


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


async def year_model(message: types.Message):
    user_id = message.from_user.id
    await Configuration.year.set()
    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        fd = cfg.ru_year
    elif language == 'am':
        fd = cfg.am_year
    await bot.send_message(user_id, fd)


# noinspection PyTypeChecker
async def state_year_model(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    year = message.text
    data = await state.get_data()
    brand = data.get('brand')
    model = data.get('model')
    await state.update_data(year=year)
    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        fd = cfg.ru_accept
    elif language == 'am':
        fd = cfg.am_accept
    await bot.send_message(user_id, f'{fd} - {year}, {model}, {brand}')
    await year_message_button(message, state)


async def model_year(message: types.Message):
    user_id = message.from_user.id
    await Configuration.model.set()
    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        fd = cfg.ru_auto_name
    elif language == 'am':
        fd = cfg.am_auto_name
    await bot.send_message(user_id, fd)


# noinspection PyTypeChecker
async def state_model_year(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    model = message.text
    data = await state.get_data()
    brand = data.get('brand')
    await state.update_data(model=model)
    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        fd = cfg.ru_accept
    elif language == 'am':
        fd = cfg.am_accept
    await bot.send_message(user_id, f'{fd} - {model}, {brand}')
    await year_model(message)


# @dp.callback_query_handler(lambda c: c.data.startswith('year:'))
# noinspection PyArgumentList,PyUnreachableCode
async def year_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    brand = callback_query.data.split('-')[3]
    model = callback_query.data.split('-')[2]
    year = callback_query.data.split('-')[1]

    if 'other' in brand:
        brand = brand[6::]
        brand = brand.title()
        if brand == 'Bmw':
            brand = 'BMW'

    await Configuration.brand.set()
    await state.update_data(brand=brand)

    print(model)

    if model == 'Non':
        print(123123)
        await Configuration.sta.set()
        await state.update_data(sta=1)
        return await model_year(callback_query)

    await Configuration.model.set()
    await state.update_data(model=model)

    if year == 'Non':
        print(22312)
        await Configuration.sta.set()
        await state.update_data(sta=2)
        return await year_model(callback_query)

    await Configuration.year.set()
    await state.update_data(year=year)

    await Configuration.c.set()

    c = brand + ', ' + model + ', ' + year
    print(c)
    x = str(brand) + ' ' + str(model) + ' ' + str(year)
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

    await bot.send_message(user_id, f'{frst}{x}{second}')
    await Configuration.engine_displacement.set()
    await bot.send_message(user_id, ed)


async def year_message_button(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    brand = data.get('brand')
    model = data.get('model')
    year = data.get('year')

    if 'other' in brand:
        brand = brand[6::]

    await Configuration.brand.set()
    await state.update_data(brand=brand)

    print(model)

    if model == 'Non':
        print(123123)

    await Configuration.model.set()
    await state.update_data(model=model)

    if year == 'Non':
        print(22312)
        return await year_model(message)

    await Configuration.year.set()
    await state.update_data(year=year)

    await Configuration.c.set()

    c = brand + ', ' + model + ', ' + year
    print(c)
    x = str(brand) + ' ' + str(model) + ' ' + str(year)
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

    await bot.send_message(user_id, f'{frst}{x}{second}')
    await Configuration.engine_displacement.set()
    await bot.send_message(user_id, ed)


async def process_engine_displacement(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    engine_displacement = message.text
    await state.update_data(engine_displacement=engine_displacement)
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        frst = cfg.ru_accept
        ep = cfg.ru_ep
    elif language == 'am':
        frst = cfg.am_accept
        ep = cfg.am_ep

    data = await state.get_data()
    c = data.get('c')
    await Configuration.c.set()
    c = c + ', ' + engine_displacement
    await bot.send_message(user_id, f'{frst} - {c}')
    await state.update_data(c=c)
    await Configuration.motor_power.set()
    await bot.send_message(user_id, ep)


async def process_motor_power(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    motor_power = message.text
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
    await bot.send_message(user_id, f'{frst} - {c}')
    await state.update_data(c=c)
    await Configuration.car_body.set()
    await bot.send_message(user_id, cb, reply_markup=keyboard)


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
    await bot.send_message(user_id, f'{frst} - {c}')
    await state.update_data(c=c)
    await Configuration.auto_transmission.set()
    await bot.send_message(user_id, at, reply_markup=keyboard)


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
    await bot.send_message(user_id, f'{frst} - {c}')
    await state.update_data(c=c)
    await Configuration.engine.set()
    await bot.send_message(user_id, et, reply_markup=keyboard)


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
    await bot.send_message(user_id, f'{frst} - {c}')
    await state.update_data(c=c)
    await Configuration.drive.set()
    await bot.send_message(user_id, d, reply_markup=keyboard)


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
    user_id = callback_query.from_user.id
    drive = callback_query.data
    await state.update_data(drive=drive)

    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        frst = cfg.ru_accept
        code = cfg.ru_code
        keyboard = ru_code_keyboard()
    elif language == 'am':
        frst = cfg.am_accept
        code = cfg.am_code
        keyboard = am_code_keyboard()

    data = await state.get_data()
    c = data.get('c')
    await Configuration.c.set()
    c = c + ', ' + drive
    await bot.send_message(user_id, f'{frst} - {c}')
    await state.update_data(c=c)
    await Configuration.code.set()
    await bot.send_message(user_id, code, reply_markup=keyboard)


def ru_code_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Указать", callback_data="Тру")
    button2 = InlineKeyboardButton(text="Не указывать", callback_data="Фолс")
    keyboard.add(button1, button2)
    return keyboard


def am_code_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Նշել", callback_data="Тру")
    button2 = InlineKeyboardButton(text="Մի նշեք", callback_data="Фолс")
    keyboard.add(button1, button2)
    return keyboard


async def code_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    date = callback_query.data

    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        frst = cfg.ru_accept
        codes = cfg.ru_codes
        keyboard = ru_body_code_keyboard()
    elif language == 'am':
        frst = cfg.am_accept
        codes = cfg.am_codes
        keyboard = am_body_code_keyboard()

    if date == 'Тру':
        await state.update_data(code=date)
        await Configuration.engine_code.set()
        await bot.send_message(user_id, codes)

    elif date == 'Фолс':
        await state.update_data(code=date)
        data = await state.get_data()
        c = data.get('c')
        await bot.send_message(user_id, f'{frst}- {c}')
        await Configuration.codes.set()
        await bot.send_message(user_id, codes, reply_markup=keyboard)


async def engine_code_h(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        codes = cfg.ru_codes
        keyboard = ru_body_code_keyboard()
    elif language == 'am':
        ec = cfg.am_ec
        codes = cfg.am_codes
        keyboard = am_body_code_keyboard()
    engine_code = message.text
    await state.update_data(engine_code=engine_code)
    await Configuration.codes.set()
    await bot.send_message(user_id, codes, reply_markup=keyboard)


def ru_body_code_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Указать", callback_data="T")
    button2 = InlineKeyboardButton(text="Не указывать", callback_data="F")
    keyboard.add(button1, button2)
    return keyboard


def am_body_code_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    button1 = InlineKeyboardButton(text="Նշել", callback_data="T")
    button2 = InlineKeyboardButton(text="Մի նշեք", callback_data="F")
    keyboard.add(button1, button2)
    return keyboard


async def body_code_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    date = callback_query.data
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        bc = cfg.ru_codes
        pt = cfg.ru_pt
    elif language == 'am':

        bc = cfg.am_codes
        pt = cfg.am_pt
    if date == 'T':
        await state.update_data(codes=date)
        await Configuration.body_code.set()
        await bot.send_message(user_id, bc)

    elif date == 'F':
        await state.update_data(codes=date)
        await Configuration.part.set()
        await bot.send_message(user_id, pt)


async def body_code_h(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    body_code = message.text
    language = BotDB.get_user_lang(user_id)

    if language == 'ru':
        col = cfg.ru_col
        ya = cfg.ru_ya
        bc = cfg.ru_bcc
        ec = cfg.ru_ecc
        pt = cfg.ru_pt
    elif language == 'am':
        col = cfg.am_col
        ya = cfg.am_ya
        bc = cfg.am_bcc
        ec = cfg.am_ecc
        pt = cfg.am_pt
    await state.update_data(body_code=body_code)
    await bot.send_message(user_id, col)
    data = await state.get_data()
    c = data.get('c')
    engine_code = data.get('engine_code')
    body_code = data.get('body_code')
    await bot.send_message(user_id, f'{ya} - {c}')
    if body_code is not None:
        await bot.send_message(user_id, f'{bc} {body_code}')

    if engine_code is not None:
        await bot.send_message(user_id, f'{ec} {engine_code}')

    await Configuration.part.set()
    await bot.send_message(user_id, pt)


async def close_car(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    part = message.text
    await state.update_data(part=part)
    data = await state.get_data()
    sta = data.get('sta')
    c = data.get('c')
    brand = data.get('brand')
    model = data.get('model')
    year = data.get('year')
    engine_displacement = data.get('engine_displacement')
    motor_power = data.get('motor_power')
    car_body = data.get('car_body')
    auto_transmission = data.get('auto_transmission')
    engine = data.get('engine')
    drive = data.get('drive')
    code = data.get('code')
    codes = data.get('codes')
    engine_code = data.get('engine_code')
    body_code = data.get('body_code')
    part = data.get('part')
    status = 'processed'

    user_status = BotDB.get_user_status(user_id)

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

    if code == 'Тру':

        if codes == "T":
            idd = bot_car.add_enquiry(brand, model, year, engine_displacement, motor_power, car_body, auto_transmission,
                                      engine,
                                      drive, engine_code, body_code, part, c, user_id, status)

        else:
            idd = bot_car.add_enquiry(brand, model, year, engine_displacement, motor_power, car_body, auto_transmission,
                                      engine,
                                      drive, engine_code, None, part, c, user_id, status)

    else:
        if codes == "T":
            idd = bot_car.add_enquiry(brand, model, year, engine_displacement, motor_power, car_body, auto_transmission,
                                      engine,
                                      drive, None, body_code, part, c, user_id, status)

        else:
            idd = bot_car.add_enquiry(brand, model, year, engine_displacement, motor_power, car_body, auto_transmission,
                                      engine,
                                      drive, None, None, part, c, user_id, status)


    if sta == 1:
        k = bot_car.select_car_other(brand)
        if k[0] != 2 and k[0] != 3:

            for i in k:
                i = i.replace(' ', '')
                c_user_id = BotDB.get_user_id_login(i)
                language = BotDB.get_user_lang(c_user_id)

                if language == 'ru':
                    txt = f'''
Запрос №{idd}\n
{c}\n
Объем двигателя - {engine_displacement}
Мощность двигателя - {motor_power}
Кузов - {car_body}
КПП - {auto_transmission}
Тип двигателя - {engine}
Привод авто - {drive}
Код двигателя - {engine_code}
Код кузова - {body_code}

Запчасть/деталь -  {part}
                            '''

                elif language == 'am':
                    txt = f'''
Հարցում  №{idd}\n
{c}\n
Շարժիչի ծավալը - {engine_displacement}
Շարժիչի հզորությունը - {motor_power}
Մարմին - {car_body}
PPC - {auto_transmission}
Շարժիչի տեսակը - {engine}
Ավտո drive - {drive}
Շարժիչի կոդ - {engine_code}
Մարմնի կոդ - {body_code}

Մաս -  {part}
                            '''
                if language == 'ru':
                    keyboard = ru_change_keyboard(idd)
                elif language == 'am':
                    keyboard = am_change_keyboard(idd)
                await bot.send_message(c_user_id, txt, reply_markup=keyboard)
                language = BotDB.get_user_lang(user_id)
                if language == 'ru':
                    await bot.send_message(user_id, f'Запрос №{idd} принят в обработку')
                    await bot.send_message(user_id, f'{c}, {engine_code}, {body_code}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')
                    print(f'Запрос номер {idd} отправлен {c}')
                elif language == 'am':
                    await bot.send_message(user_id, f'Հարցում №{idd} ընդունվել է մշակման')
                    await bot.send_message(user_id, f'{c}, {engine_code}, {body_code}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')
                    print(f'Запрос номер {idd} отправлен {c}')
        elif k[0] == 2:
            language = BotDB.get_user_lang(user_id)

            if language == 'ru':
                await bot.send_message(user_id, f'Автомобиль на разборах не найден')
            elif language == 'am':
                await bot.send_message(user_id, f'Մեքենան չի գտնվել')

        elif k[0] == 3:
            adm_id = k[1]
            mess = k[2]
            await bot.send_message(adm_id, mess)
            language = BotDB.get_user_lang(user_id)

            if language == 'ru':
                await bot.send_message(user_id, f'Автомобиль на разборах не найден, попробуйте найти запчасть в другом '
                                                f'поколении автомобиля {brand} {model}')

            elif language == 'am':
                await bot.send_message(user_id, f'Մեքենան չի գտնվել վերլուծության մեջ, Փորձեք գտնել մեկ այլ պահեստամաս'
                                                f'մեքենայի սերունդ {brand} {model}')

    elif sta == 2:
        k = bot_car.select_other_car(brand, model)
        if k[0] != 2 and k[0] != 3:

            for i in k:
                i = i.replace(' ', '')
                c_user_id = BotDB.get_user_id_login(i)
                language = BotDB.get_user_lang(c_user_id)

                if language == 'ru':
                    txt = f'''
Запрос №{idd}\n
{c}\n
Объем двигателя - {engine_displacement}
Мощность двигателя - {motor_power}
Кузов - {car_body}
КПП - {auto_transmission}
Тип двигателя - {engine}
Привод авто - {drive}
Код двигателя - {engine_code}
Код кузова - {body_code}

Запчасть/деталь -  {part}
                                        '''

                elif language == 'am':
                    txt = f'''
Հարցում  №{idd}\n
{c}\n
Շարժիչի ծավալը - {engine_displacement}
Շարժիչի հզորությունը - {motor_power}
Մարմին - {car_body}
PPC - {auto_transmission}
Շարժիչի տեսակը - {engine}
Ավտո drive - {drive}
Շարժիչի կոդ - {engine_code}
Մարմնի կոդ - {body_code}

Մաս -  {part}
                                        '''

                if language == 'ru':
                    keyboard = ru_change_keyboard(idd)
                elif language == 'am':
                    keyboard = am_change_keyboard(idd)
                await bot.send_message(c_user_id, txt, reply_markup=keyboard)
                language = BotDB.get_user_lang(user_id)
                if language == 'ru':
                    await bot.send_message(user_id, f'Запрос №{idd} принят в обработку')
                    await bot.send_message(user_id, f'{c}, {engine_code}, {body_code}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')
                    print(f'Запрос номер {idd} отправлен {c}')
                elif language == 'am':
                    await bot.send_message(user_id, f'Հարցում №{idd} ընդունվել է մշակման')
                    await bot.send_message(user_id, f'{c}, {engine_code}, {body_code}')
                    await bot.send_message(user_id, part)
                    await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')
                    print(f'Запрос номер {idd} отправлен {c}')
        elif k[0] == 2:
            language = BotDB.get_user_lang(user_id)

            if language == 'ru':
                await bot.send_message(user_id, f'Автомобиль на разборах не найден')
            elif language == 'am':
                await bot.send_message(user_id, f'Մեքենան չի գտնվել')

        elif k[0] == 3:
            adm_id = k[1]
            mess = k[2]
            await bot.send_message(adm_id, mess)
            language = BotDB.get_user_lang(user_id)

            if language == 'ru':
                await bot.send_message(user_id, f'Автомобиль на разборах не найден, попробуйте найти запчасть в другом '
                                                f'поколении автомобиля {brand} {model}')

            elif language == 'am':
                await bot.send_message(user_id, f'Մեքենան չի գտնվել վերլուծության մեջ, Փորձեք գտնել մեկ այլ պահեստամաս'
                                                f'մեքենայի սերունդ {brand} {model}')

    else:
        years_list = bot_car.get_car_years(brand, model)
        print(years_list)
        years_lst = list()

        for i in years_list:

            first = i[:4:]
            second = i[5::]

            for j in range(int(first), int(second) + 1):

                if j == int(year):
                    years_lst.append(i)

        for r in years_lst:
            k = bot_car.select_car(brand, model, r)
            print(f'k = {k}')

            if k[0] != 2 and k[0] != 3:

                for i in k:
                    i = i.replace(' ', '')
                    c_user_id = BotDB.get_user_id_login(i)
                    language = BotDB.get_user_lang(c_user_id)

                    if language == 'ru':
                        txt = f'''
Запрос №{idd}\n
{c}\n
Объем двигателя - {engine_displacement}
Мощность двигателя - {motor_power}
Кузов - {car_body}
КПП - {auto_transmission}
Тип двигателя - {engine}
Привод авто - {drive}
Код двигателя - {engine_code}
Код кузова - {body_code}

Запчасть/деталь -  {part}
                                                      '''

                    elif language == 'am':
                        txt = f'''
Հարցում  №{idd}\n
{c}\n
Շարժիչի ծավալը - {engine_displacement}
Շարժիչի հզորությունը - {motor_power}
Մարմին - {car_body}
PPC - {auto_transmission}
Շարժիչի տեսակը - {engine}
Ավտո drive - {drive}
Շարժիչի կոդ - {engine_code}
Մարմնի կոդ - {body_code}

Մաս -  {part}
                                                      '''
                    if language == 'ru':
                        keyboard = ru_change_keyboard(idd)
                    elif language == 'am':
                        keyboard = am_change_keyboard(idd)
                    await bot.send_message(c_user_id, txt, reply_markup=keyboard)
                    language = BotDB.get_user_lang(user_id)
                    if language == 'ru':
                        await bot.send_message(user_id, f'Запрос №{idd} принят в обработку')
                        await bot.send_message(user_id, f'{c}, {engine_code}, {body_code}')
                        await bot.send_message(user_id, part)
                        await bot.send_message(user_id, f'Хотите отправить еще запрос? Нажмите кнопку "Меню"')
                        print(f'Запрос номер {idd} отправлен {c}')
                    elif language == 'am':
                        await bot.send_message(user_id, f'Հարցում №{idd} ընդունվել է մշակման')
                        await bot.send_message(user_id, f'{c}, {engine_code}, {body_code}')
                        await bot.send_message(user_id, part)
                        await bot.send_message(user_id, f'Ցանկանում եք ուղարկել ևս մեկ հարցում: Սեղմեք կոճակը "Меню"')
                        print(f'Запрос номер {idd} отправлен {c}')
            elif k[0] == 2:
                language = BotDB.get_user_lang(user_id)
                if language == 'ru':
                    await bot.send_message(user_id, f'Автомобиль на разборах не найден')
                elif language == 'am':
                    await bot.send_message(user_id, f'Մեքենան չի գտնվել')

            elif k[0] == 3:
                adm_id = k[1]
                mess = k[2]
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

    await state.finish()


class Change(StatesGroup):
    idd = State()
    types = State()
    summ = State()
    login = State()


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
    srs = callback_query.data.split('_')[0]
    idd = callback_query.data.split('_')[1]
    if srs == 'NON' or srs == 'NOT':
        return print('non', idd)

    user_id = callback_query.from_user.id
    login = BotDB.get_user_login(user_id)
    await Change.login.set()
    await state.update_data(login=login[0])
    await Change.idd.set()
    await state.update_data(idd=idd)
    await Change.types.set()
    await state.update_data(types=srs)
    await Change.summ.set()
    language = BotDB.get_user_lang(user_id)
    if language == 'ru':
        await bot.send_message(user_id, 'Введите цену за деталь')
    elif language == 'am':
        await bot.send_message(user_id, 'Մուտքագրեք գինը յուրաքանչյուր մասի համար')


# noinspection PyArgumentList
async def change_finish(message: types.Message, state: FSMContext):
    global photo_1, photo_2, photo_3, y
    summ = message.text
    data = await state.get_data()
    idd = data.get('idd')
    srs = data.get('types')
    login = data.get('login')
    user_id = bot_car.get_user_id_by_id(idd)
    c = bot_car.get_c_by_id(idd)
    part = bot_car.get_part_by_id(idd)
    result = bot_db.user(login)  # Pass the login value as login[0]
    language = BotDB.get_user_lang(user_id)

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
    ui = message.from_user.id
    lang = BotDB.get_user_lang(ui)
    if lang == 'ru':
        await bot.send_message(ui, f'Предложение отправлено, номер - {idd}')
    if lang == 'am':
        await bot.send_message(ui, f'Առաջարկը ուղարկված է, թիվ - {idd}')

    await state.finish()


def register_handlers_order(dp: Dispatcher):
    dp.register_message_handler(order_switch, commands=['order'])
    dp.register_callback_query_handler(order_switch_callback, lambda c: c.data.startswith(('om-', 'omsk')))
    dp.register_message_handler(order, commands=['orderswitch', 'quick'])
    dp.register_callback_query_handler(models_callback_button, lambda c: c.data.startswith('ocondition-'))
    dp.register_callback_query_handler(year_callback_button, lambda c: c.data.startswith('oyear-'))
    dp.register_callback_query_handler(years_callback_button, lambda c: c.data.startswith('omodel-'))
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

    dp.register_callback_query_handler(code_callback, lambda c: c.data.startswith(('Тру', 'Фолс')),
                                       state=Configuration.code)
    dp.register_message_handler(engine_code_h, state=Configuration.engine_code)

    dp.register_callback_query_handler(body_code_callback, lambda c: c.data.startswith(('T', 'F')),
                                       state=Configuration.codes)
    dp.register_message_handler(body_code_h, state=Configuration.body_code)
    dp.register_message_handler(close_car, state=Configuration.part)
    dp.register_message_handler(state_year_model, state=Configuration.year)
    dp.register_message_handler(state_model_year, state=Configuration.model)
    dp.register_callback_query_handler(change_callback, lambda c: c.data.startswith(('neworig_', 'baorig_', 'newcopy_',
                                                                                     'bacopy_', 'NON_', 'NOT_')))
    dp.register_message_handler(change_finish, state=Change.summ)
