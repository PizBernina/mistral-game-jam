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

def save_chat_history(history):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(current_dir, 'chat_history.json')
    
    with open(history_path, 'w') as file:
        json.dump(history, file, indent=2)
