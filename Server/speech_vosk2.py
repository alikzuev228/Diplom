from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json, pyaudio

MODEL_PATH = r"C:\python\vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']

for text in listen():
    print(text)

