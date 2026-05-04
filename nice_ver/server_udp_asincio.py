# UDP сервер прийому PCM-аудіо та збереження у .pcm / .wav
import asyncio
import time
import os
import sys
import subprocess


# НАЛАШТУВАННЯ
HOST = "0.0.0.0"
PORT = 9000

SAMPLE_RATE = 16000          # 16 kHz
BYTES_PER_SAMPLE = 2        # 16 bit
BYTES_PER_SEC = SAMPLE_RATE * BYTES_PER_SAMPLE
CHUNK_5S = BYTES_PER_SEC * 5

# Отримуємо абсолютний шлях до директорії скрипта
current_dir = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = f"{current_dir}\\audio"
os.makedirs(AUDIO_DIR, exist_ok=True)


# UDP ПРОТОКОЛ
class AudioUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        # Буфер окремо для кожного клієнта
        self.buffers = {}

    def datagram_received(self, data, addr):

# Викликається для КОЖНОГО UDP пакета

        client_id = f"{addr[0]}_{addr[1]}"

        if client_id not in self.buffers:
            self.buffers[client_id] = bytearray()
            print(f"New client: {client_id}")

        buffer = self.buffers[client_id]
        buffer.extend(data)

        #print(f"{client_id}: received {len(data)} bytes")

# Коли буфер заповнюється - записуємо файл
        while len(buffer) >= CHUNK_5S:
            ts = int(time.time())
            pcm_path = f"{AUDIO_DIR}\\audio_{client_id}_{ts}.pcm"
            wav_path = f"{AUDIO_DIR}\\audio_{client_id}_{ts}.wav"

            with open(pcm_path, "wb") as f:
                f.write(buffer[:CHUNK_5S])

# Очищуємо буфер
            del buffer[:CHUNK_5S]

            print(f"Saved {pcm_path}")

# Конвертація в WAV
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "s16le",
                "-ar", str(SAMPLE_RATE),
                "-ac", "1",
                "-i", pcm_path,
                wav_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.system(f"del {pcm_path}")
            
            print(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))
            print(f" Converted to {wav_path}\n")

# ЗАПУСК ДЕТЕКЦІЇ ПОДІЙ
#process = subprocess.Popen([sys.executable, f'{current_dir}\\rms_det_file.py'])

# ЗАПУСК UDP СЕРВЕРА
async def main():
    
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: AudioUDPProtocol(),
        local_addr=(HOST, PORT)
    )

    print(f"UDP Audio Server listening on {HOST}:{PORT}")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        transport.close()

asyncio.run(main())

