import telebot
import sqlite3

# Инициализация бота
bot = telebot.TeleBot('6609385582:AAHUy3ysMcw2-Egu6Ri3NC1_sVrK4by9hwg')

# Функция для получения всех заявок в ожидании из базы данных
def get_pending_requests():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spravki WHERE status=?', ('В ожидании',))
    requests = cursor.fetchall()
    conn.close()
    return requests

def get_specific_request(request_number):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spravki WHERE request_number=?', (request_number,))
    specific_request = cursor.fetchone()
    conn.close()
    return specific_request

def get_oldest_spravka():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spravki ORDER BY submission_time ASC LIMIT 1')
    oldest_spravka = cursor.fetchone()
    conn.close()
    return oldest_spravka

# Функция для получения количества заявок в ожидании
def get_pending_requests_count():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM spravki WHERE status=?', ('В ожидании',))
    pending_requests_count = cursor.fetchone()[0]
    conn.close()
    return pending_requests_count

# Функция для обновления статуса заявки
def update_request_status(request_number):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE spravki SET status=? WHERE request_number=?', ('Справка готова', request_number))
    conn.commit()
    conn.close()

# Функция для получения всех готовых справок
def get_ready_spravki():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spravki WHERE status=?', ('Справка готова',))
    ready_spravki = cursor.fetchall()
    conn.close()
    return ready_spravki

def update_spravka_status(request_number, new_status):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE spravki SET status=? WHERE request_number=?', (new_status, request_number))
    conn.commit()
    conn.close()

def delete_spravka(request_number):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spravki WHERE request_number=?', (request_number,))
    conn.commit()
    conn.close()

def delete_all_spravki():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spravki')
    conn.commit()
    conn.close()

# Список команд с описаниями
commands = [
    {'command': '/start', 'description': 'Начать процесс получения справки'},
    {'command': '/nomer <номер_заявки>', 'description': 'Проверить и изменить статус заявки'},
    {'command': '/total', 'description': 'Показать общее количество справок (в ожидании)'},
    {'command': '/spravki', 'description': 'Показать справки в ожидании'},
    {'command': '/nomerall <номер_заявки>', 'description': 'Посмотреть конкретную заявку'},
    {'command': '/r_spravki', 'description': 'Показать готовые справки'},
    {'command': '/nomer_nr <номер_заявки>', 'description': 'Переделать готовую справку в ожидание'},
    {'command': '/nomer_d <номер_заявки>', 'description': 'Удалить справку'},
    {'command': '/nomer_d_all', 'description': 'Удалить все справки'},
    {'command': '/long', 'description': 'Показать самую старую справку'},
    {'command': '/', 'description': 'Показать все доступные команды'}
]

# Функция для вывода списка всех команд
def list_all_commands(message):
    commands_text = "\n".join([f"{cmd['command']} - {cmd['description']}" for cmd in commands])
    bot.reply_to(message, f"Доступные команды:\n{commands_text}")

# Обработчик команды /
@bot.message_handler(commands=[''])
def list_commands(message):
    list_all_commands(message)

# Обработчик команды /spravki
@bot.message_handler(commands=['spravki'])
def send_pending_requests(message):
    # Получаем все заявки в ожидании
    pending_requests = get_pending_requests()

    # Если есть заявки в ожидании, отправляем их пользователю
    if pending_requests:
        for request in pending_requests:
            request_id, text, login, fio, groups, request_number, status, submission_time = request
            response_message = f"Номер заявки: {request_number}\nТекст справки: {text}\nСтатус: {status}\nФИО: {fio}\nГруппа: {groups}\nДата подачи: {submission_time}\n"
            bot.reply_to(message, response_message)
    else:
        bot.reply_to(message, "Нет заявок в ожидании")

# Обработчик команды /status
@bot.message_handler(commands=['status'])
def check_request_status(message):
    try:
        request_number = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите номер заявки после команды /status")
        return

    specific_request = get_specific_request(request_number)

    if specific_request:
        request_id, text, login, fio, groups, request_number, status, submission_time = specific_request
        response_message = f"Номер заявки: {request_number}\nСтатус: {status}\n"
        bot.reply_to(message, response_message)
    else:
        bot.reply_to(message, f"Заявка с номером {request_number} не найдена.")


if __name__ == "__main__":
    try:
        print("Бот запущен...")
        bot.infinity_polling()
    
    except Exception as e:
        print(f"Ошибка: {e}")

