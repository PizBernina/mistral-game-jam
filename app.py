from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

game_over_rich = False
game_over_bankrupt = False

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.get("/chat-history", tags=['History'])
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

@app.post("/api/generate-text")
async def send_message(message: Message):
    global init_game
    global game_over_rich
    global game_over_bankrupt
    try:
        #If we're ate the beginning of a game
        if init_game:
            game_number = initialize_game()
            init_game = False
        else:
            game_number = len(os.listdir('games/'))

        # Load existing chat history
        chat_history = load_chat_history(f'games/game_{game_number}')

        #If we're at the beginning of a round
        if message.message == "":
            idea, concern, advisor_full, events, consequences = generate_round_context(game_number)
            round_context = {
                    "idea": idea,
                    "concern": concern,
                    'advisor': advisor_full,
                    "events": events
                }

            with open(f'games/game_{game_number}/round_context.json', 'w') as f:
                json.dump(round_context, f, indent=4)

            with open(f'games/game_{game_number}/round_consequences.json', 'w') as f:
                json.dump(consequences, f, indent=4)
        else:
            file_path = f'games/game_{game_number}/round_context.json'
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    round_context = json.load(f)
                    idea = round_context.get("idea")
                    concern = round_context.get("concern")
                    advisor_full = round_context.get("advisor")
                    events = round_context.get("events")
            else:
                raise FileNotFoundError(f"Round context file not found: {file_path}")

        # Add user message to history

        if message.message != "":
            chat_history = update_chat_history(chat_history, user_message=message.message)
        else:
            chat_history = []
        # Format the prompt
        formatted_prompt = instruction_prompt.format(
            hints=hints,
            chat_history=chat_history, #useless, don't worry
            character=trump_character,
            rules=game_rules,
            triggers=triggers,
            advisor=advisor_full,
            events=events,
            idea=idea,
            concern=concern,
        )
        # Get Trump's response
        #### TO STREAM : USE ASYNC VERSION

        system = [{"role": "system", "content": formatted_prompt}]
        dynamic_history = []
        role_mapping = {
                "user": "user",
                "trump": "assistant"  # Mapping 'trump' to 'assistant'
            }
        for interaction in chat_history:
            for key, value in interaction.items():
                user_message = value['user']['message'] if 'user' in value else "..."
                trump_message = value['trump']['message'] if value['trump'] else None

                dynamic_history.append({
                "role": role_mapping["user"],
                "content": user_message
            })

            # Append Trump's message, mapped to 'assistant'
            if trump_message:
                dynamic_history.append({
                    "role": role_mapping["trump"],
                    "content": trump_message
                })

        messages = system + dynamic_history

        chat_response = client.chat.complete(
            model=model,
            messages=messages
        )

        trump_response = chat_response.choices[0].message.content

        # Add Trump's response to history
        chat_history = update_chat_history(chat_history, trump_message=trump_response)
        # Save updated chat history
        save_chat_history(chat_history, f'games/game_{game_number}')

        is_ending, idea_is_accepted = check_end(trump_response)

        if is_ending:
            process_ending(idea_is_accepted, game_number, idea)
            
            world_graph = WorldGraph(f'games/game_{game_number}/world_graph.edgelist')
            dico_world = world_graph.push_data_to_front()

        return {
            "character_response": trump_response,
            "chat_history": chat_history,
            "chat_ended": is_ending,
            "idea": idea,
            "idea_is_accepted": idea_is_accepted,
        }
    except Exception as e:
        print(e)
        raise e
        raise HTTPException(status_code=500, detail=str(e))

# Add this before the final static files mount
app.mount("/images", StaticFiles(directory="static/images"), name="images")

# Keep this as the last mount
app.mount("/", StaticFiles(directory="static", html=True), name="static")
