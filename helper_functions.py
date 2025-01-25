import os
import json

def load_character_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'prompts/trump.character.json')
    
    with open(json_path, 'r') as file:
        return json.load(file)

def load_chat_history():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(current_dir, 'chat_history.json')
    
    try:
        with open(history_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def update_chat_history(chat_history, user_message=None, character_response=None):
    # If this is a new interaction, create a new interaction number
    interaction_number = len(chat_history) + 1
    
    # If we're starting a new interaction with a user message
    if user_message and not character_response:
        interaction_key = f"interaction_{interaction_number}"
        new_interaction = {
            interaction_key: {
                "user": {"role": "user", "message": user_message},
                "trump": None
            }
        }
        chat_history.append(new_interaction)
    
    # If we're adding Trump's response to an existing interaction
    elif character_response:
        # Get the last interaction number (current one)
        interaction_key = f"interaction_{len(chat_history)}"
        current_interaction = chat_history[-1][interaction_key]
        current_interaction["trump"] = {"role": "Trump", "message": character_response}
    
    return chat_history

def save_chat_history(history):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(current_dir, 'chat_history.json')
    
    with open(history_path, 'w') as file:
        json.dump(history, file, indent=2)
