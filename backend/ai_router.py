import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from ollama_ai import ask_ollama
from google import genai


# ========================================
# GEMINI SETUP
# ========================================

api_key = os.getenv("GEMINI_API_KEY")

if api_key:

    client = genai.Client(
        api_key=api_key
    )

else:

    client = None

    print("⚠️ GEMINI_API_KEY not found.")


# ========================================
# AXIS PERSONALITY
# ========================================

AXIS_INSTRUCTIONS = """
You are AXIS, a friendly AI device assistant.

Personality:
- Friendly
- Natural
- Helpful
- Conversational
- Not overly formal

Response rules:
 - Keep normal spoken answers to one brief sentence of 8 words or fewer, unless the user asks for detail.
- Do not use markdown unless necessary.
- Do not use bullet points for simple questions.
- Give natural spoken responses because your answer will be read aloud.

Language:
- Understand English, Hindi and Hinglish.
- Reply in the same language/style used by the user.
- Write Hindi words in Devanagari so the voice uses Hindi pronunciation; English words may stay in Latin script.
- If the user speaks Hindi, reply naturally in Hindi using Devanagari; avoid Romanized Hindi and Hinglish.
- If the user speaks English, reply in English.
- If the user uses Hinglish, reply naturally in Hinglish.

Important:
- Do not pretend you performed a device action unless it was actually performed.
- If a device action is not available, clearly say that it is not available.
"""


# ========================================
# GEMINI
# ========================================

def ask_gemini(prompt):

    print("☁️ Gemini is being used...")

    if client is None:

        print("❌ Gemini client is not configured.")

        return None

    try:

        response = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
            system_instruction=AXIS_INSTRUCTIONS
        )

        answer = response.output_text

        if answer:

            answer = answer.strip()

        print("☁️ Gemini response:", repr(answer))

        return answer

    except Exception as e:

        print("❌ Gemini error:", repr(e))

        return None


# ========================================
# OLLAMA
# ========================================

def ask_ollama_with_personality(prompt):

    full_prompt = f"""
{AXIS_INSTRUCTIONS}

User:
{prompt}

AXIS:
"""

    try:

        response = ask_ollama(full_prompt)

        if response is None:

            print("⚠️ Ollama returned None.")

            return None

        response = str(response).strip()

        if not response:

            print("⚠️ Ollama returned empty response.")

            return None

        return response

    except Exception as e:

        print("❌ Ollama error:", repr(e))

        return None


# ========================================
# AXIS AI ROUTER
# ========================================

def ask_ai(prompt):

    print("\n================================")
    print("🧠 AXIS AI ROUTER")
    print("================================")


    # ====================================
    # OLLAMA FIRST
    # ====================================

    print("🥇 Asking Ollama...")

    try:

        answer = ask_ollama_with_personality(prompt)

        if answer:

            print("✅ Ollama responded.")

            return answer

        print("⚠️ Ollama returned no usable response.")

    except Exception as e:

        print("⚠️ Ollama failed:", repr(e))


    # ====================================
    # GEMINI FALLBACK
    # ====================================

    print("🥈 Falling back to Gemini...")

    answer = ask_gemini(prompt)

    if answer:

        print("✅ Gemini responded.")

        return answer


    # ====================================
    # BOTH FAILED
    # ====================================

    print("❌ Both Ollama and Gemini failed.")

    return (
        "Sorry, I cannot connect to my AI right now."
    )