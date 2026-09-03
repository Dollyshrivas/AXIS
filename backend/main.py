from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from fastapi.responses import StreamingResponse
#from tools import say_hello, get_status
import os
import time

app = FastAPI()

client = genai.Client(
    api_key = os.getenv("GEMINI_API_KEY")
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "AI IngredientVision is running!"}

#@app.get("/tool/hello")
#def tool_hello():
    #return say_hello()

#@app.get("/tool/status")
#def tool_status():
    #return get_status()

@app.get("/hello")
def hello():
    return {"message": "Hello AI IngredientVision!!"}

@app.post("/chat")
def chat(request: ChatRequest):

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=request.message,
        system_instruction="""
        You are AXIS, an AI device assistant.

        Your job is to help the user with tasks on their devices.

        Rules:
        - Keep normal responses short and clear.
        - Be helpful and conversational.
        - Do not give long explanations unless the user asks.
        """
    )

    return {"reply": response.output_text}

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):

    def generate():
        stream = client.interactions.create(
            model="gemini-3.6-flash",
            input=request.message,
            system_instruction="""
            You are AXIS, an AI device assistant.

            Keep responses short and clear.
            Be helpful and conversational.
            """
            ,
            stream=True
        )

        for event in stream:
            if event.event_type == "step.delta":
                if event.delta.type == "text":
                    yield event.delta.text

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )