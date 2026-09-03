from google import genai
import os
import json

from tools import get_time

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Tell Gemini about our Python function
get_time_tool = {
    "type": "function",
    "name": "get_time",
    "description": "Gets the current local time.",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

print("AXIS Tool Calling Test Started...\n")

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="What time is it?",
    tools=[get_time_tool],
)

# Look for a function call
for step in interaction.steps:

    if step.type == "function_call":

        print("Gemini selected tool:")
        print("Tool:", step.name)
        print("Arguments:", step.arguments)

        # Execute our real Python function
        if step.name == "get_time":
            result = get_time()

            print("Python executed get_time()")
            print("Result:", result)

            # Send result back to Gemini
            final_interaction = client.interactions.create(
                model="gemini-3.6-flash",
                previous_interaction_id=interaction.id,
                input=[
                    {
                        "type": "function_result",
                        "name": step.name,
                        "call_id": step.id,
                        "result": [
                            {
                                "type": "text",
                                "text": json.dumps(result),
                            }
                        ],
                    }
                ],
                tools=[get_time_tool],
            )

            print("\nAXIS final response:")
            print(final_interaction.output_text)