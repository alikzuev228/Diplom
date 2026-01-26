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

class AudioBuffer:
    def __init__(self):
        self.buf = bytearray()

    def push(self, data: bytes):
        self.buf.extend(data)

    def has_chunk(self):
        return len(self.buf) >= CHUNK_20S

    def pop_chunk(self):
        chunk = self.buf[:CHUNK_20S]
        self.buf = self.buf[CHUNK_20S:]
        return chunk

audio = AudioBuffer()

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"🔌 Connected: {addr}")

    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break

            audio.push(data)

            while audio.has_chunk():
                ts = int(time.time())
                fname = f"{AUDIO_DIR}/audio_{ts}.pcm"
                with open(fname, "wb") as f:
                    f.write(audio.pop_chunk())
                print(f"💾 Saved {fname}")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        writer.close()
        await writer.wait_closed()
        print(f"🔌 Disconnected: {addr}")

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"🚀 TCP Audio Server on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
