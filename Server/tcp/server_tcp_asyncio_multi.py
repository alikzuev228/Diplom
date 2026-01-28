import asyncio
import time
import os

# ==============================
# НАЛАШТУВАННЯ СЕРВЕРА
# ==============================

HOST = "0.0.0.0"   # Слухаємо всі мережеві інтерфейси
PORT = 9000        # TCP порт для прийому аудіо

# Параметри аудіо
SAMPLE_RATE = 16000          # 16 kHz
BYTES_PER_SEC = SAMPLE_RATE * 2  # 16 bit (2 байти) * 16000
CHUNK_20S = BYTES_PER_SEC * 20   # 20 секунд аудіо (640 000 байт)

# Каталог для збереження аудіофайлів
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ==============================
# ОБРОБНИК ОДНОГО TCP-КЛІЄНТА
# ==============================

async def handle_client(reader, writer):
    """
    Ця функція викликається ОКРЕМО для кожного TCP-клієнта (ESP8266).
    asyncio гарантує, що всі клієнти обробляються паралельно.
    """

    # Отримуємо IP та порт клієнта
    addr = writer.get_extra_info("peername")
    client_id = f"{addr[0]}_{addr[1]}"
    print(f"Connected: {client_id}")

    # Окремий буфер ТІЛЬКИ для цього клієнта
    # Дані з інших ESP сюди ніколи не потраплять
    buffer = bytearray()

    try:
        while True:
            # Читаємо дані з TCP сокету
            # reader.read(4096) — асинхронно чекає байти
            data = await reader.read(4096)

            # Якщо клієнт закрив з'єднання
            if not data:
                break

            # Додаємо отримані байти у буфер
            buffer.extend(data)

            # Поки в буфері є ≥ 20 секунд аудіо
            while len(buffer) >= CHUNK_20S:
                # UNIX-час для унікальної назви файлу
                ts = int(time.time())

                # Ім'я файлу містить ID клієнта
                fname = f"{AUDIO_DIR}/audio_{client_id}_{ts}.pcm"

                # Записуємо рівно 20 секунд PCM
                with open(fname, "wb") as f:
                    f.write(buffer[:CHUNK_20S])

                # Видаляємо записану частину з буфера
                buffer = buffer[CHUNK_20S:]

                print(f"Saved {fname}")

    except Exception as e:
        # Якщо сталася помилка (обрив, криві дані і т.д.)
        print(f"{client_id} error:", e)

    finally:
        # Коректно закриваємо TCP-з’єднання
        writer.close()
        await writer.wait_closed()
        print(f"Disconnected: {client_id}")

# ==============================
# ЗАПУСК TCP-СЕРВЕРА
# ==============================

async def main():
    """
    Створюємо TCP сервер.
    Для кожного підключення автоматично викликається handle_client().
    """
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"Multi-client TCP Audio Server on {HOST}:{PORT}")

    # Сервер працює нескінченно
    async with server:
        await server.serve_forever()

# Точка входу
asyncio.run(main())
