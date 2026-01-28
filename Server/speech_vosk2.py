from vosk import Model, KaldiRecognizer
import json, pyaudio, wave, os, time
MODEL_PATH = r"C:\Diplom\vosk-model-small-ru-0.22"
SAMPLE_RATE = 16000

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

# Логування
ts = int(time.time())
with open(f"C:\\Унік\\Диплом\\Diplom\\Log\\log_{ts}.txt", "w") as log:
    log.write("Start Prorgram...\n===============================")

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
        print("Аудіофайл має бути mono .wav 16-bit 16kHz")
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


while(True):

    dir_file = input("Введіть шлях до файлу: ")
# Відокремлення типу файлу
    type = dir_file[-3:]
    print(type)

# Перетворення формату на потрібний для VOSK
    if type == 'pcm':
        os.system(f'ffmpeg -y -f s16le -ar 16000 -ac 1 -i "{dir_file}" -b:a 128k "C:\\Diplom\\ffmpeg_output\\output.wav"')
    else:
        os.system(f'ffmpeg -y -i "{dir_file}" -ar 16000 -ac 1 -c:a pcm_s16le "C:\\Diplom\\ffmpeg_output\\output.wav"')

    for text in listen_file(r"C:\Diplom\ffmpeg_output\output.wav"):
        with open(f"C:\\Унік\\Диплом\\Diplom\\Log\\log_{ts}.txt", "a") as log:
            log.write('\n')
            log.write(text)
        print(text)









