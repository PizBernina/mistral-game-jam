import os
import json
from dotenv import load_dotenv
from mistralai import Mistral
from prompts.instruction_prompts import instruction_prompt
from prompts.game_rules import game_rules
from prompts.triggers import triggers
load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

def load_character_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'prompts/trump.character.json')
    
    with open(json_path, 'r') as file:
        return json.load(file)

trump_character = load_character_data()


client = Mistral(api_key=api_key)

def load_chat_history():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(current_dir, 'chat_history.json')
    
    try:
        with open(history_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_chat_history(history):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(current_dir, 'chat_history.json')
    
    with open(history_path, 'w') as file:
        json.dump(history, file, indent=2)

# Load existing chat history
chat_history = load_chat_history()

# Get user message from your existing code
user_message = "meow meow meow" 

# Add user message to history
chat_history.append({
    "role": "user",
    "message": user_message
})

# Whole Prompt
formatted_prompt = instruction_prompt.format(
    chat_history=chat_history,
    character=trump_character,
    rules=game_rules,
    triggers=triggers
)

chat_response = client.chat.complete(
    model=model,
    messages=[
        {
            "role": "system",
            "content": formatted_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
)

# Get Trump's response
trump_response = chat_response.choices[0].message.content

# Add Trump's response to history
chat_history.append({
    "role": "Trump",
    "message": trump_response
})

# Save updated chat history
save_chat_history(chat_history)

# Print response
print(trump_response)