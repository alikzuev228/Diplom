import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def process_audio(file_path):
    # 1. Завантаження аудіофайлу
    # sr=None зберігає оригінальну частоту дискретизації
    y, sr = librosa.load(file_path, sr=None)
    
    print(f"Файл завантажено: {file_path}")
    print(f"Частота дискретизації: {sr} Гц")
    print(f"Тривалість: {librosa.get_duration(y=y, sr=sr):.2f} секунд")

    # 2. Обробка: Нормалізація амплітуди (щоб пік був на рівні 1.0)
    y_normalized = librosa.util.normalize(y)

    # 3. Візуалізація
    plt.figure(figsize=(12, 6))

    # Малюємо оригінальну хвилю
    plt.subplot(2, 1, 1)
    librosa.display.waveshow(y, sr=sr, color='blue')
    plt.title('Оригінальна хвильова форма')
    plt.xlabel('Час (сек)')
    plt.ylabel('Амплітуда')

    # Малюємо спектрограму (візуалізація частот)
    plt.subplot(2, 1, 2)
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Спектрограма (Частотний спектр)')

    plt.tight_layout()
    plt.show()

    return y_normalized, sr

file_path = "C:\\Unik\\Diplom\\Diplom\\Server\\udp\\audio_pcm\\audio_192.168.18.48_54551_1773846960.wav"
# Виклик функції (вкажіть шлях до свого файлу)
process_audio(file_path)