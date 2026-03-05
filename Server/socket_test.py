import socket

# Создание TCP/IP сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Привязка сокета к адресу и порту
server_address = ('0.0.0.0', 65432)
server_socket.bind(server_address)

# Вывод локального адреса (адрес вашего ПК)
local_address = server_socket.getsockname()
print(f"Локальный адрес: {local_address[0]}:{local_address[1]}")

# Ожидание подключений
server_socket.listen(1)
print("Сервер запущен, ожидает подключения...")

while True:
    connection, client_address = server_socket.accept()
    try:
        print(f"Подключено: {client_address}")
        while True:
            data = connection.recv(1024)
            if data:
                print(f"Получено: {data.decode('cp866')}")
                connection.sendall(data) # Эхо-ответ

                with open("test.txt", "a") as file:
                    file.write(data.decode('cp866'))
            else:
                break
    finally:
        connection.close()
