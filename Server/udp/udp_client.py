import socket
import time
import os

# НАЛАШТУВАННЯ (вказати IP вашого роутера або сервера)
SERVER_IP = "192.168.18.38" # Вкажіть IP, на якому слухає сервер
PORT = 9000
FILE_TO_SEND = "input_audio.pcm"  # Файл, який хочете відправити
CHUNK_SIZE = 1024                 # Розмір одного UDP пакету

def send_audio():
    # Створюємо UDP сокет
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = input()
    sock.sendto(data, (SERVER_IP, PORT))
    print("Відправку завершено.")
    sock.close()
"""    
    if not os.path.exists(FILE_TO_SEND):
        print(f"Файл {FILE_TO_SEND} не знайдено!")
        return

    print(f"Починаю відправку файлу {FILE_TO_SEND} на {SERVER_IP}:{PORT}...")

    with open(FILE_TO_SEND, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            
            # Відправляємо чанк даних
            sock.sendto(data, (SERVER_IP, PORT))
            
            # Невелика пауза, щоб не перевантажити буфер роутера/NAT
            # Для 16kHz 16bit моно (32кб/сек) пауза має бути приблизно такою:
            time.sleep(0.02) 
"""    


if __name__ == "__main__":
    send_audio()