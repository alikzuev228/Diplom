import tensorflow as tf
import tensorflow_hub as hub
import librosa
import numpy as np

# Завантаження моделі
model = hub.load("https://tfhub.dev/google/yamnet/1")

# Завантаження аудіо
file = r"C:\Unik\Diplom\Diplom\Server\udp\audio_pcm\audio.wav"
y, sr = librosa.load(file, sr=16000)

# Прогін через модель
scores, embeddings, spectrogram = model(y)

scores_np = scores.numpy()

# Класи
class_map_path = model.class_map_path().numpy().decode()
class_names = [line.strip().split(',')[2] for line in open(class_map_path)]

# Аналіз
for i, frame_scores in enumerate(scores_np):
    top_class = np.argmax(frame_scores)
    confidence = frame_scores[top_class]

    if confidence > 0.5:
        print(f"{i}: {class_names[top_class]} ({confidence:.2f})")