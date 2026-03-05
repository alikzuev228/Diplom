import asyncio
import time
import numpy as np


# ==============================
# НАЛАШТУВАННЯ АУДІО
# ==============================

SAMPLE_RATE = 16000          # Частота дискретизації (16 кГц)
BYTES_PER_SAMPLE = 2         # 16-bit PCM = 2 байти
WINDOW_MS = 200              # Аналіз кожні 200 мс

# Розмір одного вікна в байтах
WINDOW_SIZE = int(SAMPLE_RATE * BYTES_PER_SAMPLE * WINDOW_MS / 1000)

# ==============================
# НАЛАШТУВАННЯ АЛГОРИТМУ
# ==============================

CALIBRATION_TIME = 60        # 60 секунд навчання (калібрування)
THRESHOLD_MULTIPLIER = 3.0   # Поріг = baseline × 3
CONFIRM_WINDOWS = 3          # Скільки гучних вікон підряд потрібно
ADAPT_RATE = 0.001           # Наскільки швидко оновлюється baseline


class AudioUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        # Буфер сирих байтів для кожного клієнта
        self.buffers = {}

        # Середній фоновий RMS (baseline)
        self.baseline = {}

        # Історія RMS під час калібрування
        self.rms_history = {}

        # Лічильник гучних вікон підряд
        self.confirm_counts = {}

        # Час підключення клієнта (для 60с калібрування)
        self.start_time = {}

    def datagram_received(self, data, addr):
        """
        Викликається при отриманні КОЖНОГО UDP пакета.
        data — сирі байти PCM
        addr — (ip, port)
        """

        client_ip = addr[0]  # Ідентифікуємо клієнта по IP

        # Якщо клієнт новий — створюємо структури даних
        if client_ip not in self.buffers:
            self.buffers[client_ip] = bytearray()
            self.baseline[client_ip] = None
            self.rms_history[client_ip] = []
            self.confirm_counts[client_ip] = 0
            self.start_time[client_ip] = time.time()

            print(f"New client connected: {client_ip}")

        # Додаємо нові дані в буфер клієнта
        buffer = self.buffers[client_ip]
        buffer.extend(data)

        # ==============================
        # ОБРОБКА ПО 200 мс
        # ==============================

        while len(buffer) >= WINDOW_SIZE:

            # Вирізаємо 200 мс аудіо
            chunk = buffer[:WINDOW_SIZE]

            # Видаляємо ці байти з буфера
            del buffer[:WINDOW_SIZE]

            # Перетворюємо сирі байти в numpy масив int16
            audio = np.frombuffer(chunk, dtype=np.int16)

            # Обчислюємо RMS (енергія сигналу)
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))

            # Скільки часу клієнт вже працює
            elapsed = time.time() - self.start_time[client_ip]

            # ==========================================
            # ЕТАП 1 — КАЛІБРУВАННЯ (перші 60 секунд)
            # ==========================================
            if elapsed < CALIBRATION_TIME:

                # Запам’ятовуємо RMS для обчислення середнього
                self.rms_history[client_ip].append(rms)

                print(f"[{client_ip}] Calibrating... RMS={int(rms)}")

                # Переходимо до наступного вікна
                continue

            # ==========================================
            # ЕТАП 2 — ВСТАНОВЛЕННЯ БАЗОВОГО РІВНЯ
            # ==========================================
            if self.baseline[client_ip] is None:

                # Обчислюємо середній RMS за 60 секунд
                self.baseline[client_ip] = np.mean(self.rms_history[client_ip])

                print(f"[{client_ip}] Baseline установлен: {int(self.baseline[client_ip])}")

            baseline = self.baseline[client_ip]

            # Поріг детекції
            threshold = baseline * THRESHOLD_MULTIPLIER

            # ==========================================
            # ПОВІЛЬНА АДАПТАЦІЯ ФОНУ
            # ==========================================
            # Якщо шум середовища зміниться (телевізор, вентиляція),
            # baseline буде повільно підлаштовуватись

            self.baseline[client_ip] = (
                (1 - ADAPT_RATE) * baseline + ADAPT_RATE * rms
            )

            # ==========================================
            # ЕТАП 3 — ДЕТЕКЦІЯ ПОДІЇ
            # ==========================================

            if rms > threshold:
                # Гучне вікно
                self.confirm_counts[client_ip] += 1

                print(
                    f"[{client_ip}] Loud detected | "
                    f"RMS={int(rms)} | Threshold={int(threshold)}"
                )
            else:
                # Якщо вікно тихе — обнуляємо лічильник
                self.confirm_counts[client_ip] = 0

            # Якщо 3 гучних вікна підряд (≈600 мс)
            if self.confirm_counts[client_ip] >= CONFIRM_WINDOWS:

                print(f"🚨 ALERT! Loud sound detected from {client_ip}")

                # Обнуляємо лічильник щоб уникнути спаму
                self.confirm_counts[client_ip] = 0
