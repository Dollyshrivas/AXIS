import sounddevice as sd
import numpy as np
import speech_recognition as sr

recognizer = sr.Recognizer()

SAMPLE_RATE = 16000
DURATION = 5

print("🎤 AXIS is listening for 5 seconds...")

audio_data = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
)

sd.wait()

print("🧠 Processing...")

audio = sr.AudioData(
    audio_data.tobytes(),
    SAMPLE_RATE,
    2
)

try:
    text = recognizer.recognize_google(audio)
    print("You:", text)

except sr.UnknownValueError:
    print("AXIS could not understand you.")

except sr.RequestError as e:
    print("Speech recognition service error:", e)