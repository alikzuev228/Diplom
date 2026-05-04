import asyncio

# Класс протокола, обрабатывающий события UDP
class UDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        print("UDP сервер запущен и готов к приему данных")

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Получено: {message} от {addr}")
        
        # Эхо-ответ: отправляем данные обратно
        #print(f"Отправка обратно: {message}")
        #self.transport.sendto(data, addr)

async def main():
    loop = asyncio.get_running_loop()
    
    # Создаем UDP endpoint
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(),
        local_addr=('0.0.0.0', 9000)
    )

    try:
        await asyncio.sleep(3600)  # Сервер работает 1 час
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
