import os
import json
from graph_utils import *
from random import choice

def load_character_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'original_setup/trump.character.json')
    
    with open(json_path, 'r') as file:
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
    with open(contexts_dir + 'actions.list', 'r') as file:
        idea_csq = file.readlines()
        idea_csq = choice(idea_csq)
        idea, delta_USA, delta_country, delta_friendliness = idea_csq.split(';')
        delta_friendliness = delta_friendliness.split()[0]
    with open(contexts_dir + 'countries.list', 'r') as f_countries:
        countries = f_countries.readlines()
        country = choice(countries).split()[0]

    idea = idea.replace('[country]', country)

    with open(contexts_dir + 'concerns.list', 'r') as f:
        concerns = f.readlines()
        concern = choice(concerns)

    with open(contexts_dir + '2nd_characters.list', 'r') as f:
        advisors = f.readlines()
        advisor = choice(advisors)

    consequences = {
        'country': country,
        'delta_USA': delta_USA,
        'delta_country': delta_country,
        'delta_friendliness': delta_friendliness
    }
    try:
        with open(game_dir + 'events.list', 'r') as f:
            events = f.read()
    except FileNotFoundError:
        events = ''

    return idea, concern, advisor, events, consequences

def check_end(trump_response):
    """checks if its the end of the sequence returns a tuple (is_ending:bool, idea_is_accepted:bool/Nonetype)"""
    if "I HAD SUCH A GREAT IDEA LET'S DO IT" in trump_response:
        return True, True
    if "I DECIDED IT WAS A BAD IDEA" in trump_response:
        return True, False
    return False, None


def process_ending(idea_is_accepted, game_number, idea):
    if idea_is_accepted:
        with open(f'games/game_{game_number}/events.list', 'a') as f:
            f.write(idea + '\n')

        world_graph = WorldGraph(f'games/game_{game_number}/world_graph.edgelist')

        with open(f'games/game_{game_number}/round_consequences.json', 'r') as f:
            consequences = json.load(f)
            country = consequences['country'] 
            delta_USA = int(consequences['delta_USA'])
            delta_country = int(consequences['delta_country'])
            delta_friendliness = int(consequences['delta_friendliness']) 
        
        GDP = world_graph.update_world(country, delta_USA, delta_country, delta_friendliness, game_number)

        return GDP