import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

print("Available voices:")

for i, voice in enumerate(voices):
    print(i, voice.name, voice.id)

# Try Microsoft Zira
for voice in voices:
    if "Zira" in voice.name:
        engine.setProperty("voice", voice.id)
        print("Using:", voice.name)
        break

print("Testing speech...")

engine.say("Hello boss. Voice testing is working.")
engine.runAndWait()

print("Speech test finished.")