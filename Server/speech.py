import speech_recognition

recognition = speech_recognition.Recognizer()
mic = speech_recognition.Microphone()

print(mic)

with mic as audio:
    print ("Speech:")
    recognition.adjust_for_ambient_noise(audio)
    audio = recognition.listen(audio)
    text = recognition.recognize_google(audio, language="ru-RU")
    print(text)