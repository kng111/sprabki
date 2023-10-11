import telebot
import sqlite3

# Инициализация бота
bot = telebot.TeleBot('6609385582:AAHUy3ysMcw2-Egu6Ri3NC1_sVrK4by9hwg')


def is_admin(user_id):
    # Здесь может быть ваш код для проверки администратора
    return user_id == 6635880006 # Замените 6635880006 на ID вашего администратора

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

@bot.message_handler(commands=['start'])
def send_help(message):
    user_login = message.from_user.username
    bot.reply_to(message, f"\n\U0001F47E: Здравствуйте, {user_login}, напишите /help или /spravki для начала работы")

    if user_login is None:
            bot.reply_to(message, "\U0001F47E:Здравствуйте, напишите /help или /spravki для начала работы")
            return

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

# Обработчик команды /nomer
@bot.message_handler(commands=['nomer'])
def set_request_ready(message):
    # Парсим номер из сообщения
    try:
        request_number = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите номер заявки после команды /nomer")
        return

    # Обновляем статус заявки
    update_request_status(request_number)
    bot.reply_to(message, f"Статус заявки №{request_number} успешно обновлен. Справка готова!")


@bot.message_handler(commands=['nomerall'])
def view_specific_request(message):
    try:
        request_number = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите номер заявки после команды /nomerall")
        return

    specific_request = get_specific_request(request_number)

    if specific_request:
        request_id, text, login, fio, groups, request_number, status, submission_time = specific_request
        response_message = f"Полная заявка\nНомер заявки: {request_number}\n\nТекст справки: {text}\n\n\nСтатус: {status}\n\nФИО: {fio}\n\nГруппа: {groups}\n\nДата подачи: {submission_time}\n\nЛогин в телеграмме: {login}\n "
        bot.reply_to(message, response_message)
    else:
        bot.reply_to(message, f"Заявка с номером {request_number} не найдена.")

@bot.message_handler(commands=['r_spravki'])
def send_ready_spravki(message):
    # Получаем все готовые справки
    ready_spravki = get_ready_spravki()

    # Если есть готовые справки, отправляем их пользователю
    if ready_spravki:
        for spravka in ready_spravki:
            spravka_id, text, login, fio, groups, request_number, status, submission_time = spravka
            response_message = f"Номер заявки: {request_number}\n\nТекст справки: {text}\n\nСтатус: {status}\n\nФИО: {fio}\n\nГруппа: {groups}\n\nДата подачи: {submission_time}\n"
            bot.reply_to(message, response_message)
    else:
        bot.reply_to(message, "Нет готовых справок")

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

@bot.message_handler(commands=['nomer_nr'])
def set_spravka_pending(message):
    # Парсим номер из сообщения
    try:
        request_number = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите номер заявки после команды /nomer_nr\n/nomer_nr [пробел] [номер заявки]")
        return

    # Обновляем статус справки
    update_spravka_status(request_number, 'В ожидании')
    bot.reply_to(message, f"Статус справки №{request_number} успешно обновлен. Справка в ожидании!")


def delete_spravka(request_number):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spravki WHERE request_number=?', (request_number,))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['nomer_d'])
def delete_spravka_command(message):
    # Проверяем, является ли пользователь администратором
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    # Парсим номер из сообщения
    try:
        request_number = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите номер заявки после команды /nomer_d")
        return

    # Удаляем справку из базы данных
    delete_spravka(request_number)
    bot.reply_to(message, f"Справка №{request_number} успешно удалена.")

    # Удаляем справку из базы данных
    delete_spravka(request_number)
    bot.reply_to(message, f"Справка №{request_number} успешно удалена.")


def delete_all_spravki():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spravki')
    conn.commit()
    conn.close()

# Обработчик команды /nomer_d_all
@bot.message_handler(commands=['nomer_d_all'])
def delete_all_spravki_command(message):
    # Проверяем, является ли пользователь администратором
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    # Удаляем все справки из базы данных
    delete_all_spravki()
    bot.reply_to(message, "Все справки успешно удалены.")

@bot.message_handler(commands=['long'])
def send_oldest_spravka(message):
    oldest_spravka = get_oldest_spravka()

    if oldest_spravka:
        request_id, text, login, fio, groups, request_number, status, submission_time = oldest_spravka
        response_message = f"Номер заявки: {request_number}\n\nТекст справки: {text}\n\nСтатус: {status}\n\nФИО: {fio}\n\nГруппа: {groups}\n\nДата подачи: {submission_time}\n"
        bot.reply_to(message, response_message)
    else:
        bot.reply_to(message, "Нет доступных справок.")



# Обработчик команды /total
@bot.message_handler(commands=['total'])
def send_total_requests(message):
    total_requests_count = len(get_pending_requests())
    pending_requests_count = get_pending_requests_count()

    bot.reply_to(message, f"Всего заявок: {total_requests_count}\n Cправок в ожидании: {pending_requests_count}")

@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    bot.reply_to(message, """Доступные команды:
/start - Начать процесс получения справки
/nomer <номер_заявки> - Проверить и изменить статус заявки
/total - Показать общее количество справок (в ожидании)
/spravki - Показать справки в ожидании
/nomerall <номер_заявки> - Посмотреть конкретную заявку
/r_spravki - Показать готовые справки
/nomer_nr <номер_заявки> - Переделать готовую справку в ожидание
/nomer_d <номер_заявки> - Удалить справку
/nomer_d_all - Удалить все справки
/long - Показать самую старую справку
/help - Показать все доступные команды""")

# Обработчик для команд, начинающихся с /
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.reply_to(message, "Неизвестная команда. Напишите /help для получения справки.\n")

# Обработчик команды /help


# Запуск бота
if __name__ == "__main__":
    try:
        print("Бот запущен...")
        bot.infinity_polling()
    
    except Exception as e:
        print(f"Ошибка: {e}")
