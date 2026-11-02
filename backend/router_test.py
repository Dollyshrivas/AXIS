from ai_router import ask_ai

print("================================")
print("       AXIS AI ROUTER TEST")
print("================================")

question = input("\nYou: ")

answer = ask_ai(question)

print("\n🤖 AXIS:", answer)