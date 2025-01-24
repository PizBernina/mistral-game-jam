from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.get("/chat-history")
async def get_chat_history():
    try:
        chat_history = load_chat_history()
        return {"chat_history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-message")
async def send_message(message: Message):
    try:
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

        # Get Trump's response
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

        trump_response = chat_response.choices[0].message.content

        # Add Trump's response to history
        chat_history = update_chat_history(chat_history, trump_message=trump_response)

        # Save updated chat history
        save_chat_history(chat_history)

        return {
            "trump_response": trump_response,
            "chat_history": chat_history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)