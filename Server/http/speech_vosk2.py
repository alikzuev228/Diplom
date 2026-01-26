from vosk import Model, KaldiRecognizer
import json, pyaudio, wave

MODEL_PATH = r"D:\Diplom\vosk-uk"
SAMPLE_RATE = 16000

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

# Розпізнавання голосу з мікрофона
def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']

# Розпізнавання з файлу
def listen_file(filename):
    wf = wave.open(filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != SAMPLE_RATE:
        print("Аудіофайл має бути mono PCM 16-bit 16kHz")
        return

    rec_file = KaldiRecognizer(model, SAMPLE_RATE)
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec_file.AcceptWaveform(data):
            answer = json.loads(rec_file.Result())
            if answer['text']:
                yield answer['text']

for text in listen_file(r"D:\Diplom\audio\audio_ua.wav"):
    print(text)


