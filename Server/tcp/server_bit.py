import asyncio
import wave
import struct
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 9000
SAMPLE_RATE = 2000
DURATION = 10  # секунд на один файл
AUDIO_DIR = r"C:\Unik\Diplom\Diplom\Server\tcp\audio_wav"
os.makedirs(AUDIO_DIR, exist_ok=True)

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"Сервер запущено на {HOST}:{PORT}")
    async with server:
        await server.serve_forever()

def convert_to_pcm16(raw_value):
    """Конвертує 0-1023 у 16-біт PCM (-32768 до 32767)"""
    return int((raw_value / 1023.0) * 65535 - 32768)

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Підключено: {addr}")

    buffer = []
    samples_per_file = SAMPLE_RATE * DURATION

    while True:
        data = await reader.read(1024)
        if not data:
            break

        # Збираємо сирі значення у buffer
        for i in range(0, len(data), 2):
            if i+1 >= len(data):
                break
            raw_value = data[i] + (data[i+1] << 8)
            pcm16 = convert_to_pcm16(raw_value)
            buffer.append(pcm16)
            #print(f"Прийнято: {buffer}")
            print(f"len(buffer) = {len(buffer)} / {samples_per_file}")

            # Якщо накопичили достатньо для одного файлу
            if len(buffer) >= samples_per_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(AUDIO_DIR, f"{timestamp}.wav")
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(struct.pack('<' + 'h'*len(buffer), *buffer))
                print(f"Збережено файл: {filename}")
                buffer.clear()  # очищаємо буфер для наступного файлу

    # Зберегти залишок, якщо він є
    if buffer:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(AUDIO_DIR, f"{timestamp}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(struct.pack('<' + 'h'*len(buffer), *buffer))
        print(f"Збережено залишок: {filename}")

    writer.close()
    await writer.wait_closed()
    print(f"Відключено: {addr}")

asyncio.run(main())
