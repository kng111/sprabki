import sqlite3
import datetime
def replace_variables(text, replacements):
    for variable, value in replacements.items():
        text = text.replace(f'{{{variable}}}', value)
    return text

# Ваш шаблон справки
template = """
Ш Государственное бюджетное
профессиональное образовательное учреждение Московской области
«Физико-технический колледж»

{date} г.
№ {nomer} с
г. Долгопрудный Московской обл.
пл. Собина, д.1
т. (495) 369-45-93
СПРАВКА

Подтверждает, что {fio}
является студентом {kurs}курса очного {bydzet/vnebydzet} отделения
по основной образовательной программе  
{group}
Приказ о зачислении {nomerPrikaz} от {PriazakDate}
Срок обучения в колледже c 01/09/{godExc} по {konecOBch}
Нормативный срок обучения {srokObychen}
Обучается по программе подготовки Специалистов среднего звена
Справка дана для предоставления по месту требования

Зам. директора                                         О.В.Винокуров
"""

# Подключаемся к базе данных
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Пользователь вводит значение namespec
search_value = input("Введите значение namespec для поиска: ")

# Ищем записи с указанным значением в поле namespec
cursor.execute("SELECT * FROM proff WHERE namespec=?", (search_value,))
row = cursor.fetchone()
today = datetime.date.today().strftime("%d.%m.%Y")
# Если найдена запись
if row:
    replacements = {
        'date': today,
        'nomer': row[0],  # Предполагаем, что shifr находится в первом столбце
        'fio': 'Vlad',  # Предполагаем, что ФИО находится во втором столбце
        'kurs': '2',  # Это вы можете заменить на нужное значение
        'bydzet/vnebydzet': 'бюджетного',  # Это вы можете заменить на нужное значение
        'group': f"{row[0]} {row[1]}",  # Это вы можете заменить на нужное значение
        'nomerPrikaz': '456',  # Это вы можете заменить на нужное значение
        'PriazakDate': '25.08.2023',  # Это вы можете заменить на нужное значение
        'godExc': '2023',  # Это вы можете заменить на нужное значение
        'konecOBch': '30/06/2025',  # Это вы можете заменить на нужное значение
        'srokObychen': row[3]  # Это вы можете заменить на нужное значение
    }

    # Вызываем функцию для замены переменных
    result = replace_variables(template, replacements)

    # Печатаем результат
    print(result)
else:
    print(f"Записей с namespec={search_value} не найдено")

# Закрываем соединение с базой данных
conn.close()
