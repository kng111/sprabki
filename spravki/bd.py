import sqlite3

# Подключение к базе данных (если базы данных не существует, она будет автоматически создана)
conn = sqlite3.connect('spravki.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# Создание таблицы справок, если она еще не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS spravki (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    login TEXT,
    fio TEXT, 
    groups TEXT,
    request_number TEXT,
    status TEXT,
    submission_time Text
);

''')

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()
