from google import genai
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("AXIS streaming test started...\n")

stream = client.interactions.create(
    model="gemini-3.6-flash",
    input="Explain what an AI assistant is in 3 short sentences.",
    stream=True
)

for event in stream:
    if event.event_type == "step.delta":
        if event.delta.type == "text":
            print(event.delta.text, end="", flush=True)

print("\n\nStreaming finished.")