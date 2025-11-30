from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json

MODEL_PATH = r"C:\python\vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

def callback(indata, frames, time, status):
    if status:
        print("Audio error:", status)

    # КОНВЕРТАЦІЯ В BYTES (найважливіша частина!)
    data = indata.tobytes()

    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        text = json.loads(result).get("text", "")
        if text.strip():
            print("→", text)
    else:
        partial = recognizer.PartialResult()
        # Якщо треба — можна розкоментувати
        # print("...", json.loads(partial).get("partial", ""))

print("Говори... (Ctrl+C щоб зупинити)")
with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=8000,
    dtype='int16',
    channels=1,
    callback=callback):

    while True:
        pass
