# Програма аналізу аудіо та детекції подій
import time
import os
import librosa
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import numpy as np
import matplotlib.pyplot as plt
import telebot

# Папка з аудіо для аналізу
FOLDER_TO_WATCH = r"C:\Unik\Diplom\Diplom\Server\udp\audio_pcm"

# Дані Telegram-бота
BOT_TOKEN = "8379068830:AAHWSxusQMhEIIOgXWUhlPWxitAqfRFATfQ" # Токен 
bot = telebot.TeleBot(BOT_TOKEN)

def analyze_audio_events(path, frame_length=2048, hop_length=512, sensitivity_coeff=2.5):
    if not os.path.exists(path):
        print(f"Помилка: Файл не знайдено")
        return

# 1. Завантаження (sr=None зберігає оригінальну частоту)
    y, sr = librosa.load(path, sr=None)
    
# 2. Розрахунок RMS (гучності) для кожного вікна
# frame_length — розмір вікна, hop_length — крок (зсув) вікна
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    
# Масив часу для кожного вікна RMS
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

# 3. Оцінка фонового шуму (Baseline)
# Використовуємо медіану або середнє значення всього запису як базу
    baseline_noise = np.median(rms) 
    
# 5. Визначення порогового значення (Baseline * коефіцієнт)
    threshold = baseline_noise * sensitivity_coeff

    print(f"--- Аналіз завершено ---")
    print(f"Базовий рівень шуму (RMS): {baseline_noise:.5f}")
    print(f"Порогове значення (Коеф {sensitivity_coeff}): {threshold:.5f}")
    print(f"------------------------\n")

# 7 & 8. Виявлення перевищення порогу та вивід часу
    detected_events = []
    is_event_active = False

    print("Виявлені події (час у секундах):")
    for i in range(len(rms)):
        if rms[i] > threshold:
            if not is_event_active:
# Початок нової події
                start_time = times[i]
# Фіксація події та відправка повідомлення через API TG
                print(f"Подія зафіксована: {time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())} сек (RMS: {rms[i]:.5f})")
                bot.send_message(-4810244717, f"Подія")
                detected_events.append(start_time)
                is_event_active = True

        else:
            is_event_active = False

    if not detected_events:
        print("Гучних подій не виявлено.")
"""
    # Візуалізація результатів
    plt.figure(figsize=(12, 6))
    
    # Графік RMS
    plt.plot(times, rms, label='Поточна гучність (RMS)', color='blue')
    # Лінія порогу
    plt.axhline(y=threshold, color='red', linestyle='--', label=f'Поріг (Baseline * {sensitivity_coeff})')
    # Лінія фонового шуму
    plt.axhline(y=baseline_noise, color='green', linestyle=':', label='Фоновий шум (Baseline)')
    
    plt.title('Аналіз гучних подій на основі RMS та адаптивного порогу')
    plt.xlabel('Час (сек)')
    plt.ylabel('Амплітуда RMS')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
"""

# Запуск:
# analyze_audio_events(file_path, sensitivity_coeff=1.1)

class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
# Перевіряємо, чи це файл і чи має він розширення .wav
        if not event.is_directory and event.src_path.endswith('.wav'):
            print(f"\nНовий файл виявлено: {event.src_path}")
            
# Невелика пауза, щоб система встигла закрити файл після запису
            time.sleep(1) 
            
            try:
# Викликаємо функцію аналізу
                analyze_audio_events(event.src_path, sensitivity_coeff=1.15)
# Видалення файлів                
                os.system(f'del /q "{FOLDER_TO_WATCH}\\*.wav"')
            except Exception as e:
                print(f"Помилка при обробці файлу: {e}")

if __name__ == "__main__":
# Перевірка наявності папки
    if not os.path.exists(FOLDER_TO_WATCH):
        os.makedirs(FOLDER_TO_WATCH)

    event_handler = AudioHandler()
    observer = Observer()
    observer.schedule(event_handler, FOLDER_TO_WATCH, recursive=False)
    
    print(f"Моніторинг папки: {FOLDER_TO_WATCH}")
    print("Очікування нових файлів... (Натисніть Ctrl+C для зупинки)")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()