import sqlite3


class CarsDB:

    def __init__(self):
        """open bd connection"""
        self.conn = sqlite3.connect('cars.db')
        self.cursor = self.conn.cursor()

    # Достаем все марки авто и убираем повторы
    def firms(self):
        self.cursor.execute("SELECT firm FROM cars_list")
        firms = [row[0] for row in self.cursor.fetchall()]

        unique_list_firms = []
        seen = set()

        for item in firms:
            if item not in seen:
                unique_list_firms.append(item)
                seen.add(item)

        return unique_list_firms

    # Достаем все модели по марке авто и убираем повторы
    def models_by_firm(self, firm):
        self.cursor.execute("SELECT model FROM cars_list WHERE firm = ?", (firm,))
        models = [row[0] for row in self.cursor.fetchall()]

        unique_list_models = []
        seen = set()

        for item in models:
            if item not in seen:
                unique_list_models.append(item)
                seen.add(item)

        return unique_list_models

    # Достаем все поколения по модели и по марке авто и убираем повторы

    def years_by_model_and_firm(self, firm, model):
        self.cursor.execute("SELECT gen FROM cars_list WHERE firm = ? AND model = ?", (firm, model))
        gens = [row[0] for row in self.cursor.fetchall()]
        print(gens)
        return gens

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()
