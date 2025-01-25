import os
import json
from graph_utils import *
from random import choice

def load_character_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'original_setup/trump.character.json')
    
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_chat_history(game_root):
    history_path = game_root + '/chat_history.json'
    try:
        with open(history_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def update_chat_history(chat_history, user_message=None, trump_message=None):
    # If this is a new interaction, create a new interaction number
    interaction_number = len(chat_history) + 1
    
    # If we're starting a new interaction with a user message
    if user_message and not trump_message:
        interaction_key = f"interaction_{interaction_number}"
        new_interaction = {
            interaction_key: {
                "user": {"role": "user", "message": user_message},
                "trump": None
            }
        }
        chat_history.append(new_interaction)
    
    # If we're adding Trump's response to an existing interaction
    elif trump_message:
        # Get the last interaction number (current one)
        interaction_key = f"interaction_{len(chat_history)}"
        current_interaction = chat_history[-1][interaction_key]
        current_interaction["trump"] = {"role": "Trump", "message": trump_message}
    
    return chat_history

def save_chat_history(history, game_root):
    history_path = os.path.join(game_root, 'chat_history.json')
    
    with open(history_path, 'w') as file:
        json.dump(history, file, indent=2)

def initialize_game():
    world_graph = WorldGraph('original_setup/contexts/world_map.edgelist')
    os.makedirs("games", exist_ok=True)
    game_number = len(os.listdir('games')) + 1
    os.makedirs(f"games/game_{game_number}", exist_ok=True)
    world_graph.save_graph_as_edgelist(f'games/game_{game_number}/world_graph.edgelist')
    return game_number


def generate_round_context(game_number):
    """randomly generates a context and returns all the prompt elements needed"""
    game_dir = f'games/game_{game_number}/'
    contexts_dir = 'original_setup/contexts/'

    #generate idea
    with open(contexts_dir + 'actions.list', 'r') as ideas:
        idea_list = ideas.readlines()
        #### TODO
        
        idea = idea_list[0].replace('[country]', 'Europe')
        
    concern = "How will it impact jobs in America"
    try:
        with open(game_dir + 'events.list', 'r') as f:
            events = f.read()
    except FileNotFoundError:
        events = ''

    return idea, concern, events

def check_end(trump_response):
    """checks if its the end of the sequence returns a tuple (is_ending:bool, idea_is_accepted:bool/Nonetype)"""
    if "I HAD SUCH A GREAT IDEA LET'S DO IT" in trump_response:
        return True, True
    if "I DECIDED IT WAS A BAD IDEA" in trump_resonse:
        return True, False
    return False, None