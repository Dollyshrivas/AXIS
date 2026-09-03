import time
import os
from google import genai
from google.genai import types

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=15000
    )
)

print("Starting request...")
start = time.time()

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello in one sentence."
    )

    print("Response:", response.text)

except Exception as e:
    print("ERROR:", type(e).__name__)
    print(e)

finally:
    print("Total time:", round(time.time() - start, 2), "seconds")