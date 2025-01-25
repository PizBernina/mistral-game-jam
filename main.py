from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from mistralai import Mistral

from original_setup.instruction_prompts import instruction_prompt
from original_setup.game_rules import game_rules
from original_setup.hints import hints
from original_setup.triggers import triggers

from helper_functions import *
from utils import model, trump_character, client

from graph_utils import *

# initialize game
init_game = True
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
    global init_game
    try:
        #If we're ate the beginning of a game
        if init_game:
            game_number = initialize_game()
            init_game = False
        else:
            game_number = len(os.listdir('games/'))

        chat_history = load_chat_history(f'games/game_{game_number}')
        
        return {"chat_history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-message")
async def send_message(message: Message):
    global init_game
    try:
        #If we're ate the beginning of a game
        if init_game:
            game_number = initialize_game()
            init_game = False
        else:
            game_number = len(os.listdir('games/'))

        # Load existing chat history
        chat_history = load_chat_history(f'games/game_{game_number}')
        interaction_number = len(chat_history) + 1
        
        #If we're at the beginning of a round
        if interaction_number == 1:
            idea, concern, events = generate_round_context(game_number)
            round_context = {
                    "idea": idea,
                    "concern": concern,
                    "events": events
                }
            with open(f'games/game_{game_number}/round_context.json', 'w') as f:
                json.dump(round_context, f, indent=4)
        else:
            file_path = f'games/game_{game_number}/round_context.json'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    round_context = json.load(f)
                    idea = round_context.get("idea")
                    concern = round_context.get("concern")
                    events = round_context.get("events")
            else:
                raise FileNotFoundError(f"Round context file not found: {file_path}")

        # Add user message to history

        chat_history = update_chat_history(chat_history, user_message=message.message)
        # Format the prompt
        formatted_prompt = instruction_prompt.format(
            hints=hints,
            chat_history=chat_history,
            character=trump_character,
            rules=game_rules,
            triggers=triggers,
            events=events,
            idea=idea,
            concern=concern
        )

        # Get Trump's response
        #### TO STREAM : USE ASYNC VERSION
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
        print(chat_history)
        # Save updated chat history
        save_chat_history(chat_history, f'games/game_{game_number}')

        return {
            "trump_response": trump_response,
            "chat_history": chat_history
        }
    except Exception as e:
        print(e)
        raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)