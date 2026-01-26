import asyncio
import time
import os

HOST = "0.0.0.0"
PORT = 9000

SAMPLE_RATE = 16000
BYTES_PER_SEC = SAMPLE_RATE * 2
CHUNK_20S = BYTES_PER_SEC * 20

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    client_id = f"{addr[0]}_{addr[1]}"
    print(f"Connected: {client_id}")

    buffer = bytearray()

    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break

            buffer.extend(data)

            while len(buffer) >= CHUNK_20S:
                ts = int(time.time())
                fname = f"{AUDIO_DIR}/audio_{client_id}_{ts}.pcm"

                with open(fname, "wb") as f:
                    f.write(buffer[:CHUNK_20S])

                buffer = buffer[CHUNK_20S:]
                print(f"Saved {fname}")

    except Exception as e:
        print(f"{client_id} error:", e)

    finally:
        writer.close()
        await writer.wait_closed()
        print(f"🔌 Disconnected: {client_id}")

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"Multi-client TCP Audio Server on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
