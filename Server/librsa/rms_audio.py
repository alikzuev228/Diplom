import librosa
import numpy as np
import matplotlib.pyplot as plt
import os


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
                print(f"Подія зафіксована: {start_time:.2f} сек (RMS: {rms[i]:.5f})")
                detected_events.append(start_time)
                is_event_active = True
        else:
            is_event_active = False

    if not detected_events:
        print("Гучних подій не виявлено.")

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

# Шлях до файлу
file_path = r"C:\Unik\Diplom\Diplom\Server\udp\audio_pcm\audio_192.168.18.35_1234_1775806272.wav"
# Запуск: sensitivity_coeff можна змінювати (чим вище, тим менше чутливість)
analyze_audio_events(file_path, sensitivity_coeff=1.1)