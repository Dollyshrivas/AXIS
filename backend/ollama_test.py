from ollama_ai import ask_ollama

print("AXIS Local AI Test\n")

answer = ask_ollama("What is artificial intelligence? Explain in 2 short sentences.")

print("AXIS:", answer)