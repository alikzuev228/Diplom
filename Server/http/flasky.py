from flask import Flask, request
import threading
import time


app = Flask(__name__)

# === Flask-сервер для прийому повідомлень від ESP8266 ===
@app.route('/', methods=['POST'])
def receive_message():
    msg = request.form.get('message', '')
    if msg:
        print(f"Отримано: {msg}")
    return "OK", 200

# === Запуск Flask і Telegram бота паралельно ===
def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    time.sleep(1)  # дати час ініціалізації, для стабільності
    threading.Thread(target=run_flask, daemon=True).start()
    print("Flask запущено!")
    while True:
        time.sleep(10)

