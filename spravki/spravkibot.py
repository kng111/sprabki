import telebot
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot('6342840039:AAF_FMrFwGXcTRHCV0oiOZzaVfz3-CLMYns')

user_states = {}

def get_user_group(user_login):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT groups FROM spravki WHERE login=?', (user_login,))
    user_group = cursor.fetchone()
    conn.close()
    return user_group[0] if user_group else None

def get_max_request_number():
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(request_number) FROM spravki')
    max_number = cursor.fetchone()[0]
    conn.close()
    return str(max_number) if max_number else "0"

def get_request_status(request_number):
    conn = sqlite3.connect('spravki.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM spravki WHERE request_number=?', (request_number,))
    status = cursor.fetchone()
    conn.close()
    return status[0] if status else None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'waiting_for_fio'}
    bot.reply_to(message, "\U0001F47E: Отлично! Теперь отправь своё ФИО.")

@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'waiting_for_request_number'}
    bot.reply_to(message, "Введите номер заявки для проверки статуса.")

@bot.message_handler(func=lambda message: message.text.lower() == '/help')
def send_help(message):
    bot.reply_to(message, "\U0001F47E: Этот бот предназначен для получения справок. Вот как им пользоваться:\n\n"
                        "/start - начать процесс получения справки\n"
                        "/status <номер_заявки> - проверить статус заявки\n"
                        "/help - получить справку о доступных командах\n\n"
                        "Для получения справки сначала используйте /start.")

@bot.message_handler(func=lambda message: True)
def receive_statement(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {})

    if 'state' not in user_state:
        bot.reply_to(message, "Не правильная команда. Напишите сначала /start")
        return

    if user_state['state'] == 'waiting_for_fio':
        user_state['fio'] = message.text
        user_login = message.from_user.username

        user_group = get_user_group(user_login)

        if user_group:
            user_state['group'] = user_group
            max_request_number = int(get_max_request_number())
            user_state['request_number'] = str(max_request_number + 1)
            user_state['state'] = 'waiting_for_statement'
            bot.reply_to(message, f"Отлично! Ваша группа: {user_group}. Теперь отправь текст справки.")
        else:
            user_state['state'] = 'waiting_for_group'
            bot.reply_to(message, "Отлично! Теперь отправьте номер своей группы. [ИСП 4-1]")
        return

    if user_state['state'] == 'waiting_for_group':
        user_state['group'] = message.text
        user_state['state'] = 'waiting_for_statement'
        max_request_number = int(get_max_request_number())
        user_state['request_number'] = str(max_request_number + 1)
        bot.reply_to(message, f"Хорошо! Теперь отправь текст справки.")
        return

    if user_state['state'] == 'waiting_for_statement':
        user_login = message.from_user.username

        if user_login is None:
            bot.reply_to(message, "У вас не указан username в настройках Telegram. Пожалуйста, установите его, чтобы мы могли вас идентифицировать.")
            return

        statement = message.text
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('spravki.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO spravki (text, login, fio, groups, request_number, status, submission_time) VALUES (?, ?, ?, ?, ?, ?, ?)', (statement, user_login, user_state['fio'], user_state['group'], user_state['request_number'], 'В ожидании', current_time))
        conn.commit()

        conn.close()

        bot.reply_to(message, f"Спасибо за справку! Мы ее получили и рассмотрим в ближайшее время. Номер вашей заявки: {user_state['request_number']}\n Что бы проверить статус вашей заявки напишите /status")

        user_states[user_id] = {}
        bot.send_message(user_id, "Для отправки новой справки нажмите /start")
        return

    if user_state['state'] == 'waiting_for_request_number':
        request_number = message.text
        status = get_request_status(request_number)
        if status is not None:
            bot.reply_to(message, f"Статус заявки №{request_number}: {status}")
        else:
            bot.reply_to(message, f"Заявка с номером №{request_number} не найдена.")



if __name__ == "__main__":
    try:
        print("Бот запущен...")
        bot.infinity_polling()
    
    except Exception as e:
        
        print(f"Ошибка: {e}")
