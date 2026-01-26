from flask import Flask, request
import telebot
import threading
import os
import time


# Дані Telegram-бота
BOT_TOKEN = "8379068830:AAHWSxusQMhEIIOgXWUhlPWxitAqfRFATfQ"       # Токен 
users = set()        # Змінна для зберігання користувачів

#file_users = open("C:\\Diplom\\Data\\users.txt", "w")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === Flask-сервер для прийому повідомлень від ESP8266 ===
@app.route('/', methods=['POST'])
def receive_message():
    msg = request.form.get('message', '')
    if msg:
# Зчитуємо файл з користувачами
        with open("C:\\Diplom\\Data\\users.txt", "r") as file:
            user_id = [line.strip() for line in file]

        print(f"Отримано: {msg}")
        for user in user_id: 
            bot.send_message(user, f"{msg}")
    return "OK", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привіт, я сповіщеня для Дипломного проекту!")
    users.add(message.chat.id)

# Зчитуємо файл з користувачами, та записуємо нових якщо є
    with open("C:\\Diplom\\Data\\users.txt", "r") as file:
        user_id = [line.strip() for line in file]

        if str(message.chat.id) not in user_id:
            print(f"Додано користувача: {message.chat.id}")
            file_users = open("C:\\Diplom\\Data\\users.txt", "a")
            file_users.write(f"{message.chat.id}\n") # додаємо в кінець списку нового користувачаі
            file_users.close()

# === Запуск Flask і Telegram бота паралельно ===
def run_flask():
    app.run(host='0.0.0.0', port=5000)

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    time.sleep(1)  # дати час ініціалізації, для стабільності
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    print("Flask + Telegram бот запущені!")
    while True:
        time.sleep(10)

