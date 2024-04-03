import sqlite3
from unittest import result


class BotDB:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_user_status(self, user_id):
        """Достаем acccaunt_status юзера в базе по его user_id"""
        self.cursor.execute("SELECT `acccount_status` FROM `users` WHERE `user_id` = ?", (user_id,))
        row = self.cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            # Handle the case when the user_id is not found in the database
            return None

    def update_user_status(self, accaunt_status, login, user_id):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE users SET acccount_status=? WHERE user_id=?', (accaunt_status, user_id))
        self.cursor.execute('UPDATE users SET login=? WHERE user_id=?', (login, user_id))
        self.conn.commit()

    def get_user_lang(self, user_id):
        """Достаем lang юзера в базе по его user_id"""
        self.cursor.execute("SELECT `language` FROM `users` WHERE `user_id` = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_user_phone(self, user_id):
        """Достаем lang юзера в базе по его user_id"""
        self.cursor.execute("SELECT `phone` FROM `users` WHERE `user_id` = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def update_user_lang(self, language, user_id):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE users SET language=? WHERE user_id=?', (language, user_id))
        self.conn.commit()

    def insert_user_lang(self, user_id, language):
        """Добавляем lang юзера в базу или обновляем язык, если пользователь уже существует"""
        if self.user_exists(user_id):
            self.update_user_lang(language, user_id)
        else:
            self.cursor.execute('INSERT INTO users (`user_id`, `language`) VALUES (?, ?)', (user_id, language))
            self.conn.commit()

    def load_phone(self, user_id, num):
        """Добавляем lang юзера в базу или обновляем язык, если пользователь уже существует"""
        self.cursor.execute('UPDATE users SET `phone` = ? WHERE `user_id` = ?', (num, user_id))
        self.conn.commit()

    def get_phones(self, user_id):
        self.cursor.execute("SELECT `phone` FROM `users` WHERE `user_id` = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        self.conn.commit()

    def get_user_login(self, user_id):
        """Достаем login юзера в базе по его user_id"""
        self.cursor.execute("SELECT `login` FROM `users` WHERE `user_id` = ?", (user_id,))
        result = self.cursor.fetchone()
        return result

    def get_user_id_login(self, login):

        # Выполнение запроса для получения user_id по логину
        self.cursor.execute("SELECT user_id FROM users WHERE login=?", (login,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()


class bot_db:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.cursor = self.conn.cursor()

    def check_account(self, login, password):
        """Проверяем, есть ли юзер в базе"""
        self.cursor.execute("SELECT * FROM accounts WHERE login = ? AND password = ?", (login, password))
        account = self.cursor.fetchone()
        return account

    def check_login(self, login):
        # Проверка, существует ли уже пользователь с таким логином
        self.cursor.execute("SELECT * FROM accounts WHERE login = ?", (login,))
        existing_account = self.cursor.fetchone()
        return existing_account

    def new_user(self, login, password, user_type, user_id, user_name, auto_name, address, num_1, num_2, description,
                 date):
        self.cursor.execute(
            "INSERT INTO accounts(login, password, user_type, user_id, user_name, auto_name, address, num_1, num_2, description, date)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (login, password, user_type, user_id, user_name, auto_name, address, num_1, num_2, description, date))
        self.conn.commit()

    def user(self, login):
        query = "SELECT * FROM accounts WHERE login = ?"
        self.cursor.execute(query, (login,))
        result = self.cursor.fetchall()
        return result

    def get_id_login(self, login):
        """Достаем id юзера в базе по его login"""
        self.cursor.execute("SELECT `id` FROM `accounts` WHERE `login` = ?", (login,))
        result = self.cursor.fetchone()
        return result

    def get_num_login(self, login):
        """Достаем id юзера в базе по его login"""
        self.cursor.execute("SELECT `num_1` FROM `accounts` WHERE `login` = ?", (login,))
        result = self.cursor.fetchone()
        return result

    def get_enquiries_login(self, login):
        """Достаем id юзера в базе по его login"""
        self.cursor.execute("SELECT `enquiries` FROM `accounts` WHERE `login` = ?", (login,))
        result = self.cursor.fetchone()
        return result

    def update_login(self, login, id):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET login=? WHERE id=?', (login, id))
        self.conn.commit()

    def update_enquiries(self, enquiries, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET enquiries=? WHERE login=?', (enquiries, login))
        self.conn.commit()

    def update_password(self, password, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET password=? WHERE login=?', (password, login))
        self.conn.commit()

    def update_num_2(self, num_2, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET num_2=? WHERE login=?', (num_2, login))
        self.conn.commit()

    def update_num_1(self, num_1, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET num_1=? WHERE login=?', (num_1, login))
        self.conn.commit()

    def update_description(self, description, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET description=? WHERE login=?', (description, login))
        self.conn.commit()

    def update_name(self, auto_name, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET auto_name=? WHERE login=?', (auto_name, login))
        self.conn.commit()

    def update_site(self, site, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute('UPDATE accounts SET site=? WHERE login=?', (site, login))
        self.conn.commit()

    def update_photo_1(self, file_id, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute("UPDATE accounts SET photo_1=? WHERE login=?", (file_id, login))
        self.conn.commit()

    def update_photo_2(self, file_id, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute("UPDATE accounts SET photo_2=? WHERE login=?", (file_id, login))
        self.conn.commit()

    def update_photo_3(self, file_id, login):
        """Обновляем lang юзера в базе по его user_id"""
        self.cursor.execute("UPDATE accounts SET photo_3=? WHERE login=?", (file_id, login))
        self.conn.commit()

    def get_all_user_ids(self):
        # Выполняем SQL-запрос для выборки всех user_id из таблицы accounts
        self.cursor.execute("SELECT user_id FROM accounts")

        # Извлекаем все строки результата и сохраняем их в переменной user_ids
        user_ids = [row[0] for row in self.cursor.fetchall()]
        return user_ids

    def get_users_id(self):
        self.cursor.execute("SELECT user_id FROM users WHERE acccount_status = 0")

        user_ids = [row[0] for row in self.cursor.fetchall()]
        return user_ids

    def get_auto_rb(self):
        self.cursor.execute("SELECT user_id FROM users WHERE acccount_status = 1")
        results = self.cursor.fetchall()
        # Извлекаем user_id из результатов
        user_ids = [result[0] for result in results]
        return user_ids

    def get_len_users(self):
        # Выполняем SQL-запрос для подсчета количества уникальных user_id
        self.cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
        count = self.cursor.fetchone()[0]
        return count

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()


class bot_car:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.cursor = self.conn.cursor()

    def get_idd_by_status(self, status):
        self.cursor.execute("SELECT id FROM enquiries WHERE status = ?", (status,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def get_data_by_idd(self, idd):
        self.cursor.execute("SELECT * FROM enquiries WHERE id = ?", (idd,))
        result = self.cursor.fetchone()
        return result

    def add_enquiry(self, brand, model, year, engine_displacement, motor_power, car_body, auto_transmission, engine,
                    drive,
                    engine_code, body_code, part, c, user_id, status):
        self.cursor.execute(
            "INSERT INTO enquiries(brand, model, year, engine_displacement, motor_power, car_body, auto_transmission, "
            "engine, drive, engine_code, body_code, part, c, user_id, status)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (brand, model, year, engine_displacement, motor_power, car_body, auto_transmission, engine, drive,
             engine_code, body_code, part, c, user_id, status))
        # Получаем id последней вставленной строки
        last_inserted_id = self.cursor.lastrowid

        self.conn.commit()

        # Возвращаем id последней вставленной строки
        return last_inserted_id

    def select_car(self, brand, model, years):
        # Находим записи с совпадением brand и model в столбцах brand и model
        self.cursor.execute("SELECT * FROM cars WHERE brand = ? AND model = ?", (brand, model))
        rows = self.cursor.fetchall()

        # Ищем точное совпадение между year и years
        logins_list = []
        for row in rows:
            if row[3] == years:  # row[3] соответствует столбцу years в таблице cars
                # Получаем список логинов, если логины есть
                logins = row[4] if row[4] else None  # row[4] соответствует столбцу logins
                if logins:
                    logins_list.extend(logins.split(','))
        # Если список логинов не пуст, вернуть его
        if logins_list:
            return logins_list
        elif len(rows) == 0:
            # Если нет совпадений по brand и model, отправить сообщение пользователю и вернуть 3

            return 3
        else:
            # Если нет логинов, вернуть 2
            return 2

    def add_car_login(self, brand, model, years, login):
        # Поиск совпадений для указанного бренда и модели
        self.cursor.execute("SELECT logins FROM cars WHERE brand=? AND model=? AND years=?", (brand, model, years))
        result = self.cursor.fetchone()

        if result is None:
            # Если не найдено совпадений, добавляем новую запись
            self.cursor.execute("INSERT INTO cars (brand, model, years, logins) VALUES (?, ?, ?, ?)",
                                (brand, model, years, login))
        else:
            # Если найдено совпадение, проверяем, что логин не существует в списке logins
            logins_list = result[0].split(', ') if result[0] else []
            if login not in logins_list:
                logins_list.append(login)
                updated_logins = ', '.join(logins_list)
                self.cursor.execute("UPDATE cars SET logins=? WHERE brand=? AND model=? AND years=?",
                                    (updated_logins, brand, model, years))
        self.conn.commit()

    def add_login(self, id, logins_list):

        updated_logins = ', '.join(logins_list)
        self.cursor.execute("UPDATE cars SET logins=? WHERE id=?",
                            (updated_logins, id))
        self.conn.commit()

    def get_car_years(self, brand, model):
        """Получаем все строки years, где есть точное совпадение между brand и model"""
        self.cursor.execute("SELECT years FROM cars WHERE brand = ? AND model = ?", (brand, model))
        result = self.cursor.fetchall()
        years_list = [row[0] for row in result] if result else []
        return years_list

    def get_user_id_by_id(self, enquiry_id):
        """Находим строку по id и возвращаем значение столбца user_id"""
        self.cursor.execute("SELECT user_id FROM enquiries WHERE id = ?", (enquiry_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_c_by_id(self, enquiry_id):
        """Находим строку по id и возвращаем значение столбца user_id"""
        self.cursor.execute("SELECT c FROM enquiries WHERE id = ?", (enquiry_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_part_by_id(self, enquiry_id):
        """Находим строку по id и возвращаем значение столбца user_id"""
        self.cursor.execute("SELECT part FROM enquiries WHERE id = ?", (enquiry_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def select_car_other(self, brand):
        # Находим записи с совпадением brand и model в столбцах brand и model
        self.cursor.execute("SELECT * FROM other_cars WHERE brand = ?", (brand,))

        rows = self.cursor.fetchall()

        # Ищем точное совпадение между year и years
        logins_list = []
        for row in rows:
            if row[1] == brand:  # row[3] соответствует столбцу years в таблице cars
                # Получаем список логинов, если логины есть
                logins = row[3] if row[3] else None  # row[4] соответствует столбцу logins
                if logins:
                    logins_list.extend(logins.split(', '))
        print(logins_list, 'ls')
        # Если список логинов не пуст, вернуть его
        if logins_list:
            return logins_list
        elif len(rows) == 0:
            # Если нет совпадений по brand и model, отправить сообщение пользователю и вернуть 3
            user_id = 6061725297
            message = f"Нет совпадений для: brand={brand}"

            return [3, user_id, message]
        else:
            # Если нет логинов, вернуть 2
            return [2, 165546465, 'sa']

    def add_car_other_login(self, brand, login):
        # Поиск совпадений для указанного бренда и модели
        self.cursor.execute("SELECT logins FROM other_cars WHERE brand=?", (brand,))
        result = self.cursor.fetchone()

        if result is None:
            # Если не найдено совпадений, добавляем новую запись
            self.cursor.execute("INSERT INTO other_cars (brand, logins) VALUES (?, ?)", (brand, login))
        else:
            # Если найдено совпадение, проверяем, что логин не существует в списке logins
            logins_list = result[0].split(', ') if result[0] else []
            if login not in logins_list:
                logins_list.append(login)
                updated_logins = ', '.join(logins_list)
                self.cursor.execute("UPDATE other_cars SET logins=? WHERE brand=?", (updated_logins, brand,))
        self.conn.commit()

    def select_other_car(self, brand, model):
        # Находим записи с совпадением brand и model в столбцах brand и model
        self.cursor.execute("SELECT * FROM other_cars WHERE brand = ? AND model = ?", (brand, model))

        rows = self.cursor.fetchall()

        # Ищем точное совпадение между year и years
        logins_list = []
        for row in rows:
            if row[2] == model:  # row[3] соответствует столбцу years в таблице cars
                # Получаем список логинов, если логины есть
                logins = row[3] if row[3] else None  # row[4] соответствует столбцу logins
                if logins:
                    logins_list.extend(logins.split(', '))

        # Если список логинов не пуст, вернуть его
        if logins_list:
            return logins_list
        elif len(rows) == 0:
            # Если нет совпадений по brand и model, отправить сообщение пользователю и вернуть 3
            user_id = 6061725297
            message = f"Нет совпадений для: brand={brand}, model={model}"

            return [3, user_id, message]
        else:
            # Если нет логинов, вернуть 2
            return [2, 165546465, 'sa']

    def add_other_car_login(self, brand, model, login):
        # Поиск совпадений для указанного бренда и модели
        self.cursor.execute("SELECT logins FROM other_cars WHERE brand=? AND model=? ", (brand, model))
        result = self.cursor.fetchone()

        if result is None:
            # Если не найдено совпадений, добавляем новую запись
            self.cursor.execute("INSERT INTO other_cars (brand, model, logins) VALUES (?, ?, ?)", (brand, model, login))
        else:
            # Если найдено совпадение, проверяем, что логин не существует в списке logins
            logins_list = result[0].split(', ') if result[0] else []
            if login not in logins_list:
                logins_list.append(login)
                updated_logins = ', '.join(logins_list)
                self.cursor.execute("UPDATE other_cars SET logins=? WHERE brand=? AND model=?",
                                    (updated_logins, brand, model))
        self.conn.commit()

    def update_stat(self, record_id, new_status):
        try:
            # SQL-запрос для обновления статуса записи
            update_query = "UPDATE enquiries SET status = ? WHERE id = ?"
            self.cursor.execute(update_query, (new_status, record_id))

            # Подтверждение изменений
            self.conn.commit()
            return True  # Успешно обновлено
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False  # Произошла ошибка

    def get_stat(self, record_id):
        try:
            # SQL-запрос для получения статуса записи по ID
            query = "SELECT status FROM enquiries WHERE id = ?"
            self.cursor.execute(query, (record_id,))
            status = self.cursor.fetchone()

            if status:
                return status[0]  # Возвращаем статус, если запись существует
            else:
                return None  # Запись не найдена
        except sqlite3.Error as e:
            print(f"Ошибка при получении статуса записи: {e}")
            return None  # Произошла ошибка

    def get_models_list(self, id_list):

        # Формируем параметры для SQL-запроса
        params = tuple(id_list)

        # Выполняем SQL-запрос для выборки строк по id
        self.cursor.execute("SELECT * FROM cars WHERE id IN ({})".format(','.join(['?'] * len(id_list))), params)

        res = self.cursor.fetchall()

        self.conn.commit()
        resu = list()
        # Вывод результатов
        if res:
            for row in res:
                row = row[1:-1]
                r = list(row)
                r = ', '.join(str(item) for item in r)
                resu.append(r)
            return resu
        else:

            return None

    def get_logins(self, id_list):

        # Формируем параметры для SQL-запроса
        params = tuple(id_list)

        # Выполняем SQL-запрос для выборки строк по id
        self.cursor.execute("SELECT * FROM cars WHERE id IN ({})".format(','.join(['?'] * len(id_list))), params)

        res = self.cursor.fetchall()

        self.conn.commit()

        # Вывод результатов
        if res:
            for row in res:
                row = row[4:]
                r = list(row)
                r = ', '.join(str(item) for item in r)

            return r
        else:

            return None

    def get_id_list(self, login):
        # Выполнение SQL-запроса для поиска строк с заданным логином
        self.cursor.execute("SELECT id FROM cars WHERE INSTR(logins, ?) > 0", (login,))

        # Извлечение результатов запроса
        res = self.cursor.fetchall()

        # Закрытие соединения с базой данных
        self.conn.commit()

        # Вывод списка id строк, где логин найден
        if res:
            id_list = [row[0] for row in res]

            return id_list
        else:
            return None

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()
