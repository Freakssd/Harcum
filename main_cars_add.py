import json
import requests
import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('cars.db')
cursor = conn.cursor()

# https://jsonviewer.stack.hu/
f_id: str = input('firm id:')
url_list = [
    f'https://www.drom.ru/api/sales/model-list/by-firm-id?getTop=5&cityId=0&regionId=0&distance=0&uhash'
    f'=e33f4e6ca98df6e863a180ef410a81b4&dealerId=0&marketId=0&firmId={f_id}&mileageCondition=0']

firm = input("firm name:")
popular_cars_id_lst = list()
top_mod = f'{firm}\n'
for url in url_list:
    response = requests.get(url)
    # Проверяем статус-код ответа
    if response.status_code == 200:
        # Выводим текст ответа
        json_data = response.text
        data_dict = json.loads(json_data)
        # Проверяем наличие ключей 'top' и 'regular' в 'data'

        if 'top' in data_dict['data']:

            print("Top models:")

            for item in data_dict['data']['top']:
                print(item['id'], item['name'])
                top_mod += f"{item['name']}\n"
                popular_cars_id_lst.append(item['id'])
                m_id = item['id']
                m_name = item['name']

                response2 = requests.get(f"https://www.drom.ru/api/sales/generation-list/by-model-id?modelId={m_id}")

                if response2.status_code == 200:
                    # Выводим текст ответа
                    json_data2 = response2.text
                    data_dict2 = json.loads(json_data2)

                    for generation in data_dict2['data']['generations']:
                        # Получаем доступ к ключу 'items' внутри текущего элемента 'generation'
                        items = generation['items']
                        # Итерируемся по каждому элементу списка 'items'
                        for it in items:
                            c = list()

                            m_yearStart = it['yearStart']
                            m_yearEnd = it['yearEnd']
                            m_frames = it['frames']

                            if it['yearEnd'] is None:
                                m_yearEnd = 2024

                            if len(m_frames) != 0:

                                m_frames = m_frames[0]

                            else:

                                m_frames = ''

                            m_gen = f"{m_yearStart}-{m_yearEnd} {m_frames}"
                            c.append(m_id)
                            c.append(firm)
                            c.append(m_name)
                            c.append(m_gen)

                            print(c)
                            # SQL-запрос для вставки данных
                            sql = '''INSERT INTO Cars_list (firm_id_drom, firm, model, gen)
                                      VALUES (?, ?, ?, ?)'''

                            # Выполняем запрос с данными из списка
                            cursor.execute(sql, c)

                            # Сохраняем изменения
                            conn.commit()

        if 'regular' in data_dict['data']:

            print("\nRegular models:")

            for itemss in data_dict['data']['regular']:

                m_id = itemss['id']
                m_name = itemss['name']

                if m_id in popular_cars_id_lst:
                    print(f"skip {m_id}")
                    continue

                response2 = requests.get(f"https://www.drom.ru/api/sales/generation-list/by-model-id?modelId={m_id}")

                if response2.status_code == 200:
                    # Выводим текст ответа
                    json_data2 = response2.text
                    data_dict2 = json.loads(json_data2)

                    for generation in data_dict2['data']['generations']:
                        # Получаем доступ к ключу 'items' внутри текущего элемента 'generation'
                        items = generation['items']
                        # Итерируемся по каждому элементу списка 'items'
                        for it in items:
                            c = list()

                            m_yearStart = it['yearStart']
                            m_yearEnd = it['yearEnd']
                            m_frames = it['frames']

                            if it['yearEnd'] is None:
                                m_yearEnd = 2024

                            if len(m_frames) != 0:

                                m_frames = m_frames[0]

                            else:

                                m_frames = ''

                            m_gen = f"{m_yearStart}-{m_yearEnd} {m_frames}"
                            c.append(m_id)
                            c.append(firm)
                            c.append(m_name)
                            c.append(m_gen)

                            print(c)
                            # SQL-запрос для вставки данных
                            sql = '''INSERT INTO Cars_list (firm_id_drom, firm, model, gen)
                                              VALUES (?, ?, ?, ?)'''

                            # Выполняем запрос с данными из списка
                            cursor.execute(sql, c)

                            # Сохраняем изменения
                            conn.commit()

                else:
                    print("Error200")
        else:
            print("Error1")

    else:
        print("Ошибка при получении данных. Статус код:", response.status_code)

# Закрываем соединение с базой данных
conn.close()
print(top_mod)
