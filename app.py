from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from mistralai import Mistral
from prompts.instruction_prompts import instruction_prompt
from prompts.game_rules import game_rules
from prompts.hints import hints
from prompts.triggers import triggers
from helper_functions import load_chat_history, save_chat_history, update_chat_history
from utils import model, trump_character, client

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

class Message(BaseModel):
    message: str

def generate_text(message: Message):
    # Load existing chat history
        chat_history = load_chat_history()

        # Add user message to history
        chat_history = update_chat_history(chat_history, user_message=message.message)

        # Format the prompt
        formatted_prompt = instruction_prompt.format(
            hints=hints,
            chat_history=chat_history,
            character=trump_character,
            rules=game_rules,
            triggers=triggers
        )

        # Get Character's response
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": formatted_prompt
                },
                {
                    "role": "user",
                    "content": message.message
                }
            ]
        )
        clean_response = chat_response.choices[0].message.content

        # Add character response to history
        chat_history = update_chat_history(chat_history, character_response=clean_response)

        # Save updated chat history
        save_chat_history(chat_history)

        return {
            "character_response": clean_response,
            "chat_history": chat_history
        }

@app.post("/api/generate-text")
def inference(message: Message, request: Request):
    if request.headers.get("origin") != "https://Mistral-AI-Game-Jam/team13.static.hf.space":
        return 204
    return generate_text(message=message)


@app.get("/chat-history", tags=["History"])
def get_chat_history(request: Request):
    if request.headers.get("origin") != "https://Mistral-AI-Game-Jam/team13.static.hf.space":
        return 204
    else:
        chat_history = load_chat_history()
        return {"chat_history": chat_history}
