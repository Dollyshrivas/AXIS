import re
import subprocess
import sys
import traceback

import sounddevice as sd
import speech_recognition as sr
import pyttsx3

from ai_router import ask_ai
from tools import (
    say_hello,
    get_status,
    get_time,
    get_location,
    get_battery,
    open_item,
    open_file_explorer,
    search_web,
    open_chrome,
    open_youtube,
    open_whatsapp,
)


# ========================================
# AXIS CONFIGURATION
# ========================================

SAMPLE_RATE = 16000
RECORD_SECONDS = 6

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.8
recognizer.dynamic_energy_threshold = True

current_voice = "female"
engine = None


# ========================================
# WINDOWS VOICE INITIALIZATION
# ========================================

def initialize_voice():
    global engine

    try:
        engine = pyttsx3.init("sapi5")
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")

        print("\nAvailable Windows voices:")
        for voice in voices:
            print(f" - {voice.name}")

        print("Windows voice engine initialized.")
        return True

    except Exception as error:
        print(f"Voice initialization error: {error}")
        traceback.print_exc()
        return False


# ========================================
# VOICE SELECTION
# ========================================

def set_voice(gender):
    global current_voice

    if engine is None:
        print("Voice engine is not initialized.")
        return False

    try:
        voices = engine.getProperty("voices")

        if gender == "female":
            preferred_names = ("zira", "female")
        else:
            preferred_names = ("david", "male")

        for voice in voices:
            if any(name in voice.name.lower()
                   for name in preferred_names):
                engine.setProperty("voice", voice.id)
                current_voice = gender
                print(f"Selected {gender} voice: {voice.name}")
                return True

        print(f"No matching {gender} voice installed.")
        return False

    except Exception as error:
        print(f"Voice selection error: {error}")
        return False


# ========================================
# TEXT TO SPEECH
# ========================================

def speak(text):
    if text is None:
        return

    clean_text = str(text).strip()

    if not clean_text:
        return

    print(f"\nAXIS: {clean_text}")

    tts_script = """
import sys
import pyttsx3

engine = pyttsx3.init("sapi5")
engine.setProperty("rate", 165)
engine.setProperty("volume", 1.0)

engine.say(sys.stdin.read())
engine.runAndWait()
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", tts_script],
            input=clean_text,
            text=True,
            capture_output=True,
            timeout=90
        )

        if result.returncode == 0:
            print("AXIS speech process completed.")
        else:
            print("TTS ERROR:", result.stderr)

    except subprocess.TimeoutExpired:
        print("TTS ERROR: Speech process timed out.")

    except Exception as error:
        print("TTS ERROR:", error)

# ========================================
# MICROPHONE AND GOOGLE SPEECH RECOGNITION
# ========================================

def listen():
    print(f"\n🎤 AXIS is listening for {RECORD_SECONDS} seconds.")
    print("Speak now...")

    try:
        audio_data = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
        )
        sd.wait()

        audio = sr.AudioData(
            audio_data.tobytes(),
            SAMPLE_RATE,
            2,
        )

    except Exception as error:
        print(f"Microphone error: {error}")
        return None

    for language in ("en-IN", "hi-IN"):
        try:
            print(f"Recognizing speech in {language}...")

            text = recognizer.recognize_google(
                audio,
                language=language,
            )

            if text and text.strip():
                text = text.strip()
                print(f"👤 You ({language}): {text}")
                return text

        except sr.UnknownValueError:
            print(f"Speech not understood in {language}.")

        except sr.RequestError as error:
            print(f"Google speech service error: {error}")
            print("Check your internet connection.")
            return None

        except Exception as error:
            print(f"Speech recognition error: {error}")
            return None

    print("AXIS could not understand the recording.")
    return None


# ========================================
# AXIS TOOLS
# ========================================

def run_axis_tool(user_text):
    command = user_text.lower().strip()
    command = re.sub(r"[.!?,]+$", "", command).strip()

    # Greeting / tool test
    if command in ("hello tool", "test tools", "test tool"):
        return say_hello()

    # Open websites and applications
    if command in (
        "open google",
        "launch google",
        "google kholo",
        "गूगल खोलो",
        "गूगल ओपन करो",
    ):
        return open_item("google")

    if command in ("open youtube", "launch youtube", "youtube kholo"):
        return open_youtube()

    if command in ("open whatsapp", "launch whatsapp", "whatsapp kholo"):
        return open_whatsapp()

    if command in ("open chrome", "launch chrome"):
        return open_chrome()

    if command in (
        "open file explorer",
        "open files",
        "launch file explorer",
    ):
        return open_file_explorer()

    # Open a requested website, e.g. "open github.com"
    open_prefixes = ("open ", "launch ", "go to ")
    for prefix in open_prefixes:
        if command.startswith(prefix):
            target = user_text[len(prefix):].strip()
            if target:
                return open_item(target)

    # Web search
    search_prefixes = (
        "search google for ",
        "search for ",
        "google search for ",
        "search ",
    )

    for prefix in search_prefixes:
        if command.startswith(prefix):
            query = user_text[len(prefix):].strip()
            if query:
                return search_web(query)
            return "Tell me what you want me to search for."

    # Google Maps search
    map_prefixes = ("find on maps ", "search maps for ", "maps search ")
    for prefix in map_prefixes:
        if command.startswith(prefix):
            query = user_text[len(prefix):].strip()
            if query:
                return search_web(query, maps=True)
            return "Tell me what location to search for."

    # System information
    if command in ("time", "what time is it", "tell me the time"):
        return f"The current time is {get_time()}."

    if "battery" in command:
        return get_battery()

    if command in (
        "my location",
        "what is my location",
        "what's my location",
        "current location",
        "where am i",
    ):
        return get_location()

    if command in ("axis status", "system status", "check status"):
        return str(get_status())

    # No matching local tool: send to AI.
    return None


# ========================================
# AXIS AI
# ========================================

def ask_axis(text):
    print("\n🧠 AXIS is processing...")
    print(f"User: {text}")

    try:
        response = ask_ai(text)

        if response is None or not str(response).strip():
            print("AI returned an empty response.")
            return "Sorry, I could not get a response."

        response = str(response).strip()
        print(f"AI response: {response}")
        return response

    except Exception as error:
        print(f"AXIS AI error: {error}")
        traceback.print_exc()
        return "Sorry, I am having trouble processing that request."


# ========================================
# MAIN LOOP
# ========================================

def main():
    print("=" * 42)
    print("       AXIS VOICE ASSISTANT")
    print("=" * 42)

    if not initialize_voice():
        print("AXIS could not start its voice engine.")
        return
    

    # Default voice
    if not set_voice("female"):
        print("Using the default Windows voice.")

    # Initial greeting
    speak("Hello boss. How can I help you?")

    print("\nAXIS is ready.")
    print("Try: Open Google, search for Python, check battery.")
    print("Say 'switch to male voice' or 'switch to female voice'.")
    print("Say 'exit' to stop.")

    try:
        while True:
            user_text = listen()

            if user_text is None:
                continue

            command = user_text.lower().strip()
            command = re.sub(r"[.!?,]+$", "", command).strip()

            # Switch voices
            if any(phrase in command for phrase in (
                "switch to male",
                "use male",
                "male voice",
            )):
                if set_voice("male"):
                    speak("Okay, I will use the male voice.")
                continue

            if any(phrase in command for phrase in (
                "switch to female",
                "use female",
                "female voice",
            )):
                if set_voice("female"):
                    speak("Okay, I will use the female voice.")
                continue

            # Exit
            if command in ("exit", "quit", "stop", "goodbye"):
                speak("Okay, have a nice day.")
                break

            # Run tools before asking the AI.
            try:
                tool_response = run_axis_tool(user_text)

                if tool_response is not None:
                    print(f"🛠️ Tool result: {tool_response}")
                    speak(tool_response)
                    continue

            except Exception as error:
                print(f"Tool execution error: {error}")
                traceback.print_exc()
                speak("Sorry, I could not complete that command.")
                continue

            # Normal conversation goes to the AI.
            response = ask_axis(user_text)
            speak(response)

    except KeyboardInterrupt:
        print("\nAXIS stopped by keyboard.")

    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass

        print("AXIS has stopped.")


if __name__ == "__main__":
    main()
